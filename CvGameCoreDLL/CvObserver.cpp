#include "CvGameCoreDLL.h"
#include "CvObserver.h"
#ifdef CV_OBSERVER_ENABLE
#include "CvGame.h"
#include "CvObserverTransport.h"
#include <stdio.h>
#include <new>

// XANA: 2026-11-04 ObserverMCP - game-thread boundary and lifetime
namespace
{
	// POD globals only: no thread creation or joining during loader-lock callbacks.
	CvGame const* g_owner = NULL; // ONLY the game-thread bridge ever sees this.
	CvObserverTransport* g_transport = NULL;
	DWORD g_gameThread = 0;
	unsigned long g_generation = 0;
	unsigned long g_snapshot = 0;
	char g_session[64];
	int g_lastTurn = 0;
	bool g_haveTurn = false;

	bool readNumber(const char* name, unsigned long fallback,
		unsigned long minimum, unsigned long maximum, unsigned long& result)
	{
		char buffer[32];
		SetLastError(ERROR_SUCCESS);
		DWORD count = GetEnvironmentVariableA(name, buffer, sizeof(buffer));
		result = fallback;
		if (count == 0)
			return GetLastError() == ERROR_ENVVAR_NOT_FOUND;
		if (count >= sizeof(buffer))
			return false;
		unsigned long n = 0;
		for (DWORD i = 0; i < count; ++i)
		{
			if (buffer[i] < '0' || buffer[i] > '9')
				return false;
			unsigned long digit = buffer[i] - '0';
			if (n > maximum / 10 || (n == maximum / 10 && digit > maximum % 10))
				return false;
			n = n * 10 + digit;
		}
		if (n < minimum || n > maximum)
			return false;
		result = n;
		return true;
	}

	void start(CvGame const& game)
	{
		g_owner = &game; // Attempt once per game/reset, including disabled launches.
		g_gameThread = GetCurrentThreadId();
		char enabled[8];
		DWORD count = GetEnvironmentVariableA("CV_OBSERVER_ENABLE", enabled, sizeof(enabled));
		if (count != 1 || enabled[0] != '1')
			return;
		CvObserverTransportConfig config;
		unsigned long port, capacity, retry, timeout;
		if (!readNumber("CV_OBSERVER_PORT", 37631, 1, 65535, port) ||
			!readNumber("CV_OBSERVER_QUEUE", 16, 1, 64, capacity) ||
			!readNumber("CV_OBSERVER_RETRY_MS", 500, 50, 30000, retry) ||
			!readNumber("CV_OBSERVER_TIMEOUT_MS", 500, 50, 5000, timeout))
		{
			OutputDebugStringA("ObserverMCP: invalid configuration; disabled until reset.\n");
			return;
		}
		config.port = static_cast<unsigned short>(port);
		config.queueCapacity = static_cast<unsigned int>(capacity);
		config.retryMs = retry;
		config.ioTimeoutMs = timeout;
		// XANA: 2026-11-05 Observer allocation uses explicit failure returns.
		g_transport = new (std::nothrow) CvObserverTransport(config);
		if (g_transport == NULL)
		{
			FAssertMsg(false, "Observer transport allocation failed");
			OutputDebugStringA("ObserverMCP: allocation failed; disabled until reset.\n");
			return;
		}
		if (!g_transport->start())
		{
			delete g_transport;
			g_transport = NULL;
			OutputDebugStringA("ObserverMCP: transport start failed; disabled until reset.\n");
			return;
		}
		// XANA: 2026-11-05 Observer allocation end.
		FILETIME now;
		GetSystemTimeAsFileTime(&now);
		++g_generation;
		// Correlation token, NOT a security credential or persistent save identity.
		sprintf(g_session, "%08lx%08lx%08lx%08lx", now.dwHighDateTime,
			now.dwLowDateTime, GetCurrentProcessId(), g_generation);
		g_snapshot = 0;
		g_haveTurn = false;
	}
}

void CvObserver::postUpdate(CvGame const& game)
{
	if (g_owner == NULL)
		start(game);
	if (g_owner != &game || g_gameThread != GetCurrentThreadId() || g_transport == NULL)
		return;
	// This is the sole live game read. Extend the VALUE here, never in run().
	int const turn = game.getGameTurn();
	if (g_haveTurn && turn == g_lastTurn)
		return;
	// Exhaustion fails closed instead of wrapping IDs within the session.
	if (g_snapshot == 0xffffffffUL)
		return;
	CvObserverMessage message;
	if (CvObserverFormatSnapshot(g_session, ++g_snapshot, turn, message))
		g_transport->enqueue(message);
	g_lastTurn = turn;
	g_haveTurn = true;
}

void CvObserver::stop(CvGame const& game)
{
	if (g_owner != &game)
		return;
	FAssertMsg(g_gameThread == GetCurrentThreadId(), "Observer shutdown must run on game thread");
	if (g_transport != NULL)
	{
		g_transport->stop(); // Join before queue, locks or game data are destroyed.
		delete g_transport;
		g_transport = NULL;
	}
	g_owner = NULL;
	g_gameThread = 0;
	g_haveTurn = false;
}
// XANA: 2026-11-04 ObserverMCP end
#endif
