#include "CvGameCoreDLL.h"
#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false), m_iTransactionGeneration(0)
{
    m_bActive = begin();
}

SQLiteTransaction::~SQLiteTransaction()
{
    rollback();
}

bool SQLiteTransaction::begin()
{
	if (isValid())
		return true;
	// XANA: 10-27-2026 A new attempt must not inherit a prior commit result.
	m_bActive = false;
	m_bCommitted = false;
	if (!DB.exec("BEGIN;"))
		return false;
	m_iTransactionGeneration = DB.getTransactionGeneration();
	m_bActive = true;
	// XANA: END transaction ownership capture.
	return true;
}

bool SQLiteTransaction::commit()
{
    if (!isValid())
	{
		return wasCommitted();
	}
    if (DB.exec("COMMIT;"))
    {
        m_bActive = false;
        m_bCommitted = true;
        return true;
    }
    return false;
}

bool SQLiteTransaction::rollback()
{
    if (isValid())
    {
    	if (DB.exec("ROLLBACK;"))
    	{
			m_bActive = false;
			m_bCommitted = false;
			return true;
		}
	}
	return false;
}

// XANA: 10-27-2026 An implicit rollback or a connection reset ends ownership.
// A stale wrapper must not commit or roll back a later caller's transaction.
bool SQLiteTransaction::isActive() const
{
    return m_bActive && DB.isTransactionCurrent(m_iTransactionGeneration);
}
// XANA: END transaction ownership validation.
