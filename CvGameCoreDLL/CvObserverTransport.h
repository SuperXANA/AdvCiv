#ifndef CV_OBSERVER_TRANSPORT_H
#define CV_OBSERVER_TRANSPORT_H

#include "CvObserverConfig.h"
#ifdef CV_OBSERVER_ENABLE
// XANA: 20261104 ObserverMCP transport prototype (ChatGPT).
// Winsock2 must precede any non-lean Windows.h inclusion in standalone tests.
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <winsock2.h>
#include "CvObserverCore.h"

struct CvObserverTransportConfig
{
	unsigned short port;
	unsigned int queueCapacity;
	unsigned long retryMs;
	unsigned long ioTimeoutMs;
	CvObserverTransportConfig();
};

// All lifecycle/enqueue calls belong to one owner (the game thread).
// stop() joins the worker before destroying any queue/event resources.
// Never call stop(), destroy this object, or wait for it from DllMain.
// An instance is single-use: create a fresh instance after stop().
class CvObserverTransport
{
public:
	explicit CvObserverTransport(const CvObserverTransportConfig& config);
	~CvObserverTransport();
	bool start();
	bool enqueue(const CvObserverMessage& message);
	void stop();
	// Thread-safe diagnostic; a completed send clears the preceding error.
	unsigned long lastError();
	bool isRunning() const;

private:
	CvObserverTransport(const CvObserverTransport&);
	CvObserverTransport& operator=(const CvObserverTransport&);
	static unsigned int __stdcall threadEntry(void* context);
	void run();
	bool stopping() const;
	bool waitWritable(SOCKET socket, DWORD started);
	SOCKET connectSocket();
	bool sendMessage(SOCKET socket, const CvObserverMessage& message);
	void setError(unsigned long error);

	CvObserverTransportConfig m_config;
	CvObserverQueue m_queue;
	HANDLE m_stopEvent;
	HANDLE m_thread;
	bool m_started;
	bool m_stopped;
	bool m_winsockStarted;
	CvCriticalSection m_errorMutex;
	unsigned long m_lastError;
};
// XANA: End 20261104 ObserverMCP transport prototype (ChatGPT).
#endif // CV_OBSERVER_ENABLE
#endif // CV_OBSERVER_TRANSPORT_H
