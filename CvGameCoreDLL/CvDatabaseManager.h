#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

struct sqlite3;
struct sqlite3_stmt;
class SQLiteConnection;

class CvDatabaseManager : private boost::noncopyable
{
	friend class SQLiteStatement; // XANA (note): The Statement class is the only one needing access to the sqlite pointer. For safety we will hide the sqlite pointer from the rest of the normal game code.
public:
	CvDatabaseManager();
	~CvDatabaseManager();
	
	bool exec(const CvString& szSQL);
	bool isValid() const;
	bool init();

private:
	sqlite3_stmt* prepareStatementFromCache(const CvString& szKey, const CvString& szSQL);
	void returnStatementToCache(const CvString& szKey, sqlite3_stmt* pStatement);
	void clearStatementPool();
	
	sqlite3_stmt* prepareStatementFromCache(const std::string& key, const std::string& sql)
	{
		return prepareStatementFromCache(CvString(key), CvString(sql));
	}
	sqlite3_stmt* prepareStatementFromCache(const char* key, const char* sql)
	{
		return prepareStatementFromCache(CvString(key), CvString(sql));
	}
	void returnStatementToCache(const std::string& key, sqlite3_stmt* pStatement)
	{
		returnStatementToCache(CvString(key), pStatement);
	}
	void returnStatementToCache(const char* key, sqlite3_stmt* pStatement)
	{
		returnStatementToCache(CvString(key), pStatement);
	}
	bool prepare(sqlite3_stmt* pStatement, const CvString& szSQL);
	typedef stdext::hash_map<std::string, std::vector<sqlite3_stmt*> > StatementPool;
	StatementPool m_statementPool;
	SQLiteConnection* m_sqlite;
};
#endif
