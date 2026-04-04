#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

SQLiteConnection::SQLiteConnection() : m_database(NULL) {}

SQLiteConnection::SQLiteConnection(const char* szFilename) : m_database(NULL)
{
	open(szFilename);
}

SQLiteConnection::~SQLiteConnection()
{
	optimize();
	close();
}

bool SQLiteConnection::open(const char* szFilename)
{
	if (m_database)
	{
		close();
	}
	int const rc = sqlite3_open_v2(szFilename, &m_database);
	return (rc == SQLITE_OK);
}

bool SQLiteConnection::close()
{
	if (m_database)
	{
		sqlite3_stmt* pStatement = NULL;
		while ((pStatement = sqlite3_next_stmt(m_database, NULL)) != NULL)
		{
			sqlite3_finalize(pStatement);
		}
		return (sqlite3_close_v2(m_database) == SQLITE_OK);
	}
	return true;
}

bool SQLiteConnection::optimize()
{
	return GC.getDatabaseInstance().exec("PRAGMA optimize;");
}
