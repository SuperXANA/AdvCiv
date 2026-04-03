#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

class SQLiteConnection;

class CvDatabaseManager : private boost::noncopyable
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
	
	sqlite3* getSQLite();
	
	CvString getErrorMsg() const;
	int getErrorCode() const;

private:
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
