#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false)
{
    m_bActive = DB.exec("BEGIN;");
}

SQLiteTransaction::~SQLiteTransaction()
{
    if (m_bActive && !m_bCommitted)
    {
        DB.exec("ROLLBACK;");
    }
}

bool SQLiteTransaction::commit() const
{
    if (!m_bActive || m_bCommitted)
	{
		return false;
	}
    if (DB.exec("COMMIT;"))
    {
        m_bActive = false;
        m_bCommitted = true;
        return true;
    }
    return false;
}

bool SQLiteTransaction::rollback() const
{
    if (!m_bActive)
	{
		return false;
	}
    m_bActive = false;
    m_bCommitted = false;
    return DB.exec("ROLLBACK;");
}
