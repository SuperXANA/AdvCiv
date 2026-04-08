#pragma once

#include "CvGameCoreDLL.h"
#include "SQLiteResults.h"

#ifndef CV_SQLITESTATEMENT_H
#define CV_SQLITESTATEMENT_H

struct sqlite3_stmt;
class CvDatabaseManager;

class SQLiteStatement : private boost::noncopyable
{
public:
	SQLiteStatement();
	SQLiteStatement(const CvString& szSQL);
	SQLiteStatement(const std::string& sql);
	~SQLiteStatement();
	
	bool isValid(bool bCheckDatabaseConnection = true) const;
	bool isPrepared() const { return isValid() && m_bPrepared; }
	bool hasRow() const { return isPrepared() && m_bHasRow; }
	
	bool prepare(const CvString& szSQL);
	bool prepare(const std::string& sql);
	bool mapColumns();
	int getColumnIndex(const char* szName) const;

	bool reset();
	bool finalize();
	bool clearBindings();

	bool bind(const char* szParam, int iValue);
	bool bind(const char* szParam, float fValue);
	bool bind(const char* szParam, double dValue);
	bool bind(const char* szParam, scaled rValue);
	bool bind(const char* szParam, const char* szValue, bool bCopy = true);
	bool bind(const char* szParam, const std::string& szValue);
	bool bind(const char* szParam, const CvString& szValue);
	bool bindNull(const char* szParam);
	bool hasBinding(const char* szParam) const;

	bool exec();
	void setPrepared(bool b) { m_bPrepared = b; }
	SQLiteResults& getResults();
	
	int getColumnType(int iColumn) const;
	int getInt(int iColumn) const;
	float getFloat(int iColumn) const;
	double getDouble(int iColumn) const;
	bool getBool(int iColumn) const;
	CvString getText(int iColumn) const;
	bool isNull(int iColumn) const;

private:
	CvString m_szSQL;
	sqlite3_stmt* m_statement;
	bool m_bHasRow;
	typedef stdext::hash_map<std::string, int> ColumnsMap;
	ColumnsMap m_columnsMap;
	bool m_bMappedColumns;
	bool m_bFinalized;
	bool m_bPrepared;
	SQLiteResults m_resultCursor;
	
	bool step();
	
	int getColumnCount() const;
	bool bind(int index, int iValue);
	bool bind(int index, float fValue);
	bool bind(int index, double dValue);
	bool bind(int index, scaled rValue);
	bool bind(int index, const char* szValue, bool bCopy = true);
	bool bind(int index, const std::string& szValue);
	bool bind(int index, const CvString& szValue);
	bool bindNull(int index);
	int getParameterIndex(const char* szName) const;
	const char* getColumnName(int col) const;
};
#endif

