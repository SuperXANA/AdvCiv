// XANA: 2026-11-04 ObserverMCP - focused standalone C++03 tests.
// No Civilization IV headers or objects are used by this program.
#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <windows.h>
#include <process.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <pthread.h>
#include <sys/time.h>
#include <time.h>
#endif

#include "CvObserverCore.h"
#ifdef _WIN32
#include "CvObserverTransport.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

static void check(bool condition, const char* expression, int line)
{
	if (!condition)
	{
		fprintf(stderr, "FAIL line %d: %s\n", line, expression);
		exit(1);
	}
}
#define CHECK(expression) check(!!(expression), #expression, __LINE__)

static unsigned long nowMs()
{
#ifdef _WIN32
	return GetTickCount();
#else
	struct timeval value;
	gettimeofday(&value, NULL);
	return (unsigned long)value.tv_sec * 1000UL + value.tv_usec / 1000;
#endif
}

static void pauseMs(unsigned long milliseconds)
{
#ifdef _WIN32
	Sleep(milliseconds);
#else
	struct timespec delay;
	delay.tv_sec = milliseconds / 1000;
	delay.tv_nsec = (milliseconds % 1000) * 1000000;
	nanosleep(&delay, NULL);
#endif
}

static CvObserverSnapshot snapshotValue(unsigned long id, int turn)
{
	CvObserverSnapshot value;
	value.sessionId = "abc012";
	value.sessionSequence = 1;
	value.worldId = "89abcdef-00000001";
	value.worldSequence = 1;
	value.mapSeed = 0x89abcdefUL;
	value.captureId = id;
	value.snapshotId = id;
	value.gameTurn = turn;
	value.playerCount = 1;
	value.playerIndex = 0;
	value.hasPlayer = true;
	value.player.id = 0;
	value.player.teamId = 0;
	value.player.civilizationType = 1;
	value.player.leaderType = 2;
	value.player.isHuman = true;
	value.player.isBarbarian = false;
	value.player.cityCount = 1;
	value.player.totalPopulation = 3;
	value.player.cityOffset = 0;
	value.player.cityPart = 0;
	value.player.cityPartCount = 1;
	value.player.citiesInMessage = 1;
	value.player.cities[0].id = 10;
	value.player.cities[0].x = 20;
	value.player.cities[0].y = 30;
	value.player.cities[0].population = 3;
	return value;
}

static CvObserverMessage snapshot(unsigned long id, int turn)
{
	CvObserverMessage message;
	CHECK(CvObserverFormatSnapshot(snapshotValue(id, turn), message));
	return message;
}

