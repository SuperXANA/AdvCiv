#include "CvObserverCore.h"
#ifdef CV_OBSERVER_ENABLE
#include <stdio.h>
#include <string.h>
#include <limits.h>

// XANA: 2026-11-08 ObserverMCP - protocol v2, bounded hierarchical values
namespace
{
	bool observerUint32(unsigned long value)
	{
		if (value == 0)
			return false;
#if ULONG_MAX > 0xffffffffUL
		if (value > 0xffffffffUL)
			return false;
#endif
		return true;
	}

	bool observerHex(char c)
	{
		return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
			(c >= 'A' && c <= 'F');
	}

	bool observerSessionId(const char* id)
	{
		if (id == NULL)
			return false;
		unsigned int i = 0;
		for (; i <= 64 && id[i] != 0; ++i)
		{
			if (!observerHex(id[i]))
				return false;
		}
		return i > 0 && i <= 64;
	}

	bool observerWorldId(const char* id)
	{
		if (id == NULL)
			return false;
		for (unsigned int i = 0; i < 17; ++i)
		{
			if (i == 8)
			{
				if (id[i] != '-')
					return false;
			}
			else if (!observerHex(id[i]))
				return false;
		}
		return id[17] == 0;
	}

	bool observerPlayer(const CvObserverPlayer& player)
	{
		if (player.cityCount < 0 || player.totalPopulation < 0 ||
			player.cityOffset < 0 || player.cityPart < 0 ||
			player.cityPartCount < 1 || player.cityPart >= player.cityPartCount ||
			player.citiesInMessage < 0 ||
			player.citiesInMessage > CV_OBSERVER_CITY_CHUNK_SIZE)
			return false;
		int expectedParts = player.cityCount / CV_OBSERVER_CITY_CHUNK_SIZE;
		if (player.cityCount % CV_OBSERVER_CITY_CHUNK_SIZE != 0)
			++expectedParts;
		if (expectedParts < 1)
			expectedParts = 1;
		if (player.cityPartCount != expectedParts ||
			player.cityOffset / CV_OBSERVER_CITY_CHUNK_SIZE != player.cityPart ||
			player.cityOffset % CV_OBSERVER_CITY_CHUNK_SIZE != 0 ||
			player.cityOffset > player.cityCount)
			return false;
		int remaining = player.cityCount - player.cityOffset;
		int expectedCities = remaining < CV_OBSERVER_CITY_CHUNK_SIZE ?
			remaining : CV_OBSERVER_CITY_CHUNK_SIZE;
		if (player.citiesInMessage != expectedCities)
			return false;
		for (int i = 0; i < player.citiesInMessage; ++i)
		{
			if (player.cities[i].population < 0)
				return false;
		}
		return true;
	}

	class CvObserverJsonWriter
	{
	public:
		explicit CvObserverJsonWriter(CvObserverMessage& message)
		: m_data(message.data), m_capacity(CV_OBSERVER_MESSAGE_CAPACITY),
		  m_length(0), m_valid(true)
		{}

		void append(const char* text, unsigned int count)
		{
			if (!m_valid)
				return;
			// Reserve one byte for a diagnostic NUL after the LF-terminated wire data.
			if (count >= m_capacity - m_length)
			{
				m_valid = false;
				return;
			}
			memcpy(m_data + m_length, text, count);
			m_length += count;
			m_data[m_length] = 0;
		}

		void number(int value)
		{
			char buffer[16];
			int count = sprintf(buffer, "%d", value);
			if (count <= 0)
			{
				m_valid = false;
				return;
			}
			append(buffer, static_cast<unsigned int>(count));
		}

		void number(unsigned long value)
		{
			char buffer[32];
			int count = sprintf(buffer, "%lu", value);
			if (count <= 0)
			{
				m_valid = false;
				return;
			}
			append(buffer, static_cast<unsigned int>(count));
		}

