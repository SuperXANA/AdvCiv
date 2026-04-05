#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITESTATEMENT_H
#define CV_SQLITESTATEMENT_H

struct sqlite3_stmt;
class SQLiteResults;
class CvDatabaseManager;

class SQLiteStatement : private boost::noncopyable
{
public:
	SQLiteStatement();
	SQLiteStatement(const CvString& szSQL);
	SQLiteStatement(const char* sql);
	~SQLiteStatement();
	
	bool isValid() const;
	bool isPrepared() const { return isValid() && m_bPrepared; }
	bool hasRow() const { return isPrepared() && m_bHasRow; }
	
	bool prepare(const CvString& szSQL);
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
	bool bindNull(const char* szParam) const;
	bool hasBinding(const char* szParam) const;

	bool step();
	bool exec();
	
	SQLiteResults getResults();
	
	int getColumnType(int iColumn) const
	{
		return isValid(false) ? sqlite3_column_type(m_statement, iColumn) : SQLITE_NULL;
	}
	int getInt(int iColumn) const
	{
		return isPrepared() ? sqlite3_column_int(m_statement, iColumn) : 0;
	}
	float getFloat(int iColumn) const
	{
		return isPrepared() ? static_cast<float>(sqlite3_column_double(m_statement, iColumn))) : 0.0f;
	}
	double getDouble(int iColumn) const
	{
		return isPrepared() ? sqlite3_column_double(m_statement, iColumn) : 0;
	}
	scaled getScaled(int iColumn) const
	{
		return scaled(isPrepared() ? sqlite3_column_int(m_statement, iColumn) : 0);
	}
	bool getBool(int iColumn) const
	{
		return isPrepared() ? sqlite3_column_int(m_statement, iColumn) != 0 : false;
	}
	const char* getText(int iColumn) const
	{
		return isPrepared() ? reinterpret_cast<const char*>(sqlite3_column_text(m_statement, iColumn)) : NULL;
	}
	bool isNull(int iColumn) const
	{
		return isPrepared() ? sqlite3_column_type(m_statement, iColumn) == SQLITE_NULL : false;
	}

private:
	sqlite3_stmt* m_statement;
	bool m_bHasRow;
	typedef stdext::hash_map<std::string, int> ColumnsMap;
	ColumnsMap m_columnsMap;
	bool m_bMappedColumns;
	bool m_bFinalized;
	bool m_bPrepared;
	
	bool prepare(const char* sql);
	
	int getColumnCount() const
	{
		return isValid() ? sqlite3_column_count(m_statement) : 0;
	}
	bool bind(int index, int iValue)
	{
		return isValid() ? sqlite3_bind_int(m_statement, index, iValue) == SQLITE_OK : false;
	}
	bool bind(int index, float fValue)
	{
		return isValid() ? sqlite3_bind_double(m_statement, index, static_cast<double>(fValue)) == SQLITE_OK : false;
	}
	bool bind(int index, double dValue)
	{
		return isValid() ? sqlite3_bind_double(m_statement, index, dValue) == SQLITE_OK : false;
	}
	bool bind(int index, scaled rValue)
	{
		return isValid() ? sqlite3_bind_int(m_statement, index, rValue) == SQLITE_OK : false;
	}
	bool bind(int index, const char* szValue, bool bCopy = true)
	{
		if (!value) return bindNull(index);
		sqlite3_destructor_type destructor = bCopy ? SQLITE_TRANSIENT : SQLITE_STATIC;
		return isValid() ? sqlite3_bind_text(m_statement, index, szValue, -1, destructor) == SQLITE_OK : false;
	}
	bool bind(int index, const std::string& szValue)
	{
		return bind(index, szValue.c_str(), true);
	}
	bool bind(int index, const CvString& szValue)
	{
		return bind(index, szValue.c_str(), true);
	}
	bool bindNull(int index)
	{
		return isValid() ? sqlite3_bind_null(m_statement, index) == SQLITE_OK : false;
	}
	int getParameterIndex(const char* szName) const
	{
		return isValid() ? sqlite3_bind_parameter_index(m_statement, szName) : 0;
	}
	const char* getColumnName(int col) const
	{
		return isValid() ? sqlite3_column_name(m_statement, col) : NULL;
	}
};
#endif

