#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

struct sqlite3;

class SQLiteConnection;

class CvDatabaseManager : private boost::noncopyable
friend class SQLiteStatement; // XANA (note): Statement class is the only one needing access to the pointer. Better hide the sqlite pointer from the rest of the prepared game code.
{
public:

	CvDatabaseManager();
	~CvDatabaseManager();
	
	bool exec(const char* sql)
	{
		if (!m_sqlite || !sql) return false;
		return sqlite3_exec(getSQLite(), sql, NULL, NULL, NULL) == SQLITE_OK;
	}
	bool exec(const CvString& szSQL) { return exec(szSQL.c_str()); }
	
	CvString getErrorMsg() const;
	int getErrorCode() const;

private:
	sqlite3* getSQLite();
	
	const char* getErrorInfo() const
	{
		if (!m_sqlite)
		{
			return "Database not open";
		}
		return sqlite3_errmsg(getSQLite());
	}
	
    SQLiteConnection* m_sqlite = NULL;
};
#endif
