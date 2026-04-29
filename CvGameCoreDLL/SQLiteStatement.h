#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITESTATEMENT_H
#define CV_SQLITESTATEMENT_H

struct sqlite3_stmt;
class CvDatabaseManager;
class SQLiteValue;

class SQLiteStatement : private boost::noncopyable
{
public:
	SQLiteStatement();
	SQLiteStatement(const CvString& szSQL);
	SQLiteStatement(const std::string& sql);
	~SQLiteStatement();
	
	bool isValid(bool bCheckDatabaseConnection = true) const;
	bool isPrepared() const { return isValid() && m_bPrepared; }
	bool hasRow(int iColumn) const { return isPrepared() && m_bHasRow && (iColumn >= 0); }
	
	bool prepare(const CvString& szSQL);
	bool prepare(const std::string& sql);
	
	bool exec(); // XANA (note): Use for single queries, when loops aren't needed.
	bool next(); // XANA (note): Use for looping queries, when a while loop is needed.
	
	SQLiteValue getValue(const char* szColName) const; // XANA (note): Use when you don't know the type of data stored in the database column, it converts stored column information into a supported type automatically.
	
	int getInt(const char* szColName) const;
	float getFloat(const char* szColName) const;
	double getDouble(const char* szColName) const;
	scaled getScaled(const char* szColName) const;
	bool getBool(const char* szColName) const;
	CvString getText(const char* szColName) const;
	bool isNull(const char* szColName) const;
	
	bool mapColumns();

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
	bool bind(const char* szParam, bool bValue);
	bool bindNull(const char* szParam);
	bool hasBinding(const char* szParam) const;

	void setPrepared(bool b) { m_bPrepared = b; }

private:
	CvString m_szSQL;
	mutable sqlite3_stmt* m_statement;
	bool m_bHasRow;
	typedef stdext::hash_map<std::string, int> ColumnsMap;
	ColumnsMap m_columnsMap;
	bool m_bMappedColumns;
	bool m_bFinalized;
	bool m_bPrepared;
	
	bool step(bool bLooping = true);
	int getColumnCount() const;
	bool bind(int index, int iValue);
	bool bind(int index, float fValue);
	bool bind(int index, double dValue);
	bool bind(int index, scaled rValue);
	bool bind(int index, const char* szValue, bool bCopy = true);
	bool bind(int index, const std::string& szValue);
	bool bind(int index, const CvString& szValue);
	bool bind(int index, bool bValue);
	bool bindNull(int index);
	int getParameterIndex(const char* szName) const;
	const char* getColumnName(int col) const;
	
	int getColumnType(const char* szColName) const;
	int getColumnType(int iColumn) const;
	int getColumnIndex(const char* szName) const;
	
	int getInt(int iColumn) const;
	float getFloat(int iColumn) const;
	double getDouble(int iColumn) const;
	bool getBool(int iColumn) const;
	CvString getText(int iColumn) const;
	bool isNull(int iColumn) const;
};

#endif

