#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

SQLiteConnection::SQLiteConnection(const char* szFilename, bool bReadOnly) : m_database(NULL), m_szFilename(szFilename)
{
	open();
}

SQLiteConnection::~SQLiteConnection()
{
	optimize();
	close();
}

bool SQLiteConnection::open()
{
	if (isValid())
	{
		close();
	}
	int const rc = sqlite3_open_v2(m_szFilename, &m_database);
	return (rc == SQLITE_OK);
}

bool SQLiteConnection::close()
{
	if (isValid())
	{
		sqlite3_stmt* pStatement = NULL;
		while ((pStatement = sqlite3_next_stmt(m_database, NULL)) != NULL)
		{
			sqlite3_finalize(pStatement);
		}
		if ((sqlite3_close_v2(m_database) == SQLITE_OK))
		{
			m_database = NULL;
		}
	}
	return (m_database == NULL);
}
	
bool SQLiteConnection::exec(const char* sql)
{
	if (!isValid() || !sql)
	{
		return false;
	}
	return (sqlite3_exec(m_database, sql, NULL, NULL, NULL) == SQLITE_OK);
}

bool SQLiteConnection::optimize()
{
	return isValid() ? exec("PRAGMA optimize;") : false;
}
