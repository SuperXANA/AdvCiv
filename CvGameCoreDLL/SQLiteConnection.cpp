#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"

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
	close();
	int rc = sqlite3_open(szFilename, &m_database);
	return (rc == SQLITE_OK);
}

void SQLiteConnection::close()
{
	if (m_database)
	{
		sqlite3_close(m_database);
		m_database = NULL;
	}
}

bool SQLiteConnection::optimize()
{
	return GC.getDatabaseInstance().exec("PRAGMA optimize;");
}
