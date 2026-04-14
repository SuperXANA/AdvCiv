#include "CvBugOptions.h"
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

bool CvDatabaseManager::exec(const CvString& szSQL)
{
	if (!isValid() || !szSQL.GetCString())
	{
		return false;
	}
	return m_sqlite->exec(szSQL);
}

bool CvDatabaseManager::isValid() const
{
	return (m_sqlite ? m_sqlite->isValid() : false);
}

bool CvDatabaseManager::init()
{
	if (m_sqlite == NULL)
	{
		CvString szDatabasePath(BUGOption::userDirPath());
		if (!szDatabasePath.empty()) // XANA (note): If we successfully found the user's valid, writable My Documents folder (path not empty)
		{
			szDatabasePath += "\\Beyond the Sword\\"; // XANA (note): We'll put the game database inside the main BtS folder to keep it nominally safe from modification or deletion
			szDatabasePath += "CvGameDatabase.sqlite"; // XANA (note): If the file somehow gets removed, that's fine for Civ4, it won't affect actual gameplay much since the game doesn't depend on SQL to function
		}
		else return false; // XANA (note): Can't save a database file in an invalid, empty location, so we won't initialize at all
		m_sqlite = new SQLiteConnection(szDatabasePath); 
	}
	return isValid();
}