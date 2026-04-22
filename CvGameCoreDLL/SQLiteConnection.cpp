#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

SQLiteConnection::SQLiteConnection(const CvString& szFilename) : m_database(NULL), m_szFilename(szFilename)
{
	open();
}

SQLiteConnection::~SQLiteConnection()
{
	close();
}

bool SQLiteConnection::open(bool bReopen)
{
	if (isValid() && !bReopen)
	{
		return true;
	}
	else if (isValid() && bReopen)
	{
		close();
	}
	int const rc = sqlite3_open_v2(m_szFilename.GetCString(), &m_database);
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

bool SQLiteConnection::isValid() const
{
	return (m_database != NULL);
}

sqlite3* SQLiteConnection::getDatabase()
{
	return m_database ? m_database : NULL;
}

bool SQLiteConnection::exec(const CvString& szSQL)
{
	return (sqlite3_exec(m_database, szSQL.GetCString(), NULL, NULL, NULL) == SQLITE_OK);
}
