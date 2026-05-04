#include "CvBugOptions.h"
#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL)
{}

CvDatabaseManager::~CvDatabaseManager()
{
	clearStatementPool();
	SAFE_DELETE(m_sqlite);
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
		/* XANA (note): For network games, we must ensure that the sqlite3 database will be kept in sync between the players or there will be out-of-sync errors. */
		CvString szDatabasePath(BUGOption::userDirPath());
		if (!szDatabasePath.empty()) // XANA (note): If we successfully found the user's valid, writable My Documents folder (path not empty)
		{
			szDatabasePath += "\\Beyond the Sword\\"; // XANA (note): We'll put the game database inside the main BtS folder to keep it nominally safe from modification or deletion
			szDatabasePath += "CvGameDatabase"; // XANA (note): If the file somehow gets removed, that's fine for Civ4, it won't affect actual gameplay much since the game doesn't depend on SQL to function
			if (GC.getGame().isNetworkMultiPlayer())
			{
				szDatabasePath += ("-MP_" + CvString(GC.getGame().getName()));
			}
			szDatabasePath += ".sqlite"
		}
		else return false; // XANA (note): Can't save a database file in an invalid, empty location, so we won't initialize at all
		m_sqlite = new SQLiteConnection(szDatabasePath);
	}
	return isValid();
}

sqlite3_stmt* CvDatabaseManager::prepareStatementFromCache(const CvString& szKey, const CvString& szSQL)
{
	if (!szKey.GetCString() || !szSQL.GetCString())
	{
		return NULL;
	}
	std::vector<sqlite3_stmt*>& vPool = m_statementPool[szKey];
	// XANA (note): If we have cached a statement like this before, meaning the vector pool wasn't empty, give what we found back to the caller now so it can be processed immediately.
	if (!vPool.empty())
	{
		sqlite3_stmt* pStatement = vPool.back();
		vPool.pop_back();
		return pStatement;
	}
	/* XANA (note): If we fell through when checking against szKey's vector storage, there's clearly nothing to use here from our memory.
	We'll get a new statement ready now, using szSQL's text data, and the caller will automatically add it back to the cache once it's finished processing. */
	sqlite3_stmt* pStatement = NULL;
	if (prepare(pStatement, szSQL))
	{
		return pStatement;
	}
	return NULL;
}

void CvDatabaseManager::returnStatementToCache(const CvString& szKey, sqlite3_stmt* pStatement)
{
	if (pStatement != NULL)
	{
		if (isValid())
		{
			sqlite3_reset(pStatement);
			sqlite3_clear_bindings(pStatement);
			m_statementPool[szKey].push_back(pStatement);
		}
		// XANA (note): If the database isn't ready, for example when the game shutdown process has started, we shouldn't cache anything because the pointer will be invalidated once the game has closed.
		else
		{
			sqlite3_finalize(pStatement);
			pStatement = NULL;
		}
	}
}

void CvDatabaseManager::clearStatementPool()
{
	StatementPool::iterator poolIter = m_statementPool.begin();
	while (poolIter != m_statementPool.end())
	{
		std::vector<sqlite3_stmt*>& vPool = poolIter->second;
		for (int iHandle = 0; iHandle < (int)vPool.size(); ++iHandle)
		{
			if (vPool[iHandle] != NULL)
			{
				sqlite3_finalize(vPool[iHandle]);
				vPool[iHandle] = NULL;
			}
		}
		vPool.clear();
		++poolIter;
	}
	m_statementPool.clear();
}

bool CvDatabaseManager::prepare(sqlite3_stmt* pStatement, const CvString& szSQL) const
{
	if (!isValid() || !szSQL.GetCString() || !(pStatement == NULL))
	{
		return false;
	}
	return m_sqlite->prepare(pStatement, szSQL);
}