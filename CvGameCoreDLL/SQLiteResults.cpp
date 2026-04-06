#include "SQLiteResults.h"
#include "SQLiteStatement.h"

SQLiteResults::SQLiteResults(SQLiteStatement& stmt)
	: m_statement(stmt)
	{}

bool SQLiteResults::exec()
{
	return m_statement.exec();
}

bool SQLiteResults::next()
{
	return exec();
}
	
int SQLiteResults::getInt(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getInt(idx) : 0;
}

float SQLiteResults::getFloat(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getFloat(idx) : 0.0f;
}

scaled SQLiteResults::getScaled(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return scaled((idx >= 0) ? getInt(idx) : 0);
}

bool SQLiteResults::getBool(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getBool(idx) : false;
}

CvString SQLiteResults::getText(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getText(idx) : CvString(NULL);
}

bool SQLiteResults::isNull(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? isNull(idx) : false;
}

int SQLiteResults::getColumnType(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getColumnType(idx) : SQLITE_NULL;
}

// XANA (note): Internal functions below, you likely want to use the functions that take SQL columns by name instead
int SQLiteResults::getColumnIndex(const char* szName) const { return m_statement.getColumnIndex(szName); }
int SQLiteResults::getColumnType(int iColumn) const { return m_statement.getColumnType(iColumn); }

// SQL Database Private Access Functions
int SQLiteResults::getInt(int iColumn) const { return m_statement.getInt(iColumn); }
float SQLiteResults::getFloat(int iColumn) const { return m_statement.getFloat(iColumn); }
double SQLiteResults::getDouble(int iColumn) const { return m_statement.getDouble(iColumn); }
bool SQLiteResults::getBool(int iColumn) const { return m_statement.getBool(iColumn); }
CvString SQLiteResults::getText(int iColumn) const { return m_statement.getText(iColumn); }
bool SQLiteResults::isNull(int iColumn) const { return m_statement.isNull(iColumn); }
