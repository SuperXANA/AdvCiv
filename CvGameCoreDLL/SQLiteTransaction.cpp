#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false)
{
    m_bActive = (sqlReady() ? GC.getDatabaseInstance()->exec("BEGIN;") : false);
}

SQLiteTransaction::~SQLiteTransaction()
{
    rollback();
}

bool SQLiteTransaction::sqlReady() const
{
	return (GC.getDatabaseInstance() != NULL);
}

bool SQLiteTransaction::commit()
{
    if (!isValid())
	{
		return true;
	}
    if (sqlReady() && GC.getDatabaseInstance()->exec("COMMIT;"))
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
		return (sqlReady() && GC.getDatabaseInstance()->exec("ROLLBACK;"));
	}
	return false;
}
