#ifndef CV_OBSERVER_CORE_H
#define CV_OBSERVER_CORE_H
#include "CvObserverConfig.h"
#ifdef CV_OBSERVER_ENABLE

// XANA: 2026-11-04 ObserverMCP - copied data only, no game dependencies
#ifdef CV_OBSERVER_TEST_POSIX
// Test adapter only. Shipping Windows builds use the original branch's locks.
#include <pthread.h>
class CvCriticalSection
{
	pthread_mutex_t m_mutex;
	CvCriticalSection(const CvCriticalSection&);
	CvCriticalSection& operator=(const CvCriticalSection&);
public:
	CvCriticalSection() { pthread_mutex_init(&m_mutex, 0); }
	~CvCriticalSection() { pthread_mutex_destroy(&m_mutex); }
	void lock() { pthread_mutex_lock(&m_mutex); }
	void unlock() { pthread_mutex_unlock(&m_mutex); }
};
class CvFunctionMutex
{
	CvCriticalSection& m_mutex;
	CvFunctionMutex(const CvFunctionMutex&);
	CvFunctionMutex& operator=(const CvFunctionMutex&);
public:
	explicit CvFunctionMutex(CvCriticalSection& mutex) : m_mutex(mutex) { m_mutex.lock(); }
	~CvFunctionMutex() { m_mutex.unlock(); }
};
#else
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include "CvCriticalSectionMutex.h"
#endif

enum
{
	CV_OBSERVER_MESSAGE_CAPACITY = 4096,
	CV_OBSERVER_CITY_CHUNK_SIZE = 32
};

struct CvObserverMessage
{
	char data[CV_OBSERVER_MESSAGE_CAPACITY]; // Includes LF and a trailing NUL.
	unsigned int length;
};

struct CvObserverCity
{
	int id;
	int x;
	int y;
	int population;
};

struct CvObserverPlayer
{
	int id;
	int teamId;
	int civilizationType;
	int leaderType;
	bool isHuman;
	bool isBarbarian;
	int cityCount;
	int totalPopulation;
	int cityOffset;
	int cityPart;
	int cityPartCount;
	int citiesInMessage;
	CvObserverCity cities[CV_OBSERVER_CITY_CHUNK_SIZE];
};

// Detached values only: no CvGame/CvPlayer/CvCity pointers or deferred callbacks.
// One record contains zero or one player and at most one bounded city chunk.
struct CvObserverSnapshot
{
	CvObserverSnapshot();
	const char* sessionId;
	unsigned long sessionSequence;
	const char* worldId;
	unsigned long worldSequence;
	unsigned long mapSeed;
	unsigned long captureId;
	unsigned long snapshotId;
	int gameTurn;
	int playerCount;
	int playerIndex;
	bool hasPlayer;
	CvObserverPlayer player;
};

bool CvObserverFormatSnapshot(const CvObserverSnapshot& snapshot,
	CvObserverMessage& message);

class CvObserverQueue
{
public:
	explicit CvObserverQueue(unsigned int capacity);
	bool push(const CvObserverMessage& message); // Copy; discard oldest when full.
	bool pop(CvObserverMessage& message); // Copy; never blocks for data.
	void close(); // Reject producers and discard pending data; idempotent.
	unsigned int size();
	unsigned long dropped();
private:
	CvObserverQueue(const CvObserverQueue&);
	CvObserverQueue& operator=(const CvObserverQueue&);
	CvCriticalSection m_mutex;
	CvObserverMessage m_messages[64];
	unsigned int m_capacity, m_head, m_size;
	unsigned long m_dropped;
	bool m_closed;
};
// XANA: 2026-11-08 ObserverMCP hierarchical protocol v2
#endif
#endif
