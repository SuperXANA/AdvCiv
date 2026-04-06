#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITECONNECTION_H
#define CV_SQLITECONNECTION_H

struct sqlite3;
struct sqlite3_stmt;

class SQLiteConnection : private boost::noncopyable
friend class CvDatabaseManager; // XANA (note): This class is only managed by the Database Manager and is hidden from normal game code, no other class should be creating or deleting sqlite database pointers
{
private:
	SQLiteConnection(const char* szFilename)
	~SQLiteConnection()
	sqlite3* m_database;
	const char* m_szFilename;
	bool open();
	bool close();
	bool isValid() const;
	sqlite3* getDatabase();
	bool exec(const char* sql);
};
#endif
