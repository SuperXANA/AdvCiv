#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction()
    : m_bActive(false), m_bCommitted(false)
{
    m_bActive = GC.getDatabaseInstance().exec("BEGIN;");
}

SQLiteTransaction::~SQLiteTransaction()
{
    rollback();
}

bool SQLiteTransaction::commit()
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

bool SQLiteTransaction::rollback()
{
    if (isValid())
    {
		m_bActive = false;
		m_bCommitted = false;
		return GC.getDatabaseInstance().exec("ROLLBACK;");
	}
	return false;
}
