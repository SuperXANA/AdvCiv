#include "CvDatabaseManager.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(GC.getModName().getFullPath() + "Assets\CvGameDatabase.sqlite")
{}

sqlite3* CvDatabaseManager::getSQLite()
{
	return isValid() ? m_sqlite.getDatabase() : NULL;
}

bool CvDatabaseManager::exec(const char* sql)
{
	if (!isValid() || !sql)
	{
		return false;
	}
	return m_sqlite.exec(sql);
}

bool CvDatabaseManager::isValid() const
{
	return m_sqlite.isValid();
}