static void testFormatAndCopies()
{
	CvObserverMessage message = snapshot(7, 42);
	CHECK(message.length < sizeof(message.data));
	CHECK(message.data[message.length - 1] == '\n');
	CHECK(message.data[message.length] == 0);
	CHECK(strstr(message.data, "\"version\":2") != NULL);
	CHECK(strstr(message.data, "\"game_session\":{\"id\":\"abc012\"") != NULL);
	CHECK(strstr(message.data, "\"world_instance\":{\"id\":\"89abcdef-00000001\"") != NULL);
	CHECK(strstr(message.data, "\"capture_id\":7") != NULL);
	CHECK(strstr(message.data, "\"players\":[{\"id\":0") != NULL);
	CHECK(strstr(message.data, "\"cities\":[{\"id\":10") != NULL);

	CvObserverSnapshot value = snapshotValue(0xffffffffUL, INT_MIN);
	CHECK(CvObserverFormatSnapshot(value, message));
	CHECK(strstr(message.data, "4294967295") != NULL);
	CHECK(strstr(message.data, "-2147483648") != NULL);
	value = snapshotValue(1, INT_MAX);
	value.sessionId = "0";
	CHECK(CvObserverFormatSnapshot(value, message));
	value.sessionId = "";
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.sessionId = NULL;
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.sessionId = "not-hex";
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.sessionId = "a\"";
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.sessionId = "aa\n";
	CHECK(!CvObserverFormatSnapshot(value, message));
	value = snapshotValue(0, 0);
	CHECK(!CvObserverFormatSnapshot(value, message));
	value = snapshotValue(1, 0);
	value.worldId = "89abcdef00000001";
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.worldId = NULL;
	CHECK(!CvObserverFormatSnapshot(value, message));
	value = snapshotValue(1, 0);
	value.mapSeed = 0;
	CHECK(!CvObserverFormatSnapshot(value, message));
	value.worldId = "00000000-00000001";
	CHECK(CvObserverFormatSnapshot(value, message));
	value = snapshotValue(1, 0);
	value.captureId = 0;
	CHECK(!CvObserverFormatSnapshot(value, message));
	char longSession[66];
	memset(longSession, 'a', 65);
	longSession[65] = 0;
	value = snapshotValue(1, 0);
	value.sessionId = longSession;
	CHECK(!CvObserverFormatSnapshot(value, message));
	longSession[64] = 0;
	CHECK(CvObserverFormatSnapshot(value, message));
#if ULONG_MAX > 0xffffffffUL
	value = snapshotValue(1, 0);
	value.mapSeed = 0x100000000UL;
	CHECK(!CvObserverFormatSnapshot(value, message));
#endif

	value = snapshotValue(1, 0);
	value.hasPlayer = false;
	CHECK(!CvObserverFormatSnapshot(value, message));
	value = snapshotValue(1, 0);
	value.playerCount = 0;
	value.playerIndex = -1;
	value.hasPlayer = false;
	CHECK(CvObserverFormatSnapshot(value, message));
	CHECK(strstr(message.data, "\"players\":[]") != NULL);
	value = snapshotValue(1, 0);
	value.player.cities[0].population = -1;
	CHECK(!CvObserverFormatSnapshot(value, message));
	value = snapshotValue(1, 0);
	value.player.cityPartCount = 2;
	CHECK(!CvObserverFormatSnapshot(value, message));

	value = snapshotValue(1, 0);
	value.player.cityCount = 33;
	value.player.totalPopulation = 33;
	value.player.cityPartCount = 2;
	value.player.citiesInMessage = 32;
	for (int i = 0; i < 32; ++i)
	{
		value.player.cities[i].id = INT_MIN + i;
		value.player.cities[i].x = INT_MIN;
		value.player.cities[i].y = INT_MAX;
		value.player.cities[i].population = INT_MAX;
	}
	CHECK(CvObserverFormatSnapshot(value, message));
	CHECK(strstr(message.data, "\"city_part_count\":2") != NULL);
	value.player.cityOffset = 32;
	value.player.cityPart = 1;
	value.player.citiesInMessage = 1;
	value.player.cities[0].id = 32;
	CHECK(CvObserverFormatSnapshot(value, message));
	CHECK(strstr(message.data, "\"city_offset\":32") != NULL);
	value.player.cityOffset = 31;
	CHECK(!CvObserverFormatSnapshot(value, message));

	// The queue must own a serialized copy, independent of the producer's buffer.
	CvObserverQueue queue(2);
	CvObserverMessage expected = snapshot(7, 42);
	message = expected;
	CHECK(queue.push(message));
	memset(message.data, 'x', sizeof(message.data));
	message.length = 1;
	CvObserverMessage copy;
	CHECK(queue.pop(copy));
	CHECK(copy.length == expected.length);
	CHECK(memcmp(copy.data, expected.data, expected.length) == 0);
}