		bool valid() const { return m_valid; }
		unsigned int length() const { return m_length; }
	private:
		char* m_data;
		unsigned int m_capacity;
		unsigned int m_length;
		bool m_valid;
	};

#define CV_OBSERVER_LITERAL(writer, text) writer.append(text, sizeof(text) - 1)

	void observerWritePlayer(CvObserverJsonWriter& writer,
		const CvObserverPlayer& player)
	{
		CV_OBSERVER_LITERAL(writer, "{\"id\":");
		writer.number(player.id);
		CV_OBSERVER_LITERAL(writer, ",\"team_id\":");
		writer.number(player.teamId);
		CV_OBSERVER_LITERAL(writer, ",\"civilization_type\":");
		writer.number(player.civilizationType);
		CV_OBSERVER_LITERAL(writer, ",\"leader_type\":");
		writer.number(player.leaderType);
		CV_OBSERVER_LITERAL(writer, ",\"is_human\":");
		if (player.isHuman)
			CV_OBSERVER_LITERAL(writer, "true");
		else
			CV_OBSERVER_LITERAL(writer, "false");
		CV_OBSERVER_LITERAL(writer, ",\"is_barbarian\":");
		if (player.isBarbarian)
			CV_OBSERVER_LITERAL(writer, "true");
		else
			CV_OBSERVER_LITERAL(writer, "false");
		CV_OBSERVER_LITERAL(writer, ",\"city_count\":");
		writer.number(player.cityCount);
		CV_OBSERVER_LITERAL(writer, ",\"total_population\":");
		writer.number(player.totalPopulation);
		CV_OBSERVER_LITERAL(writer, ",\"city_offset\":");
		writer.number(player.cityOffset);
		CV_OBSERVER_LITERAL(writer, ",\"city_part\":");
		writer.number(player.cityPart);
		CV_OBSERVER_LITERAL(writer, ",\"city_part_count\":");
		writer.number(player.cityPartCount);
		CV_OBSERVER_LITERAL(writer, ",\"cities\":[");
		for (int i = 0; i < player.citiesInMessage; ++i)
		{
			if (i != 0)
				CV_OBSERVER_LITERAL(writer, ",");
			const CvObserverCity& city = player.cities[i];
			CV_OBSERVER_LITERAL(writer, "{\"id\":");
			writer.number(city.id);
			CV_OBSERVER_LITERAL(writer, ",\"x\":");
			writer.number(city.x);
			CV_OBSERVER_LITERAL(writer, ",\"y\":");
			writer.number(city.y);
			CV_OBSERVER_LITERAL(writer, ",\"population\":");
			writer.number(city.population);
			CV_OBSERVER_LITERAL(writer, "}");
		}
		CV_OBSERVER_LITERAL(writer, "]}");
	}
}

CvObserverSnapshot::CvObserverSnapshot()
: sessionId(NULL), sessionSequence(0), worldId(NULL), worldSequence(0),
  mapSeed(0), captureId(0), snapshotId(0), gameTurn(0), playerCount(0),
  playerIndex(-1), hasPlayer(false)
{
	memset(&player, 0, sizeof(player));
}

