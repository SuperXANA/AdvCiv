#pragma once

#include "CvGameCoreDLL.h"
extern "C" { #include "sqlite3.h" }


class SQLiteConnection : private boost::noncopyable
{
public:
	SQLiteConnection(CvString const& szFile);
	~SQLiteConnection() { close(); }
	sqlite3* getDatabase() const { return m_database; }
	void close();
	bool ready() const { return m_database != NULL && m_bAvailable; }
private:
	sqlite3* m_database;
	bool m_bAvailable;
};