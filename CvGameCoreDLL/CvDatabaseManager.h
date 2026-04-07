#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

class CvDatabaseManager : private boost::noncopyable
friend class SQLiteStatement; // XANA (note): The Statement class is the only one needing access to the sqlite pointer. For safety we will hide the sqlite pointer from the rest of the normal game code.
{
public:
	CvDatabaseManager();
	~CvDatabaseManager();
	
	bool exec(const char* sql);
	bool isValid() const;
	bool init();

private:
	sqlite3* getSQLite();
	SQLiteConnection* m_sqlite;
};
#endif
