#pragma once

#include "CvGameCoreDLL.h"
class SQLiteConnection : private boost::noncopyable
{
public:
	SQLiteConnection();
	explicit SQLiteConnection(const char* szFilename);
	~SQLiteConnection();

	bool open(const char* szFilename);
	void close();
	bool isOpen() const
	{
		return (m_database != NULL);
	}
	sqlite3* getDatabase() { return isOpen() ? m_database : NULL; }

private:
	sqlite3* m_database;
	bool optimize();
};