static void testQueueBoundsAndClose()
{
	CvObserverQueue queue(2);
	CvObserverMessage message;
	CHECK(!queue.pop(message));
	CHECK(queue.push(snapshot(1, 1)));
	CHECK(queue.push(snapshot(2, 2)));
	CHECK(queue.push(snapshot(3, 3)));
	CHECK(queue.size() == 2);
	CHECK(queue.dropped() == 1);
	CHECK(queue.pop(message));
	CvObserverMessage expected = snapshot(2, 2);
	CHECK(message.length == expected.length);
	CHECK(memcmp(message.data, expected.data, expected.length) == 0);
	queue.close();
	queue.close();
	CHECK(!queue.push(snapshot(4, 4)));
	CHECK(!queue.pop(message));
	CHECK(queue.size() == 0);
	CvObserverQueue validation(2);
	message.length = 0;
	CHECK(!validation.push(message));
	message.length = CV_OBSERVER_MESSAGE_CAPACITY + 1;
	CHECK(!validation.push(message));

	CvObserverQueue minimum(0);
	CHECK(minimum.push(snapshot(1, 1)));
	CHECK(minimum.push(snapshot(2, 2)));
	CHECK(minimum.size() == 1);
	CHECK(minimum.dropped() == 1);
	CvObserverQueue maximum(1000);
	for (unsigned long i = 1; i <= 65; ++i)
		CHECK(maximum.push(snapshot(i, (int)i)));
	CHECK(maximum.size() == 64);
	CHECK(maximum.dropped() == 1);
}

// Test-only synchronization for the consumer's completion flag.
struct Completion
{
#ifdef _WIN32
	CRITICAL_SECTION mutex;
#else
	pthread_mutex_t mutex;
#endif
	bool done;
	Completion() : done(false)
	{
#ifdef _WIN32
		InitializeCriticalSection(&mutex);
#else
		CHECK(pthread_mutex_init(&mutex, NULL) == 0);
#endif
	}
	~Completion()
	{
#ifdef _WIN32
		DeleteCriticalSection(&mutex);
#else
		CHECK(pthread_mutex_destroy(&mutex) == 0);
#endif
	}
	bool finished(bool set)
	{
#ifdef _WIN32
		EnterCriticalSection(&mutex);
#else
		CHECK(pthread_mutex_lock(&mutex) == 0);
#endif
		if (set)
			done = true;
		bool result = done;
#ifdef _WIN32
		LeaveCriticalSection(&mutex);
#else
		CHECK(pthread_mutex_unlock(&mutex) == 0);
#endif
		return result;
	}
};

enum { MESSAGES_PER_PRODUCER = 5000, TOTAL_MESSAGES = 10000 };
struct ConcurrentContext
{
	CvObserverQueue queue;
	Completion completion;
	bool seen[TOTAL_MESSAGES + 1];
	unsigned long consumed;
	ConcurrentContext() : queue(64), consumed(0)
	{
		memset(seen, 0, sizeof(seen));
	}
};

struct ProducerContext
{
	ConcurrentContext* shared;
	unsigned long firstId;
};

static void produce(void* argument)
{
	ProducerContext& context = *static_cast<ProducerContext*>(argument);
	for (unsigned long offset = 0; offset < MESSAGES_PER_PRODUCER; ++offset)
	{
		unsigned long id = context.firstId + offset;
		CHECK(context.shared->queue.push(snapshot(id, (int)id)));
		if ((offset % 101) == 0)
			pauseMs(1);
	}
}

static void consume(void* argument)
{
	ConcurrentContext& context = *static_cast<ConcurrentContext*>(argument);
	unsigned long deadline = nowMs();
	for (;;)
	{
		CHECK(nowMs() - deadline < 10000UL);
		CvObserverMessage message;
		if (!context.queue.pop(message))
		{
			if (context.completion.finished(false) && context.queue.size() == 0)
				break;
			pauseMs(1);
			continue;
		}
		CHECK(message.length < sizeof(message.data));
		message.data[message.length] = 0;
		const char* field = strstr(message.data, "\"snapshot_id\":");
		CHECK(field != NULL);
		unsigned long id = strtoul(field + strlen("\"snapshot_id\":"), NULL, 10);
		CHECK(id >= 1 && id <= TOTAL_MESSAGES);
		CHECK(!context.seen[id]);
		context.seen[id] = true;
		CvObserverMessage expected = snapshot(id, (int)id);
		CHECK(message.length == expected.length);
		CHECK(memcmp(message.data, expected.data, expected.length) == 0);
		++context.consumed;
	}
}

