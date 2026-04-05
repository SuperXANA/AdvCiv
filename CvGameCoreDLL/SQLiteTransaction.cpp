#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false)
{
    m_bActive = GC.getDatabaseInstance().exec("BEGIN;");
}

SQLiteTransaction::~SQLiteTransaction()
{
    if (isValid())
    {
        GC.getDatabaseInstance().exec("ROLLBACK;");
    }
}

bool SQLiteTransaction::commit() const
{
    if (!isValid())
	{
		return true;
	}
    if (GC.getDatabaseInstance().exec("COMMIT;"))
    {
        m_bActive = false;
        m_bCommitted = true;
        return true;
    }
    return false;
}

bool SQLiteTransaction::rollback() const
{
    m_bActive = false;
    m_bCommitted = false;
    return GC.getDatabaseInstance().exec("ROLLBACK;");
}
