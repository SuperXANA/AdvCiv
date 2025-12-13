#pragma once

#include "CvGameCoreDLL.h"
extern "C" { #include "sqlite3.h" }
class SQLiteStatement;

class SQLiteTransaction : private boost::noncopyable
{
public:
	SQLiteTransaction();
	~SQLiteTransaction();
	bool ready() { return m_bProcessing; }
	template <typename DataType>
	bool process(std::vector<SQLiteStatement>& statementVector, std::vector<DataType>& resultVector, bool const bWaitToCommit = false)
	{
		bool bOk = false;
		int iErrorCount = 0;
		if (ready())
		{
			for (i = 0; i < statementVector.size(); i++)
			{
				SQLiteStatement& kSQLStatement = statementVector[i];
				if (kSQLStatement.ready())
				{
					SQLiteResults kResults(kSQLStatement.getStatement()); // TODO: Write SQLiteResults C++ Class
					if (kResults.process(resultVector) == false) // TODO: Write SQLiteResults C++ Class
						iErrorCount++;
					kSQLStatement.reset();
				}
				else
				{
					kSQLStatement.reset();
					iErrorCount++;
				}
			}
			if (iErrorCount == 0)
			{
				bOk = (!bWaitToCommit) ? commit() : true;
			}
		}
		return bOk;
	}
	template <typename DataType>
	bool process(std::vector<SQLiteStatement>& statementVector, stdext::hash_map<CvString, DataType>& resultMap, std::vector<CvString> const& idVector, bool const bWaitToCommit = false)
	{
		bool bOk = false;
		int iErrorCount = 0;
		if (ready())
		{
			for (i = 0; i < statementVector.size(); i++)
			{
				SQLiteStatement& kSQLStatement = statementVector[i];
				if (kSQLStatement.ready())
				{
					SQLiteResults kResults(kSQLStatement.getStatement()); // TODO: Write SQLiteResults C++ Class
					if (kResults.process(resultMap) == false) // TODO: Write SQLiteResults C++ Class
						iErrorCount++;
					kSQLStatement.reset();
				}
				else
				{
					kSQLStatement.reset();
					iErrorCount++;
				}
			}
			if (iErrorCount == 0)
			{
				bOk = (!bWaitToCommit) ? commit() : true;
			}
		}
		return bOk;
	}
	bool commit();
	bool rollback();
private:
	bool m_bProcessing;
};