#ifdef _WIN32
static unsigned __stdcall producerEntry(void* argument) { produce(argument); return 0; }
static unsigned __stdcall consumerEntry(void* argument) { consume(argument); return 0; }
#else
static void* producerEntry(void* argument) { produce(argument); return NULL; }
static void* consumerEntry(void* argument) { consume(argument); return NULL; }
#endif

static void testConcurrentQueue()
{
	ConcurrentContext context;
	ProducerContext producers[2];
	producers[0].shared = &context;
	producers[0].firstId = 1;
	producers[1].shared = &context;
	producers[1].firstId = MESSAGES_PER_PRODUCER + 1;
#ifdef _WIN32
	HANDLE consumer = (HANDLE)_beginthreadex(NULL, 0, consumerEntry, &context, 0, NULL);
	CHECK(consumer != NULL);
	HANDLE workers[2];
	for (int i = 0; i < 2; ++i)
	{
		workers[i] = (HANDLE)_beginthreadex(NULL, 0, producerEntry, &producers[i], 0, NULL);
		CHECK(workers[i] != NULL);
	}
	CHECK(WaitForMultipleObjects(2, workers, TRUE, 10000) == WAIT_OBJECT_0);
	context.completion.finished(true);
	CHECK(WaitForSingleObject(consumer, 10000) == WAIT_OBJECT_0);
	CloseHandle(consumer);
	CloseHandle(workers[0]);
	CloseHandle(workers[1]);
#else
	pthread_t consumer;
	pthread_t workers[2];
	CHECK(pthread_create(&consumer, NULL, consumerEntry, &context) == 0);
	for (int i = 0; i < 2; ++i)
		CHECK(pthread_create(&workers[i], NULL, producerEntry, &producers[i]) == 0);
	CHECK(pthread_join(workers[0], NULL) == 0);
	CHECK(pthread_join(workers[1], NULL) == 0);
	context.completion.finished(true);
	CHECK(pthread_join(consumer, NULL) == 0);
#endif
	CHECK(context.queue.size() == 0);
	CHECK(context.consumed > 0);
	CHECK(context.consumed + context.queue.dropped() == TOTAL_MESSAGES);
	context.queue.close();
}

#ifdef _WIN32
static SOCKET boundSocket(unsigned short& port, bool listenNow)
{
	SOCKET result = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	CHECK(result != INVALID_SOCKET);
	sockaddr_in address;
	memset(&address, 0, sizeof(address));
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	address.sin_port = 0;
	CHECK(bind(result, (sockaddr*)&address, sizeof(address)) == 0);
	int addressBytes = sizeof(address);
	CHECK(getsockname(result, (sockaddr*)&address, &addressBytes) == 0);
	port = ntohs(address.sin_port);
	if (listenNow)
		CHECK(listen(result, 4) == 0);
	return result;
}

static SOCKET acceptBefore(SOCKET listener, unsigned long timeout)
{
	unsigned long started = nowMs();
	while (nowMs() - started < timeout)
	{
		fd_set ready;
		FD_ZERO(&ready);
		FD_SET(listener, &ready);
		timeval wait;
		wait.tv_sec = 0;
		wait.tv_usec = 20000;
		int status = select(0, &ready, NULL, NULL, &wait);
		CHECK(status != SOCKET_ERROR);
		if (status > 0)
		{
			SOCKET peer = accept(listener, NULL, NULL);
			CHECK(peer != INVALID_SOCKET);
			return peer;
		}
	}
	return INVALID_SOCKET;
}

static void readOneByteAtATime(SOCKET peer, const CvObserverMessage& expected)
{
	char received[512];
	unsigned int count = 0;
	unsigned long started = nowMs();
	while (count < expected.length)
	{
		CHECK(nowMs() - started < 5000UL);
		fd_set ready;
		FD_ZERO(&ready);
		FD_SET(peer, &ready);
		timeval wait;
		wait.tv_sec = 0;
		wait.tv_usec = 20000;
		int status = select(0, &ready, NULL, NULL, &wait);
		CHECK(status != SOCKET_ERROR);
		if (status == 0)
			continue;
		CHECK(recv(peer, received + count, 1, 0) == 1);
		++count;
	}
	CHECK(memcmp(received, expected.data, count) == 0);
}

