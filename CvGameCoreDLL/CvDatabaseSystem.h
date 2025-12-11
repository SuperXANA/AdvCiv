#pragma once

#include "CvGameCoreDLL.h"
extern "C" { #include "sqlite3.h" }
#include "SQLiteException.h"
#include "SQLiteConnection.h"
#include "SQLiteStatement.h"
#include "SQLiteTransaction.h"
#include "SQLiteResults.h"

#ifndef CV_DATABASE_H
#define CV_DATABASE_H

#define DB() GC.getDatabaseInstance()

class CvDatabaseManager : private boost::noncopyable
{
public:

	CvDatabaseManager();
	SQLiteStatement makeStatement(CvString const& szSQL);
	template <typename DataType>
	DataType query(CvString const& szSQL)
	{
		SQLiteStatement kSQLStatement(szSQL);
		if (kSQLStatement.ready())
		{
			SQLiteResults kResults(kSQLStatement.getStatement()); // TODO: Write SQLiteResults C++ Class
			return kResults.process<DataType>(); // TODO: Write SQLiteResults C++ Class
		}
		else return DataType();
	}
	template <typename DataType>
	std::vector<DataType> execTransaction(std::vector<SQLiteStatement> const& kStatements, bool const bWaitToCommit = false)
	{
		std::vector<DataType> kDataVector;
		SQLiteTransaction kTransaction;
		kTransaction.process(kStatements, kDataVector, bWaitToCommit);
		return kDataVector;
	}
	template <typename DataType>
	stdext::hash_map<CvString, DataType> execTransaction(std::vector<SQLiteStatement> const& kStatements, std::vector<CvString> const& kResultNames, bool const bWaitToCommit = false)
	{
		if (kStatements.size() != kResultNames.size())
		{
			return stdext::hash_map<CvString, DataType>();
		}
		stdext::hash_map<CvString, DataType> kDataMap;
		for (i = 0; i < kResultNames.size(); i++)
		{
			kDataMap[kResultNames[i]] = DataType();
		}
		SQLiteTransaction kTransaction;
		kTransaction.process(kStatements, kDataMap, kResultNames, bWaitToCommit);
		return kDataMap;
	}
	bool ready() const { return m_sqlite ? m_sqlite->ready() : false; }
	sqlite3* getSQLite() { return (ready() == true) ? m_sqlite->getDatabase() : NULL; }

private:
	int exec(CvString const& szSQL)
	{
		int const sqliteReturnCode = sqlite3_exec(getSQLite(), szSQL.c_str(), NULL, NULL, NULL);
		if (sqliteReturnCode != SQLITE_OK)
		{
			log(sqliteReturnCode, "SQLiteTransaction: Failed executing SQL statement on database!");
		}
		return sqliteReturnCode;
	}
	void log(int const iReturnCode, const char* szContext)
    SQLiteConnection* m_sqlite = NULL;
};

#endif