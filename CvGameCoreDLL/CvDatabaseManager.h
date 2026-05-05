#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

struct sqlite3;
struct sqlite3_stmt;
class SQLiteConnection;

class CvDatabaseManager : private boost::noncopyable
{
	friend class SQLiteStatement; // XANA (note): The Statement class is the only one needing access to the sqlite pointer cache. For safety we will hide the cache from the rest of the normal game code.
public:
	CvDatabaseManager();
	~CvDatabaseManager();
	
	bool exec(const CvString& szSQL);
	bool isValid() const;
	bool init();
	
private:
	sqlite3_stmt* prepareStatementFromCache(const CvString& szKey, const CvString& szSQL);
	void returnStatementToCache(const CvString& szKey, sqlite3_stmt*& kStatement);
	void clearStatementPool();
	bool prepare(sqlite3_stmt*& kStatement, const CvString& szSQL);
	
	typedef stdext::hash_map<std::string, std::vector<sqlite3_stmt*> > StatementPool;
	StatementPool m_statementPool;
	
	SQLiteConnection* m_sqlite;
	bool m_doCache;
};
#endif