static void checkStop(CvObserverTransport& transport)
{
	unsigned long started = nowMs();
	transport.stop();
	CHECK(nowMs() - started < 2500UL);
	CHECK(!transport.isRunning());
	transport.stop();
	CHECK(!transport.enqueue(snapshot(1, 1)));
}

static void testTransportConfiguration()
{
	CvObserverTransportConfig defaults;
	CvObserverTransport dormant(defaults);
	CHECK(!dormant.isRunning());
	CHECK(!dormant.enqueue(snapshot(1, 1)));
	dormant.stop();
	dormant.stop();
	CHECK(!dormant.start());
	for (int invalid = 0; invalid < 7; ++invalid)
	{
		CvObserverTransportConfig config;
		switch (invalid)
		{
		case 0: config.port = 0; break;
		case 1: config.queueCapacity = 0; break;
		case 2: config.queueCapacity = 65; break;
		case 3: config.retryMs = 49; break;
		case 4: config.retryMs = 30001; break;
		case 5: config.ioTimeoutMs = 49; break;
		case 6: config.ioTimeoutMs = 5001; break;
		}
		CvObserverTransport transport(config);
		CHECK(!transport.start());
		CHECK(!transport.isRunning());
		CHECK(transport.lastError() == ERROR_INVALID_PARAMETER);
		transport.stop();
	}
}

static void testDisconnectedAndShutdown()
{
	unsigned short port;
	// Keep the port reserved, but do not listen: connects must fail.
	SOCKET reserved = boundSocket(port, false);
	CvObserverTransportConfig config;
	config.port = port;
	config.queueCapacity = 2;
	config.retryMs = 100;
	config.ioTimeoutMs = 100;
	CvObserverTransport transport(config);
	CHECK(transport.start());
	CHECK(transport.start()); // Starting an already active instance is harmless.
	for (unsigned long id = 1; id <= 1000; ++id)
		CHECK(transport.enqueue(snapshot(id, (int)id)));
	unsigned long started = nowMs();
	while (transport.lastError() == 0 && nowMs() - started < 3000UL)
		pauseMs(10);
	CHECK(transport.lastError() != 0);
	checkStop(transport);
	CHECK(!transport.start()); // A stopped queue is final; create a new session.
	closesocket(reserved);
}

