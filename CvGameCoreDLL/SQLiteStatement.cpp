#include "CvDatabaseManager.h"
#include "SQLiteStatement.h"
#include "CvDatabaseFwd.h"

SQLiteStatement::SQLiteStatement()
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false), m_szSQL(NULL), m_resultCursor(*this)
	{}


SQLiteStatement::SQLiteStatement(const CvString& szSQL)
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false), m_szSQL(szSQL), m_resultCursor(*this)
	{
		prepare(m_szSQL);
	}
	
SQLiteStatement::SQLiteStatement(const std::string& sql)
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false), m_szSQL(sql), m_resultCursor(*this)
	{
		prepare(m_szSQL);
	}

SQLiteStatement::~SQLiteStatement()
{
	finalize();
}

bool SQLiteStatement::isValid(bool bCheckDatabaseConnection) const
{
	return (bCheckDatabaseConnection ? (GC.getDatabaseInstance().isValid() && m_statement != NULL && !m_bFinalized) : (m_statement != NULL && !m_bFinalized));
}

bool SQLiteStatement::prepare(const CvString& szSQL)
{
	m_szSQL = szSQL;
	if (!GC.getDatabaseInstance().isValid() || !(m_szSQL.GetCString()) || m_bFinalized)
	{
		return false;
	}
	if (m_bPrepared)
	{
		return true;
	}
	if (isValid()) // XANA (note): If we are re-using the existing (prepared or not) statement for something else, clear out the existing statement object and make sure it's ready for new SQL queries
	{
		reset();
		clearBindings();
		m_bPrepared = false;
	}
	int const rc = sqlite3_prepare_v2(GC.getDatabaseInstance().getSQLite(), m_szSQL.GetCString(), -1, &m_statement, NULL);
	if (rc != SQLITE_OK || m_statement == NULL)
	{
		return false;
	}
	m_bPrepared = true;
	if (!m_bMappedColumns)
	{
		m_bMappedColumns = mapColumns();
	}
	return true;
}

bool SQLiteStatement::prepare(const std::string& sql)
{
	return prepare(CvString(sql));
}

bool SQLiteStatement::mapColumns() // Hash columns for fast lookup, based on MapChildren from CvXMLloadUtility
{
	if (m_bMappedColumns)
	{
		return true;
	}
	if (!isValid())
	{
		return false;
	}
	m_columnsMap.clear();
	int const iCount = getColumnCount();
	if (iCount <= 0)
	{
		return false;
	}
	int iColsMapped = 0;
	for (int i = 0; i < iCount; ++i)
	{
		const char* szColumn = getColumnName(i);
		if (szColumn)
		{
			m_columnsMap[szColumn] = i;
			iColsMapped++;
		}
	}
	return (iColsMapped > 0);
}

int SQLiteStatement::getColumnIndex(const char* szName) const
{
	if (!m_bMappedColumns || !isValid())
	{
		return -1;
	}
	ColumnsMap::interator it = m_columnsMap.find(szName);
    if (it == m_columnsMap.end())
	{
		return -1;
    }
	return it->second;
}

bool SQLiteStatement::reset()
{
	m_bHasRow = false;
	m_bPrepared = false;
	return isValid() ? sqlite3_reset(m_statement) == SQLITE_OK : false;
}

bool SQLiteStatement::finalize()
{
	if (isValid(false))
	{
		m_bFinalized = (sqlite3_finalize(m_statement) == SQLITE_OK);
		if (m_bFinalized)
		{
			m_statement = NULL;
		}
		m_bHasRow = false;
		m_bPrepared = false;
		return (m_statement == NULL);
	}
	return true;
}

bool SQLiteStatement::clearBindings()
{
	return isValid() ? sqlite3_clear_bindings(m_statement) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(const char* szParam, int iValue)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, iValue) : false;
}

bool SQLiteStatement::bind(const char* szParam, float fValue)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, fValue) : false;
}

bool SQLiteStatement::bind(const char* szParam, double dValue)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, dValue) : false;
}

bool SQLiteStatement::bind(const char* szParam, scaled rValue)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, rValue) : false;
}

