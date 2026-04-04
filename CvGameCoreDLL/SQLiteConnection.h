#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITECONNECTION_H
#define CV_SQLITECONNECTION_H

struct sqlite3;

class SQLiteConnection : private boost::noncopyable
{
public:
	SQLiteConnection();
	explicit SQLiteConnection(const char* szFilename);
	~SQLiteConnection();

	bool open(const char* szFilename);
	bool close();
	bool isOpen() const
	{
		return (m_database != NULL);
	}
	sqlite3* getDatabase() { return isOpen() ? m_database : NULL; }

private:
	sqlite3* m_database;
	bool optimize();
};
#endif
