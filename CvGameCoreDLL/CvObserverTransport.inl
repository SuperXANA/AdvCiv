#include "CvObserverConfig.h"
#ifdef CV_OBSERVER_ENABLE
// XANA: 20261104 ObserverMCP transport prototype (ChatGPT).
#include "CvObserverTransport.h"
#include <process.h>

#pragma comment(lib, "ws2_32.lib")

CvObserverTransportConfig::CvObserverTransportConfig()
: port(37631), queueCapacity(16), retryMs(500), ioTimeoutMs(500)
{
}

CvObserverTransport::CvObserverTransport(const CvObserverTransportConfig& config)
: m_config(config), m_queue(config.queueCapacity), m_stopEvent(NULL),
  m_thread(NULL), m_started(false), m_stopped(false),
  m_winsockStarted(false), m_lastError(0)
{
}

CvObserverTransport::~CvObserverTransport()
{
	stop();
}

bool CvObserverTransport::start()
{
	if (m_started)
		return true;
	if (m_stopped || m_config.port == 0 || m_config.queueCapacity < 1 ||
		m_config.queueCapacity > 64 || m_config.retryMs < 50 ||
		m_config.retryMs > 30000 || m_config.ioTimeoutMs < 50 ||
		m_config.ioTimeoutMs > 5000)
	{
		setError(ERROR_INVALID_PARAMETER);
		return false;
	}
	WSADATA data;
	int error = WSAStartup(MAKEWORD(2, 2), &data);
	if (error != 0)
	{
		setError(error);
		return false;
	}
	m_winsockStarted = true;
	if (LOBYTE(data.wVersion) != 2 || HIBYTE(data.wVersion) != 2)
	{
		setError(WSAVERNOTSUPPORTED);
		WSACleanup();
		m_winsockStarted = false;
		return false;
	}
	m_stopEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
	if (m_stopEvent == NULL)
	{
		setError(GetLastError());
		WSACleanup();
		m_winsockStarted = false;
		return false;
	}
	unsigned int threadId = 0;
	m_thread = reinterpret_cast<HANDLE>(_beginthreadex(NULL, 0,
		&CvObserverTransport::threadEntry, this, 0, &threadId));
	if (m_thread == NULL)
	{
		setError(ERROR_NOT_ENOUGH_MEMORY);
		CloseHandle(m_stopEvent);
		m_stopEvent = NULL;
		WSACleanup();
		m_winsockStarted = false;
		return false;
	}
	m_started = true;
	return true;
}

bool CvObserverTransport::enqueue(const CvObserverMessage& message)
{
	if (!m_started || m_stopped || message.length == 0 ||
		message.length > sizeof(message.data) ||
		message.data[message.length - 1] != '\n')
	{
		return false;
	}
	return m_queue.push(message);
}

void CvObserverTransport::stop()
{
	if (m_stopped)
		return;
	m_stopped = true;
	m_queue.close(); // Reject future producers; buffered snapshots are discarded.
	if (m_stopEvent != NULL)
		SetEvent(m_stopEvent);
	if (m_thread != NULL)
	{
		// Every network operation is nonblocking; waits poll this event at <=50ms.
		// Joining preserves ownership even if the OS schedules this worker late.
		WaitForSingleObject(m_thread, INFINITE);
		CloseHandle(m_thread);
		m_thread = NULL;
	}
	if (m_stopEvent != NULL)
	{
		CloseHandle(m_stopEvent);
		m_stopEvent = NULL;
	}
	if (m_winsockStarted)
	{
		WSACleanup();
		m_winsockStarted = false;
	}
	m_started = false;
}

bool CvObserverTransport::isRunning() const
{
	return m_started && !m_stopped;
}

unsigned long CvObserverTransport::lastError()
{
	CvFunctionMutex lock(m_errorMutex);
	return m_lastError;
}

void CvObserverTransport::setError(unsigned long error)
{
	CvFunctionMutex lock(m_errorMutex);
	m_lastError = error;
}

bool CvObserverTransport::stopping() const
{
	return WaitForSingleObject(m_stopEvent, 0) != WAIT_TIMEOUT;
}

unsigned int __stdcall CvObserverTransport::threadEntry(void* context)
{
	static_cast<CvObserverTransport*>(context)->run();
	return 0;
}

bool CvObserverTransport::waitWritable(SOCKET socket, DWORD started)
{
	while (!stopping())
	{
		DWORD elapsed = GetTickCount() - started; // Unsigned subtraction handles wrap.
		if (elapsed >= m_config.ioTimeoutMs)
		{
			setError(WSAETIMEDOUT);
			return false;
		}
		DWORD remaining = m_config.ioTimeoutMs - elapsed;
		DWORD slice = remaining < 50 ? remaining : 50;
		timeval timeout;
		timeout.tv_sec = 0;
		timeout.tv_usec = static_cast<long>(slice * 1000);
		fd_set writable;
		fd_set failed;
		FD_ZERO(&writable);
		FD_ZERO(&failed);
		FD_SET(socket, &writable);
		FD_SET(socket, &failed);
		int ready = select(0, NULL, &writable, &failed, &timeout);
		if (ready == SOCKET_ERROR)
		{
			setError(WSAGetLastError());
			return false;
		}
		if (ready == 0)
			continue;
		int socketError = 0;
		int size = sizeof(socketError);
		if (getsockopt(socket, SOL_SOCKET, SO_ERROR,
			reinterpret_cast<char*>(&socketError), &size) == SOCKET_ERROR)
		{
			setError(WSAGetLastError());
			return false;
		}
		if (socketError != 0 || FD_ISSET(socket, &failed))
		{
			setError(socketError != 0 ? socketError : WSAECONNREFUSED);
			return false;
		}
		return FD_ISSET(socket, &writable) != 0;
	}
	return false;
}