bool SQLiteStatement::bind(const char* szParam, const char* szValue, bool bCopy)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, szValue, bCopy) : false;
}

bool SQLiteStatement::bind(const char* szParam, const std::string& szValue)
{
	return bind(szParam, szValue.c_str(), true);
}

bool SQLiteStatement::bind(const char* szParam, const CvString& szValue)
{
	return bind(szParam, szValue.c_str(), true);
}

bool SQLiteStatement::bindNull(const char* szParam)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bindNull(idx) : false;
}

bool SQLiteStatement::hasBinding(const char* szParam) const
{
    return getParameterIndex(szParam) != 0;
}

bool SQLiteStatement::step()
{
	if (!isPrepared())
	{
		m_bHasRow = false;
		return false;
	}
	int const rc = sqlite3_step(m_statement);
	m_bHasRow = (rc == SQLITE_ROW || rc == SQLITE_DONE);
	if (rc != SQLITE_ROW)
	{
		reset();
	}
	return m_bHasRow;
}

bool SQLiteStatement::exec()
{
	if (isPrepared())
	{
		return step();
	}
	return false;
}

SQLiteResults& SQLiteStatement::getResults()
{
	return m_resultCursor;
}

int SQLiteStatement::getColumnType(int iColumn) const
{
	return hasRow() ? sqlite3_column_type(m_statement, iColumn) : SQLITE_NULL;
}

int SQLiteStatement::getInt(int iColumn) const
{
	return hasRow() ? sqlite3_column_int(m_statement, iColumn) : 0;
}

float SQLiteStatement::getFloat(int iColumn) const
{
	return hasRow() ? static_cast<float>(sqlite3_column_double(m_statement, iColumn)) : 0.0f;
}

double SQLiteStatement::getDouble(int iColumn) const
{
	return hasRow() ? sqlite3_column_double(m_statement, iColumn) : 0;
}

bool SQLiteStatement::getBool(int iColumn) const
{
	return hasRow() ? sqlite3_column_int(m_statement, iColumn) != 0 : false;
}

CvString SQLiteStatement::getText(int iColumn) const
{
	return CvString(hasRow() ? reinterpret_cast<const char*>(sqlite3_column_text(m_statement, iColumn)) : NULL);
}

bool SQLiteStatement::isNull(int iColumn) const
{
	return hasRow() ? sqlite3_column_type(m_statement, iColumn) == SQLITE_NULL : false;
}

int SQLiteStatement::getColumnCount() const
{
	return isValid() ? sqlite3_column_count(m_statement) : 0;
}

bool SQLiteStatement::bind(int index, int iValue)
{
	return isValid() ? sqlite3_bind_int(m_statement, index, iValue) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, float fValue)
{
	return isValid() ? sqlite3_bind_double(m_statement, index, static_cast<double>(fValue)) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, double dValue)
{
	return isValid() ? sqlite3_bind_double(m_statement, index, dValue) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, scaled rValue)
{
	return isValid() ? sqlite3_bind_int(m_statement, index, rValue) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, const char* szValue, bool bCopy = true)
{
	if (!value) return bindNull(index);
	sqlite3_destructor_type destructor = bCopy ? SQLITE_TRANSIENT : SQLITE_STATIC;
	return isValid() ? sqlite3_bind_text(m_statement, index, szValue, -1, destructor) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, const std::string& szValue)
{
	return bind(index, szValue.c_str(), true);
}

bool SQLiteStatement::bind(int index, const CvString& szValue)
{
	return bind(index, szValue.c_str(), true);
}

bool SQLiteStatement::bindNull(int index)
{
	return isValid() ? sqlite3_bind_null(m_statement, index) == SQLITE_OK : false;
}

int SQLiteStatement::getParameterIndex(const char* szName) const
{
	return isValid() ? sqlite3_bind_parameter_index(m_statement, szName) : 0;
}

const char* SQLiteStatement::getColumnName(int col) const
{
	return isValid() ? sqlite3_column_name(m_statement, col) : NULL;
}
