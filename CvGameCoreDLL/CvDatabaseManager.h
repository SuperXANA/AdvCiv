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
	
	void init();
	bool optimize();
	bool exec(const char* sql);
	bool isValid() const;

private:
	sqlite3* getSQLite();
	SQLiteConnection* m_sqlite;
};
#endif
