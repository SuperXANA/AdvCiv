#include "SQLiteResults.h"
#include "SQLiteStatement.h"

SQLiteResults::SQLiteResults(SQLiteStatement& stmt) 
	: m_statement(stmt), m_bValid(true) 
	{}

bool SQLiteResults::next()
{
	m_bValid = m_statement.step();
	return m_bValid;
}

int SQLiteResults::getInt(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getInt(idx) : 0;
}

scaled SQLiteResults::getFloat(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getFloat(idx) : fixp(0.0f);
}

scaled SQLiteResults::getScaled(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getScaled(idx) : scaled();
}

bool SQLiteResults::getBool(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getBool(idx) : false;
}

CvString SQLiteResults::getString(const char* szColName) const
{
	int const idx = getColumnIndex(szColName);
	return (idx >= 0) ? getString(idx) : CvString();
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

int SQLiteResults::getColumnIndex(const char* szName) const { return m_statement ? m_statement.getColumnIndex(szName) : -1; }
int SQLiteResults::getColumnType(int iColumn) const { return m_statement ? m_statement.getColumnType(iColumn) : SQLITE_NULL; }
int SQLiteResults::getInt(int iColumn) const { return m_statement ? m_statement.getInt(iColumn) : 0; }
scaled SQLiteResults::getFloat(int iColumn) const { return m_statement ? m_statement.getFloat(iColumn) : scaled(); }
double SQLiteResults::getDouble(int iColumn) const { return m_statement ? m_statement.getDouble(iColumn) : 0; }
scaled SQLiteResults::getScaled(int iColumn) const { return m_statement ? m_statement.getScaled(iColumn) : scaled(); }
bool SQLiteResults::getBool(int iColumn) const { return m_statement ? m_statement.getBool(iColumn) : false; }
const char* SQLiteResults::getText(int iColumn) const { return m_statement ? m_statement.getText(iColumn) : NULL; }
CvString SQLiteResults::getString(int iColumn) const { return m_statement ? m_statement.getString(iColumn) : CvString(); }
bool SQLiteResults::isNull(int iColumn) const { return m_statement ? m_statement.isNull(iColumn) : false; }
