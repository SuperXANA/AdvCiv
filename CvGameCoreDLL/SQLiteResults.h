#pragma once

#include "CvGameCoreDLL.h"
#include "CvDatabaseFwd.h"

#ifndef CV_SQLITERESULTS_H
#define CV_SQLITERESULTS_H

class SQLiteStatement;

class SQLiteResults : private boost::noncopyable
{
public:
	explicit SQLiteResults(SQLiteStatement& stmt);
	
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
	
	int getColumnIndex(const char* szName) const
	{
		if (!m_statement)
		{
			return -1;
		}
		return m_statement.getColumnIndex(szName);
	}
	int getColumnType(int iColumn) const
	{
		return m_statement ? sqlite3_column_type(m_statement.getHandle(), iColumn) : SQLITE_NULL;
	}
	int getInt(int iColumn) const
	{
		return m_statement ? sqlite3_column_int(m_statement.getHandle(), iColumn) : 0;
	}
	scaled getFloat(int iColumn) const
	{
		return m_statement ? fixp(static_cast<float>(sqlite3_column_double(m_statement.getHandle(), iColumn))) ; scaled();
	}
	double getDouble(int iColumn) const
	{
		return m_statement ? sqlite3_column_double(m_statement.getHandle(), iColumn) : 0;
	}
	scaled getScaled(int iColumn) const
	{
		return m_statement ? scaled(sqlite3_column_double(m_statement.getHandle(), iColumn)) : scaled();
	}
	bool getBool(int iColumn) const
	{
		return m_statement ? sqlite3_column_int(m_statement.getHandle(), iColumn) != 0 : false;
	}
	const char* getText(int iColumn) const
	{
		return m_statement ? reinterpret_cast<const char*>(sqlite3_column_text(m_statement.getHandle(), iColumn)) : NULL;
	}
	CvString getString(int iColumn) const
	{
		const char* txt = getText(iColumn);
		return txt ? CvString(txt) : CvString();
	}
	bool isNull(int iColumn) const
	{
		return m_statement ? sqlite3_column_type(m_statement.getHandle(), iColumn) == SQLITE_NULL : false;
	}
};
#endif
