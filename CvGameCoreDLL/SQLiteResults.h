#pragma once

#include "CvGameCoreDLL.h"
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
		return m_statement ? sqlite3_column_type(m_statement.getHandle(), col) : SQLITE_NULL;
	}
	int getInt(int iColumn) const
	{
		return m_statement ? sqlite3_column_int(m_statement.getHandle(), col) : 0;
	}
	scaled getFloat(int iColumn) const
	{
		return m_statement ? fixp(static_cast<float>(sqlite3_column_double(m_statement.getHandle(), col))) ; scaled();
	}
	double getDouble(int iColumn) const
	{
		return m_statement ? sqlite3_column_double(m_statement.getHandle(), col) : 0d;
	}
	scaled getScaled(int iColumn) const
	{
		return m_statement ? scaled(sqlite3_column_double(m_statement.getHandle(), col)) : scaled();
	}
	bool getBool(int iColumn) const
	{
		return m_statement ? sqlite3_column_int(m_statement.getHandle(), col) != 0 : false;
	}
	const char* getText(int iColumn) const
	{
		return m_statement ? reinterpret_cast<const char*>(sqlite3_column_text(m_statement.getHandle(), col)) : "";
	}
	CvString getString(int iColumn) const
	{
		const char* txt = getText(col);
		return txt ? CvString(txt) : CvString();
	}
	bool isNull(int iColumn) const
	{
		return m_statement ? sqlite3_column_type(m_statement.getHandle(), col) == SQLITE_NULL : false;
	}
};
