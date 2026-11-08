#include "CvGameCoreDLL.h"
#include "CvObserver.h"
#ifdef CV_OBSERVER_ENABLE
#include "CvGame.h"
#include "CvPlayer.h"
#include "CvCity.h"
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
	unsigned long g_sessionSequence = 0;
	unsigned long g_snapshot = 0;
	unsigned long g_capture = 0;
	unsigned long g_worldSequence = 0;
	unsigned long g_mapSeed = 0;
	char g_session[65];
	char g_world[18];
	int g_lastTurn = 0;
	bool g_haveTurn = false;
	bool g_haveWorld = false;
	unsigned long g_pendingWorlds = 0;

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
		if (g_sessionSequence == 0xffffffffUL)
		{
			OutputDebugStringA("ObserverMCP: game-session ID space exhausted; disabled.\n");
			return;
		}
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
		FILETIME now;
		GetSystemTimeAsFileTime(&now);
		++g_sessionSequence;
		// Correlation token, NOT a security credential or persistent save identity.
		sprintf(g_session, "%08lx%08lx%08lx%08lx", now.dwHighDateTime,
			now.dwLowDateTime, GetCurrentProcessId(), g_sessionSequence);
		g_snapshot = 0;
		g_capture = 0;
		g_worldSequence = 0;
		g_haveTurn = false;
		g_haveWorld = false;
		g_pendingWorlds = 0;
	}

	void initializeSnapshot(CvObserverSnapshot& value, int turn)
	{
		value.sessionId = g_session;
		value.sessionSequence = g_sessionSequence;
		value.worldId = g_world;
		value.worldSequence = g_worldSequence;
		value.mapSeed = g_mapSeed;
		value.captureId = g_capture;
		value.gameTurn = turn;
	}

	bool emitSnapshot(CvObserverSnapshot& value)
	{
		// Exhaustion fails closed instead of wrapping IDs within the session.
		if (g_snapshot == 0xffffffffUL)
			return false;
		value.snapshotId = ++g_snapshot;
		CvObserverMessage message;
		if (!CvObserverFormatSnapshot(value, message))
			return false;
		g_transport->enqueue(message);
		return true;
	}

	bool capturePlayers(CvGame const&, int turn)
	{
		int playerCount = 0;
		for (int i = 0; i < MAX_PLAYERS; ++i)
		{
			if (GET_PLAYER((PlayerTypes)i).isAlive())
				++playerCount;
		}
		if (playerCount == 0)
		{
			CvObserverSnapshot value;
			initializeSnapshot(value, turn);
			return emitSnapshot(value);
		}

		int playerIndex = 0;
		for (int i = 0; i < MAX_PLAYERS; ++i)
		{
			CvPlayer const& player = GET_PLAYER((PlayerTypes)i);
			if (!player.isAlive())
				continue;
			int const cityCount = player.getNumCities();
			int partCount = cityCount / CV_OBSERVER_CITY_CHUNK_SIZE;
			if (cityCount % CV_OBSERVER_CITY_CHUNK_SIZE != 0)
				++partCount;
			if (partCount < 1)
				partCount = 1;
			int cityIterator = 0;
			CvCity const* city = player.firstCity(&cityIterator);
			for (int part = 0; part < partCount; ++part)
			{
				CvObserverSnapshot value;
				initializeSnapshot(value, turn);
				value.playerCount = playerCount;
				value.playerIndex = playerIndex;
				value.hasPlayer = true;
				value.player.id = player.getID();
				value.player.teamId = player.getTeam();
				value.player.civilizationType = player.getCivilizationType();
				value.player.leaderType = player.getLeaderType();
				value.player.isHuman = player.isHuman();
				value.player.isBarbarian = player.isBarbarian();
				value.player.cityCount = cityCount;
				value.player.totalPopulation = player.getTotalPopulation();
				value.player.cityOffset = part * CV_OBSERVER_CITY_CHUNK_SIZE;
				value.player.cityPart = part;
				value.player.cityPartCount = partCount;
				while (value.player.citiesInMessage < CV_OBSERVER_CITY_CHUNK_SIZE &&
					city != NULL)
				{
					CvObserverCity& output = value.player.cities[value.player.citiesInMessage];
					output.id = city->getID();
					output.x = city->getX();
					output.y = city->getY();
					output.population = city->getPopulation();
					++value.player.citiesInMessage;
					city = player.nextCity(&cityIterator);
				}
				if (!emitSnapshot(value))
					return false;
			}
			++playerIndex;
		}
		return true;
	}
}

void CvObserver::postUpdate(CvGame const& game)
{
	if (g_owner == NULL)
		start(game);
	if (g_owner != &game || g_gameThread != GetCurrentThreadId() || g_transport == NULL)
		return;
	// All live game reads and iteration stay at this game-thread boundary.
	unsigned long const mapSeed = game.getInitialRandSeed().first;
	bool const newWorld = !g_haveWorld || g_pendingWorlds > 0 || mapSeed != g_mapSeed;
	if (newWorld)
	{
		unsigned long const advance = g_pendingWorlds > 0 ? g_pendingWorlds : 1;
		if (advance > 0xffffffffUL - g_worldSequence)
			return;
		g_mapSeed = mapSeed;
		g_worldSequence += advance;
		sprintf(g_world, "%08lx-%08lx", g_mapSeed, g_worldSequence);
		g_haveWorld = true;
		g_pendingWorlds = 0;
		g_haveTurn = false;
	}
	int const turn = game.getGameTurn();
	if (g_haveTurn && turn == g_lastTurn)
		return;
	if (g_capture == 0xffffffffUL)
		return;
	++g_capture;
	capturePlayers(game, turn);
	g_lastTurn = turn;
	g_haveTurn = true;
}

void CvObserver::mapRegenerated(CvGame const& game)
{
	if (g_owner == &game && g_gameThread == GetCurrentThreadId() &&
		g_pendingWorlds < 0xffffffffUL)
		++g_pendingWorlds;
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
	g_haveWorld = false;
	g_pendingWorlds = 0;
}
// XANA: 2026-11-08 ObserverMCP hierarchical capture end
#endif
