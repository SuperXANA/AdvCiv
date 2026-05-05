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
	return (sqlite3_open_v2(m_szFilename.GetCString(), &m_database, (SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE), NULL) == SQLITE_OK);
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

bool SQLiteConnection::exec(const CvString& szSQL)
{
	return (sqlite3_exec(m_database, szSQL.GetCString(), NULL, NULL, NULL) == SQLITE_OK);
}

bool SQLiteConnection::prepare(sqlite3_stmt*& kStatement, const CvString& szSQL)
{
	return (sqlite3_prepare_v2(m_database, szSQL.GetCString(), -1, &kStatement, NULL) == SQLITE_OK);
}
