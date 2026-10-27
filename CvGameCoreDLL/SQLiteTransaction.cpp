#include "CvGameCoreDLL.h"
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
	if (isValid())
		return true;
	if (!DB.exec("BEGIN;"))
		return false;
	m_bActive = true;
	m_bCommitted = false;
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
