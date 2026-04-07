#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL)
{}

CvDatabaseManager::~CvDatabaseManager()
{
	SAFE_DELETE(m_sqlite);
}

sqlite3* CvDatabaseManager::getSQLite()
{
	return (isValid() ? m_sqlite->getDatabase() : NULL);
}

bool CvDatabaseManager::exec(const CvString& szSQL))
{
	return exec(szSQL.GetCString());
}

bool CvDatabaseManager::exec(const char* sql)
{
	if (!isValid() || !sql)
	{
		return false;
	}
	return m_sqlite->exec(sql);
}

bool CvDatabaseManager::isValid() const
{
	return (m_sqlite ? m_sqlite->isValid() : false);
}

bool CvDatabaseManager::init()
{
	if (m_sqlite == NULL)
	{
		m_sqlite = new SQLiteConnection(GC.getModName().getFullPath() + "Assets\CvGameDatabase.sqlite");
	}
	return isValid();
}