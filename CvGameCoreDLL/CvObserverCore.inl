#include "CvObserverCore.h"
#ifdef CV_OBSERVER_ENABLE
#include <stdio.h>
#include <string.h>
#include <limits.h>

// XANA: 2026-11-04 ObserverMCP - protocol v1, bounded value queue
bool CvObserverFormatSnapshot(const char* sessionId, unsigned long snapshotId,
		int gameTurn, CvObserverMessage& message)
{
	memset(&message, 0, sizeof(message));
	if (sessionId == 0 || snapshotId == 0)
		return false;
#if ULONG_MAX > 0xffffffffUL
	if (snapshotId > 0xffffffffUL)
		return false;
#endif
	unsigned int i = 0;
	for (; i <= 64 && sessionId[i] != 0; ++i)
	{
		char c = sessionId[i];
		if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
			(c >= 'A' && c <= 'F')))
			return false;
	}
	if (i == 0 || i > 64)
		return false;
	// Maximum valid record is under 256 bytes; sprintf is bounded by schema.
	int length = sprintf(message.data,
		"{\"protocol\":\"advciv-observer\",\"version\":1,\"type\":\"snapshot\","
		"\"session_id\":\"%s\",\"snapshot_id\":%lu,\"boundary\":\"post_update\","
		"\"game_turn\":%d}\n", sessionId, snapshotId, gameTurn);
	if (length <= 0 || length >= static_cast<int>(sizeof(message.data)))
		return false;
	message.length = static_cast<unsigned int>(length);
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
// XANA: 2026-11-04 ObserverMCP end
#endif
