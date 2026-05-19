#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"

SQLiteConnection::SQLiteConnection(const CvWString& szFilename) : m_database(NULL), m_szFilename(szFilename)
{}

SQLiteConnection::~SQLiteConnection()
{}

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
		m_database = NULL;
	}
	return false;
}

bool SQLiteConnection::close()
{
	if (finalizeAllStatements())
	{
		if (sqlite3_close(m_database) == SQLITE_OK)
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
	return (sqlite3_prepare_v2(m_database, szSQL.GetCString(), ((int)szSQL.GetLength() + 1) /* XANA (note): automatically calculates extra length to include the NULL terminator, since we know how long the string is */, &kStatement, NULL) == SQLITE_OK);
}

bool SQLiteConnection::finalizeAllStatements()
{
	if (!isValid())
	{
		return false;
	}
	sqlite3_stmt* pStatement = NULL;
	while ((pStatement = sqlite3_next_stmt(m_database, NULL)) != NULL)
	{
		sqlite3_finalize(pStatement);
		pStatement = NULL;
	}
	return true;
}