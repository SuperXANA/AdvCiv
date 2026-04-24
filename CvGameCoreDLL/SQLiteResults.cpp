#include "SQLiteResults.h"
#include "SQLiteStatement.h"

SQLiteResults::SQLiteResults(SQLiteStatement& stmt)
	: m_statement(stmt)
	{}

bool SQLiteResults::exec()
{
	return m_statement.step(false);
}

bool SQLiteResults::next()
{
	return m_statement.step();
}
	
int SQLiteResults::getInt(const char* szColName) const
{
	return m_statement.getInt(m_statement.getColumnIndex(szColName));
}

float SQLiteResults::getFloat(const char* szColName) const
{
	return m_statement.getFloat(m_statement.getColumnIndex(szColName));
}

double SQLiteResults::getDouble(const char* szColName) const
{
	return m_statement.getDouble(m_statement.getColumnIndex(szColName));
}

scaled SQLiteResults::getScaled(const char* szColName) const
{
	return scaled(m_statement.getFloat(m_statement.getColumnIndex(szColName)), 100);
}

bool SQLiteResults::getBool(const char* szColName) const
{
	return m_statement.getBool(m_statement.getColumnIndex(szColName));
}

CvString SQLiteResults::getText(const char* szColName) const
{
	return m_statement.getText(m_statement.getColumnIndex(szColName));
}

bool SQLiteResults::isNull(const char* szColName) const
{
	return m_statement.isNull(m_statement.getColumnIndex(szColName));
}

int SQLiteResults::getColumnType(const char* szColName) const
{
	return m_statement.getColumnType(m_statement.getColumnIndex(szColName));
}
