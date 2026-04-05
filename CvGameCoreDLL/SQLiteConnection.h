#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITECONNECTION_H
#define CV_SQLITECONNECTION_H

struct sqlite3;
struct sqlite3_stmt;

class SQLiteConnection : private boost::noncopyable
{
public:
	SQLiteConnection(const char* szFilename);
	~SQLiteConnection();

	bool open();
	bool close();
	bool isValid() const { return (m_database != NULL); }
	sqlite3* getDatabase() { return isValid() ? m_database : NULL; }
	
	bool exec(const char* sql);

private:
	sqlite3* m_database;
	const char* m_szFilename;
	bool optimize();
};
#endif
