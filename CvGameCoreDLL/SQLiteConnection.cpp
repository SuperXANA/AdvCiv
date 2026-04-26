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
	if (!bReopen && isValid())
	{
		return true;
	}
	else if (bReopen && isValid())
	{
		close();
	}
	int const rc = sqlite3_open_v2(m_szFilename.GetCString(), &m_database, (SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE), NULL);
	return (rc == SQLITE_OK);
}

bool SQLiteConnection::close()
{
	if (isValid())
	{
		if ((sqlite3_close(m_database) == SQLITE_OK))
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
