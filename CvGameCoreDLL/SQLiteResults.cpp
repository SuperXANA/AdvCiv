#include "SQLiteResults.h"
#include "SQLiteStatement.h"

SQLiteResults::SQLiteResults(SQLiteStatement* stmt)
	: m_statement(stmt)
	{}

bool SQLiteResults::isValid() const
{
	return (m_statement != NULL && m_statement->isPrepared());
}

bool SQLiteResults::hasRow() const
{
	return isValid() && m_statement->hasRow();
}

bool SQLiteResults::next()
{
	return ((isValid() ? m_statement->step() : false) && hasRow());
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
int SQLiteResults::getColumnIndex(const char* szName) const { return isValid() ? m_statement->getColumnIndex(szName) : -1; }
int SQLiteResults::getColumnType(int iColumn) const { return isValid() ? m_statement->getColumnType(iColumn) : SQLITE_NULL; }

// SQL Database Private Access Functions
int SQLiteResults::getInt(int iColumn) const { return hasRow() ? m_statement->getInt(iColumn) : 0; }
scaled SQLiteResults::getFloat(int iColumn) const { return fixp(hasRow() ? m_statement->getFloat(iColumn) : 0.0f); }
double SQLiteResults::getDouble(int iColumn) const { return hasRow() ? m_statement->getDouble(iColumn) : 0; }
scaled SQLiteResults::getScaled(int iColumn) const { return hasRow() ? m_statement->getScaled(iColumn) : scaled(); }
bool SQLiteResults::getBool(int iColumn) const { return hasRow() ? m_statement->getBool(iColumn) : false; }
const char* SQLiteResults::getText(int iColumn) const { return hasRow() ? m_statement->getText(iColumn) : NULL; }
CvString SQLiteResults::getString(int iColumn) const { return CvString(getText(iColumn)); }
bool SQLiteResults::isNull(int iColumn) const { return hasRow() ? m_statement->isNull(iColumn) : false; }
