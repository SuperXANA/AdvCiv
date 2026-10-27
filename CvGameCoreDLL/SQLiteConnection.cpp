#include "CvGameCoreDLL.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

SQLiteConnection::SQLiteConnection(const CvWString& szFilename) : m_database(NULL), m_szFilename(szFilename)
{}

SQLiteConnection::~SQLiteConnection()
{
	close();
}

bool SQLiteConnection::open()
{
	if (isValid())
	{
		return true;
	}
	if (sqlite3_open16(m_szFilename.GetCString(), &m_database) == SQLITE_OK)
	{
		return true;
	}
	else
	{
		// sqlite3_open16 can return a handle even on failure.
		if (m_database != NULL)
			sqlite3_close(m_database);
		m_database = NULL;
	}
	return false;
}

bool SQLiteConnection::close()
{
	if (m_database == NULL)
		return true;
	// XANA: 10-27-2026 Do not finalize statements still owned by callers.
	// SQLITE_BUSY preserves the handle so shutdown can be retried safely.
	if (sqlite3_close(m_database) != SQLITE_OK)
		return false;
	m_database = NULL;
	return true;
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
	return (sqlite3_prepare_v2(m_database, szSQL.GetCString(), ((int)szSQL.GetLength() + 1) /* XANA (note): automatically calculates extra length to include the NULL terminator, since we know how long the string is */, &kStatement, NULL) == SQLITE_OK);
}
