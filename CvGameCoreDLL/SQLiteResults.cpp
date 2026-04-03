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
	return (idx >= 0) ? getScaled(idx) : 0;
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
