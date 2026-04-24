#include "CvDatabaseManager.h"
#include "SQLiteTransaction.h"

#undef GC // XANA (note): The const version of the GC instance isn't useful here, just like in the CvXMLLoadUtility class, we need to override it for this implementation to work properly
#define GC CvGlobals::getInstance()

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
    if (isValid() || GC.getDatabaseInstance().exec("BEGIN;"))
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
		return (GC.getDatabaseInstance().exec("ROLLBACK;"));
	}
	return false;
}