bool CvObserverFormatSnapshot(const CvObserverSnapshot& snapshot,
	CvObserverMessage& message)
{
	memset(&message, 0, sizeof(message));
	if (!observerSessionId(snapshot.sessionId) ||
		!observerWorldId(snapshot.worldId) ||
		!observerUint32(snapshot.sessionSequence) ||
		!observerUint32(snapshot.worldSequence) ||
		!observerUint32(snapshot.captureId) ||
		!observerUint32(snapshot.snapshotId))
		return false;
#if ULONG_MAX > 0xffffffffUL
	if (snapshot.mapSeed > 0xffffffffUL)
		return false;
#endif
	char expectedWorld[18];
	sprintf(expectedWorld, "%08lx-%08lx", snapshot.mapSeed, snapshot.worldSequence);
	if (strcmp(expectedWorld, snapshot.worldId) != 0)
		return false;
	if (snapshot.hasPlayer)
	{
		if (snapshot.playerCount < 1 || snapshot.playerIndex < 0 ||
			snapshot.playerIndex >= snapshot.playerCount ||
			!observerPlayer(snapshot.player))
			return false;
	}
	else if (snapshot.playerCount != 0 || snapshot.playerIndex != -1)
		return false;

	CvObserverJsonWriter writer(message);
	CV_OBSERVER_LITERAL(writer,
		"{\"protocol\":\"advciv-observer\",\"version\":2,"
		"\"type\":\"snapshot\",\"game_session\":{\"id\":\"");
	writer.append(snapshot.sessionId, static_cast<unsigned int>(strlen(snapshot.sessionId)));
	CV_OBSERVER_LITERAL(writer, "\",\"sequence\":");
	writer.number(snapshot.sessionSequence);
	CV_OBSERVER_LITERAL(writer, ",\"world_instance\":{\"id\":\"");
	writer.append(snapshot.worldId, 17);
	CV_OBSERVER_LITERAL(writer, "\",\"sequence\":");
	writer.number(snapshot.worldSequence);
	CV_OBSERVER_LITERAL(writer, ",\"map_seed\":");
	writer.number(snapshot.mapSeed);
	CV_OBSERVER_LITERAL(writer, ",\"state\":{\"capture_id\":");
	writer.number(snapshot.captureId);
	CV_OBSERVER_LITERAL(writer, ",\"snapshot_id\":");
	writer.number(snapshot.snapshotId);
	CV_OBSERVER_LITERAL(writer, ",\"boundary\":\"post_update\",\"game_turn\":");
	writer.number(snapshot.gameTurn);
	CV_OBSERVER_LITERAL(writer, ",\"player_count\":");
	writer.number(snapshot.playerCount);
	CV_OBSERVER_LITERAL(writer, ",\"player_index\":");
	writer.number(snapshot.playerIndex);
	CV_OBSERVER_LITERAL(writer, ",\"players\":[");
	if (snapshot.hasPlayer)
		observerWritePlayer(writer, snapshot.player);
	CV_OBSERVER_LITERAL(writer, "]}}}}\n");
#undef CV_OBSERVER_LITERAL
	if (!writer.valid())
		return false;
	message.length = writer.length();
	return true;
}

CvObserverQueue::CvObserverQueue(unsigned int capacity)
: m_capacity(capacity < 1 ? 1 : (capacity > 64 ? 64 : capacity)),
  m_head(0), m_size(0), m_dropped(0), m_closed(false)
{}

bool CvObserverQueue::push(const CvObserverMessage& message)
{
	if (message.length == 0 || message.length > sizeof(message.data))
		return false;
	CvFunctionMutex lock(m_mutex);
	if (m_closed)
		return false;
	if (m_size == m_capacity)
	{
		m_head = (m_head + 1) % m_capacity;
		--m_size;
		++m_dropped;
	}
	m_messages[(m_head + m_size) % m_capacity] = message;
	++m_size;
	return true;
}

bool CvObserverQueue::pop(CvObserverMessage& message)
{
	CvFunctionMutex lock(m_mutex);
	if (m_size == 0)
		return false;
	message = m_messages[m_head];
	m_head = (m_head + 1) % m_capacity;
	--m_size;
	return true;
}

void CvObserverQueue::close()
{
	CvFunctionMutex lock(m_mutex);
	m_closed = true;
	m_size = 0;
}

unsigned int CvObserverQueue::size()
{
	CvFunctionMutex lock(m_mutex);
	return m_size;
}

unsigned long CvObserverQueue::dropped()
{
	CvFunctionMutex lock(m_mutex);
	return m_dropped;
}
// XANA: 2026-11-08 ObserverMCP hierarchical protocol v2 end
#endif
