#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITERESULTS_H
#define CV_SQLITERESULTS_H

class SQLiteStatement;

class SQLiteResults : private boost::noncopyable
{
public:
	SQLiteResults(SQLiteStatement* stmt);
	~SQLiteResults();
	
	bool sqlReady() const;
	bool isValid() const;
	bool exec(); // XANA (note): Use for single queries, when loops aren't needed.
	bool next(); // XANA (note): Use for looping queries, when a while loop is needed.
	
	int getInt(const char* szColName) const;
	float getFloat(const char* szColName) const;
	scaled getScaled(const char* szColName) const;
	bool getBool(const char* szColName) const;
	const char* getText(const char* szColName) const;
	CvString getString(const char* szColName) const;
	bool isNull(const char* szColName) const;
	int getColumnType(const char* szColName) const;
	
private:
	SQLiteStatement* m_statement;
	
	int getColumnIndex(const char* szName) const;
	int getColumnType(int iColumn) const;
	int getInt(int iColumn) const;
	float getFloat(int iColumn) const;
	double getDouble(int iColumn) const;
	bool getBool(int iColumn) const;
	const char* getText(int iColumn) const;
	bool isNull(int iColumn) const;
};
#endif
