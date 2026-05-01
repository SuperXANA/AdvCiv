#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false)
{
    m_bActive = begin();
}

SQLiteTransaction::~SQLiteTransaction()
{
    rollback();
}

bool SQLiteTransaction::begin()
{
    if (isValid() || DB.exec("BEGIN;"))
    {
        return true;
    }
    return false;
}

bool SQLiteTransaction::commit()
{
    if (!isValid())
	{
		return true;
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
		m_bActive = false;
		m_bCommitted = false;
		return (DB.exec("ROLLBACK;"));
	}
	return false;
}
