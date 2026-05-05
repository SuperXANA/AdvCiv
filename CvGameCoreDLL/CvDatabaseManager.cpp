#include "CvBugOptions.h"
#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL): m_doCache(false)
{}

CvDatabaseManager::~CvDatabaseManager()
{
	m_doCache = false;
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
			if (!m_doCache)
			{
				m_doCache = true;
			}
		}
		else return false; // XANA (note): Can't save a database file in an invalid, empty location, so we won't initialize at all
		m_sqlite = new SQLiteConnection(szDatabasePath);
	}
	return isValid();
}

sqlite3_stmt* CvDatabaseManager::prepareStatementFromCache(const CvString& szKey, const CvString& szSQL)
{
	if (!isValid() || !szKey.GetCString())
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
	We'll get a new statement ready now, using the query text for szSQL, and the caller will automatically add it back to the cache once it's finished processing. */
	sqlite3_stmt* pStatement = NULL;
	if (prepare(pStatement, szSQL))
	{
		return pStatement;
	}
	return NULL;
}

void CvDatabaseManager::returnStatementToCache(const CvString& szKey, sqlite3_stmt*& kStatement)
{
	if (!kStatement) // XANA (note): Don't push NULL pointers to the cache, just return to keep things operating normally
	{
		return;
	}
	if (isValid() && m_doCache && szKey.GetCString())
	{
		sqlite3_reset(kStatement);
		sqlite3_clear_bindings(kStatement);
		m_statementPool[szKey].push_back(kStatement);
	}
	// XANA (note): If the database isn't ready, for example when the game shutdown process has started, or if we aren't in a position to perform caching, we shouldn't keep anything to save on memory space.
	else
	{
		sqlite3_finalize(kStatement);
	}
	kStatement = NULL; // XANA (note): Clear the caller's statement pointer that it was holding, since we have taken ownership of it in the cache or deleted it if the game is closing, to guard against problems with the game memory
}

void CvDatabaseManager::clearStatementPool()
{
	for (StatementPool::iterator it = m_statementPool.begin(); it != m_statementPool.end(); ++it)
	{
		std::vector<sqlite3_stmt*>& vPool = it->second;
		for (int j = 0; j < (int)vPool.size(); ++j)
		{
			if (vPool[j] != NULL)
			{
				sqlite3_finalize(vPool[j]);
				vPool[j] = NULL;
			}
		}
		vPool.clear();
	}
	m_statementPool.clear();
}

bool CvDatabaseManager::prepare(sqlite3_stmt*& kStatement, const CvString& szSQL)
{
	if (!isValid() || !szSQL.GetCString())
	{
		return false;
	}
	return m_sqlite->prepare(kStatement, szSQL);
}