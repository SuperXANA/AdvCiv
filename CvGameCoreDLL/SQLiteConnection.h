#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITECONNECTION_H
#define CV_SQLITECONNECTION_H

struct sqlite3;
struct sqlite3_stmt;

class SQLiteConnection : private boost::noncopyable
{
	friend class CvDatabaseManager; // XANA (note): This class is only managed by the Database Manager and is hidden from normal game code, no other class should be creating or deleting sqlite database pointers
private:
	SQLiteConnection(const CvString& szFilename);
	~SQLiteConnection();
	sqlite3* m_database;
	CvString m_szFilename;
	bool open();
	bool close();
	bool isValid() const;
	bool exec(const CvString& szSQL);
	bool prepare(sqlite3_stmt*& kStatement, const CvString& szSQL);
	bool finalizeAllStatements();
};
#endif
