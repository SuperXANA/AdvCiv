#pragma once

#include "CvGameCoreDLL.h"
#include "SQLiteConnection.h"
#include "SQLiteStatement.h"
#include "SQLiteTransaction.h"
#include "SQLiteResults.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

#define DB() GC.getDatabaseInstance()

class CvDatabaseManager : private boost::noncopyable
{
public:

	CvDatabaseManager();
	~CvDatabaseManager();
	
	int exec(const char* sql)
	{
		if (!m_sqlite || !sql) return false;
		return sqlite3_exec(getSQLite(), sql, NULL, NULL, NULL) == SQLITE_OK;
	}
	int exec(const CvString& szSQL) { exec(szSQL.c_str()); }
	
	CvString getErrorMsg() const;
	int getErrorCode() const;

private:
	sqlite3* getSQLite() { return m_sqlite ? m_sqlite->getDatabase() : NULL; }
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