#include "CvGameCoreDLL.h"
#include "SQLiteConnection.h"

SQLiteConnection::SQLiteConnection(const char* szFile) : m_database(NULL), m_bAvailable(false)
{
	int const sqliteReturnCode = sqlite3_open(szFile, &m_database);
	if (sqliteReturnCode != SQLITE_OK)
	{
		DB.log(sqliteReturnCode, "SQLiteConnection: Failed opening database!");
		close();
	}
	else 
	{
		m_bAvailable = true;
		DB.exec("PRAGMA optimize=0x10002;");
	}
}

SQLiteConnection::close()
{
	DB.exec("PRAGMA optimize;");
	m_bAvailable = false;
	sqlite3_close(m_database);
	m_database = NULL;
	if (GC.isLogging())
		gDLL->messageControlLog("SQLiteConnection: The database connection has been closed.");
}