SOCKET CvObserverTransport::connectSocket()
{
	SOCKET connection = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (connection == INVALID_SOCKET)
	{
		setError(WSAGetLastError());
		return INVALID_SOCKET;
	}
	u_long nonblocking = 1;
	if (ioctlsocket(connection, FIONBIO, &nonblocking) == SOCKET_ERROR)
	{
		setError(WSAGetLastError());
		closesocket(connection);
		return INVALID_SOCKET;
	}
	sockaddr_in address;
	ZeroMemory(&address, sizeof(address));
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	address.sin_port = htons(m_config.port);
	DWORD started = GetTickCount();
	if (connect(connection, reinterpret_cast<const sockaddr*>(&address),
		sizeof(address)) == 0)
	{
		return connection;
	}
	int error = WSAGetLastError();
	if (error == WSAEWOULDBLOCK || error == WSAEINPROGRESS || error == WSAEALREADY)
	{
		if (waitWritable(connection, started))
			return connection;
	}
	else setError(error);
	closesocket(connection);
	return INVALID_SOCKET;
}

bool CvObserverTransport::sendMessage(SOCKET socket,
	const CvObserverMessage& message)
{
	unsigned int sent = 0;
	DWORD started = GetTickCount();
	while (sent < message.length && !stopping())
	{
		if (GetTickCount() - started >= m_config.ioTimeoutMs)
		{
			setError(WSAETIMEDOUT);
			return false;
		}
		int count = send(socket, message.data + sent,
			static_cast<int>(message.length - sent), 0);
		if (count > 0)
		{
			sent += count;
			continue;
		}
		if (count == 0)
		{
			setError(WSAECONNRESET);
			return false;
		}
		int error = WSAGetLastError();
		if (error != WSAEWOULDBLOCK)
		{
			setError(error);
			return false;
		}
		if (!waitWritable(socket, started))
			return false;
	}
	if (sent == message.length)
	{
		setError(0);
		return true;
	}
	return false;
}

void CvObserverTransport::run()
{
	// The worker's complete input is the copied message queue and config.
	// No CvGame, GC, gDLL, Python, game allocator, or live-game pointer is used.
	SOCKET connection = INVALID_SOCKET;
	CvObserverMessage message;
	bool pending = false;
	while (!stopping())
	{
		if (!pending)
		{
			if (!m_queue.pop(message))
			{
				// Notice an idle peer's FIN before a later turn is enqueued.
				// This is an outbound-only protocol; unsolicited bytes also close it.
				if (connection != INVALID_SOCKET)
				{
					fd_set readable;
					FD_ZERO(&readable);
					FD_SET(connection, &readable);
					timeval timeout;
					timeout.tv_sec = 0;
					timeout.tv_usec = 0;
					int ready = select(0, &readable, NULL, NULL, &timeout);
					bool closePeer = false;
					if (ready == SOCKET_ERROR)
					{
						setError(WSAGetLastError());
						closePeer = true;
					}
					else if (ready > 0)
					{
						char byte;
						int count = recv(connection, &byte, 1, MSG_PEEK);
						if (count >= 0)
						{
							setError(count == 0 ? WSAECONNRESET : WSAEOPNOTSUPP);
							closePeer = true;
						}
						else
						{
							int error = WSAGetLastError();
							if (error != WSAEWOULDBLOCK)
							{
								setError(error);
								closePeer = true;
							}
						}
					}
					if (closePeer)
					{
						closesocket(connection);
						connection = INVALID_SOCKET;
					}
				}
				WaitForSingleObject(m_stopEvent, 50);
				continue;
			}
			pending = true;
		}
		if (connection == INVALID_SOCKET)
		{
			connection = connectSocket();
			if (connection == INVALID_SOCKET)
			{
				WaitForSingleObject(m_stopEvent, m_config.retryMs);
				continue;
			}
		}
		bool delivered = sendMessage(connection, message);
		pending = false;
		if (!delivered)
		{
			// A possibly partial frame is never resumed on a different connection.
			closesocket(connection);
			connection = INVALID_SOCKET;
			WaitForSingleObject(m_stopEvent, m_config.retryMs);
		}
	}
	if (connection != INVALID_SOCKET)
		closesocket(connection);
}
// XANA: End 20261104 ObserverMCP transport prototype (ChatGPT).
#endif // CV_OBSERVER_ENABLE