static void testLoopbackAndReconnect()
{
	unsigned short port;
	SOCKET listener = boundSocket(port, true);
	CvObserverTransportConfig config;
	config.port = port;
	config.queueCapacity = 4;
	config.retryMs = 100;
	config.ioTimeoutMs = 100;
	CvObserverTransport transport(config);
	CHECK(transport.start());
	CvObserverMessage first = snapshot(1, 11);
	CHECK(transport.enqueue(first));
	SOCKET peer = acceptBefore(listener, 5000);
	CHECK(peer != INVALID_SOCKET);
	readOneByteAtATime(peer, first);

	// A receiver can close normally between turns (for example on idle timeout).
	// The idle peer check must observe FIN before the next snapshot is offered.
	CHECK(shutdown(peer, SD_BOTH) == 0);
	closesocket(peer);
	pauseMs(200);
	CvObserverMessage second = snapshot(2, 12);
	CHECK(transport.enqueue(second));
	peer = acceptBefore(listener, 5000);
	CHECK(peer != INVALID_SOCKET);
	readOneByteAtATime(peer, second);

	linger reset;
	reset.l_onoff = 1;
	reset.l_linger = 0;
	CHECK(setsockopt(peer, SOL_SOCKET, SO_LINGER, (const char*)&reset, sizeof(reset)) == 0);
	closesocket(peer);
	// A failed frame is intentionally not replayed; keep offering newer snapshots.
	peer = INVALID_SOCKET;
	unsigned long started = nowMs();
	unsigned long id = 3;
	while (peer == INVALID_SOCKET && nowMs() - started < 5000UL)
	{
		CHECK(transport.enqueue(snapshot(id, (int)id)));
		++id;
		peer = acceptBefore(listener, 150);
	}
	CHECK(peer != INVALID_SOCKET);
	// Confirm the reconnected stream consists of a complete v1 frame.
	char line[512];
	unsigned int length = 0;
	started = nowMs();
	while (length < sizeof(line) - 1)
	{
		CHECK(nowMs() - started < 5000UL);
		fd_set ready;
		FD_ZERO(&ready);
		FD_SET(peer, &ready);
		timeval wait;
		wait.tv_sec = 0;
		wait.tv_usec = 20000;
		int status = select(0, &ready, NULL, NULL, &wait);
		CHECK(status != SOCKET_ERROR);
		if (status == 0)
			continue;
		CHECK(recv(peer, line + length, 1, 0) == 1);
		if (line[length++] == '\n')
			break;
	}
	CHECK(length > 0 && line[length - 1] == '\n');
	line[length] = 0;
	const char* field = strstr(line, "\"snapshot_id\":");
	CHECK(field != NULL);
	unsigned long receivedId = strtoul(field + strlen("\"snapshot_id\":"), NULL, 10);
	CHECK(receivedId >= 3);
	CvObserverMessage expected = snapshot(receivedId, (int)receivedId);
	CHECK(length == expected.length);
	CHECK(memcmp(line, expected.data, length) == 0);

	// Receiver remains connected without reading. Shutdown must still finish.
	int smallBuffer = 512;
	CHECK(setsockopt(peer, SOL_SOCKET, SO_RCVBUF, (const char*)&smallBuffer, sizeof(smallBuffer)) == 0);
	for (unsigned long pending = id; pending < id + 20000; ++pending)
		CHECK(transport.enqueue(snapshot(pending, (int)pending)));
	checkStop(transport);
	closesocket(peer);
	closesocket(listener);
}

static unsigned __stdcall watchdogEntry(void* argument)
{
	// Fail the standalone test process if a regression makes stop() hang.
	// Production transport never terminates a thread or process this way.
	HANDLE finished = reinterpret_cast<HANDLE>(argument);
	if (WaitForSingleObject(finished, 30000) != WAIT_OBJECT_0)
	{
		fprintf(stderr, "FAIL: native transport tests exceeded 30 seconds\n");
		fflush(stderr);
		ExitProcess(1);
	}
	return 0;
}
#endif

int main(int argc, char** argv)
{
	if (argc == 2 && (strcmp(argv[1], "--emit-json") == 0 || strcmp(argv[1], "--emit") == 0))
	{
		CvObserverMessage examples[3];
		examples[0] = snapshot(1, 0);
		examples[1] = snapshot(2, INT_MIN);
		examples[2] = snapshot(0xffffffffUL, INT_MAX);
		for (int i = 0; i < 3; ++i)
			CHECK(fwrite(examples[i].data, 1, examples[i].length, stdout) == examples[i].length);
		return 0;
	}
	testFormatAndCopies();
	testQueueBoundsAndClose();
	testConcurrentQueue();
#ifdef _WIN32
	HANDLE finished = CreateEvent(NULL, TRUE, FALSE, NULL);
	CHECK(finished != NULL);
	HANDLE watchdog = (HANDLE)_beginthreadex(NULL, 0, watchdogEntry, finished, 0, NULL);
	CHECK(watchdog != NULL);
	WSADATA winsock;
	CHECK(WSAStartup(MAKEWORD(2, 2), &winsock) == 0);
	testTransportConfiguration();
	testDisconnectedAndShutdown();
	testLoopbackAndReconnect();
	CHECK(WSACleanup() == 0);
	CHECK(SetEvent(finished) != 0);
	CHECK(WaitForSingleObject(watchdog, 5000) == WAIT_OBJECT_0);
	CloseHandle(watchdog);
	CloseHandle(finished);
	puts("PASS: snapshot/JSON/queue/concurrency/Windows loopback/disconnect/shutdown");
#else
	puts("PASS: snapshot/JSON/queue/concurrency (Windows transport not executed)");
#endif
	return 0;
}
// XANA: 2026-11-04 ObserverMCP end.
