#pragma once

#include "CvGameCoreDLL.h"
#include "CvDatabaseFwd.h"

#ifndef CV_SQLITERESULTS_H
#define CV_SQLITERESULTS_H

class SQLiteStatement;

class SQLiteResults : private boost::noncopyable
{
public:
	SQLiteResults(SQLiteStatement& stmt);
	
	bool next();
	
	int getInt(const char* szColName) const;
	scaled getFloat(const char* szColName) const;
	scaled getScaled(const char* szColName) const;
	bool getBool(const char* szColName) const;
	CvString getString(const char* szColName) const;
	bool isNull(const char* szColName) const;
	int getColumnType(const char* szColName) const;
	
private:
	SQLiteStatement& m_statement;
	bool m_bValid;
	
	int getColumnIndex(const char* szName) const;
	int getColumnType(int iColumn) const;
	int getInt(int iColumn) const;
	scaled getFloat(int iColumn) const;
	double getDouble(int iColumn) const;
	scaled getScaled(int iColumn) const;
	bool getBool(int iColumn) const;
	const char* getText(int iColumn) const;
	CvString getString(int iColumn) const;
	bool isNull(int iColumn) const;
};
#endif
