#include "CvGameCoreDLL.h"
#include "CvDatabaseManager.h"
#include "SQLiteStatement.h"
#include "CvDatabaseFwd.h"
#include "SQLiteValue.h"

SQLiteStatement::SQLiteStatement()
	: m_szKey(), m_szSQL(), m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bMappedParameters(false), m_bPrepared(false), m_bFinished(false), m_iLastResult(SQLITE_OK)
	{}


SQLiteStatement::SQLiteStatement(const CvString& szKey)
	: m_szKey(szKey), m_szSQL(), m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bMappedParameters(false), m_bPrepared(false), m_bFinished(false), m_iLastResult(SQLITE_OK)
	{}
	
SQLiteStatement::SQLiteStatement(const CvString& szKey, const CvString& szSQL)
	: m_szKey(szKey), m_szSQL(szSQL), m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bMappedParameters(false), m_bPrepared(false), m_bFinished(false), m_iLastResult(SQLITE_OK)
	{
		prepare(m_szSQL);
	}

SQLiteStatement::~SQLiteStatement()
{
	finalize();
}

bool SQLiteStatement::isValid() const
{
	return (m_statement != NULL);
}

bool SQLiteStatement::prepare(const CvString& szSQL)
{
	if (m_szKey.empty() || szSQL.empty())
	{
		return false;
	}
	if (isPrepared())
	{
		if (m_szSQL == szSQL)
			return true;
		finalize();
	}
	if (m_szSQL != szSQL)
	{
		// reset(false) may preserve lookup maps for the previous SQL.
		reset();
		m_szSQL = szSQL;
	}
	m_statement = DB.prepareStatementFromCache(m_szKey, m_szSQL);
	if (m_statement == NULL)
	{
		m_iLastResult = SQLITE_ERROR;
		return false;
	}
	setPrepared(true);
	m_bFinished = false;
	m_iLastResult = SQLITE_OK;
	if (!m_bMappedColumns)
	{
		m_bMappedColumns = mapColumns();
	}
	if (!m_bMappedParameters)
	{
		m_bMappedParameters = mapParams();
	}
	return true;
}

bool SQLiteStatement::exec()
{
	return step(false);
}

bool SQLiteStatement::next()
{
	return step();
}

SQLiteValue SQLiteStatement::getValue(const char* szColName) const
{
	return getValue(getColumnIndex(szColName));
}

SQLiteValue SQLiteStatement::getValue(int iColumn) const
{
	if (iColumn >= 0)
	{
		switch (getColumnType(iColumn))
		{
			case SQLITE_INTEGER:
			{
				return SQLiteValue(getInt(iColumn));
			}
			case SQLITE_FLOAT:
			{
				return SQLiteValue(getDouble(iColumn));
			}
			case SQLITE_TEXT:
			{
				return SQLiteValue(getText(iColumn));
			}
			default:
			{
				return SQLiteValue();
			}
		}
	}
	return SQLiteValue();
}

int SQLiteStatement::getInt(const char* szColName) const
{
	return getInt(getColumnIndex(szColName));
}

float SQLiteStatement::getFloat(const char* szColName) const
{
	return getFloat(getColumnIndex(szColName));
}

double SQLiteStatement::getDouble(const char* szColName) const
{
	return getDouble(getColumnIndex(szColName));
}

scaled SQLiteStatement::getScaled(const char* szColName) const
{
	double const d = getDouble(getColumnIndex(szColName));
	return (d >= scaled::MIN && d <= scaled::MAX) ? scaled::fromDouble(d) : scaled();
}

bool SQLiteStatement::getBool(const char* szColName) const
{
	return getBool(getColumnIndex(szColName));
}

CvString SQLiteStatement::getText(const char* szColName) const
{
	return getText(getColumnIndex(szColName));
}

bool SQLiteStatement::isNull(const char* szColName) const
{
	return isNull(getColumnIndex(szColName));
}

int SQLiteStatement::getColumnType(const char* szColName) const
{
	return getColumnType(getColumnIndex(szColName));
}

bool SQLiteStatement::mapColumns() // Hash columns for fast lookup, based on MapChildren from CvXMLloadUtility
{
	if (!isValid())
	{
		return false;
	}
	if (m_bMappedColumns)
	{
		return true;
	}
	m_columnNameMap.clear();
	m_columnIDMap.clear();
	int const iCount = getColumnCount();
	if (iCount <= 0)
	{
		return false;
	}
	bool bColsMapped = false;
	for (int i = 0; i < iCount; ++i)
	{
		const char* szColumn = getSQLColumnName(i);
		if (szColumn)
		{
			m_columnNameMap[szColumn] = i;
			m_columnIDMap[i] = szColumn;
			bColsMapped = true;
		}
	}
	return bColsMapped;
}

bool SQLiteStatement::mapParams() // Hash parameters for fast lookup, based on MapChildren from CvXMLloadUtility
{
	if (!isValid())
	{
		return false;
	}
	if (m_bMappedParameters)
	{
		return true;
	}
	m_paramNameMap.clear();
	m_paramIDMap.clear();
	int const iCount = getParameterCount();
	if (iCount <= 0)
	{
		return false;
	}
	bool bParamsMapped = false;
	for (int i = 1; i < (iCount + 1); ++i)
	{
		const char* szParam = getSQLParameterName(i);
		if (szParam)
		{
			m_paramNameMap[szParam] = i;
			m_paramIDMap[i] = szParam;
			bParamsMapped = true;
		}
	}
	return bParamsMapped;
}

void SQLiteStatement::reset(bool bClearStatementMap)
{
	if (bClearStatementMap)
	{
		m_columnNameMap.clear();
		m_columnIDMap.clear();
		m_bMappedColumns = false;
		
		m_paramNameMap.clear();
		m_paramIDMap.clear();
		m_bMappedParameters = false;
	}
	m_bHasRow = false;
	setPrepared(false);
	DB.returnStatementToCache(m_szKey, m_statement);
}

void SQLiteStatement::finalize()
{
	reset();
}

int SQLiteStatement::getColumnIndex(const char* szName) const
{
	if (!m_bMappedColumns || !isValid() || !szName)
	{
		return -1;
	}
	ColumnNameMap::const_iterator it = m_columnNameMap.find(szName);
    if (it == m_columnNameMap.end())
	{
		return -1;
    }
	return it->second;
}

const char* SQLiteStatement::getColumnName(int iColumn) const
{
	if (!m_bMappedColumns || !isValid() || iColumn < 0)
	{
		return NULL;
	}
	ColumnIDMap::const_iterator it = m_columnIDMap.find(iColumn);
    if (it == m_columnIDMap.end())
	{
		return NULL;
    }
	return it->second.c_str();
}

int SQLiteStatement::getParameterIndex(const char* szName) const
{
	if (!m_bMappedParameters || !isValid() || !szName)
	{
		return 0;
	}
	ParameterNameMap::const_iterator it = m_paramNameMap.find(szName);
    if (it == m_paramNameMap.end())
	{
		return 0;
    }
	return it->second;
}

const char* SQLiteStatement::getParameterName(int index) const
{
	if (!m_bMappedParameters || !isValid() || index <= 0)
	{
		return NULL;
	}
	ParameterIDMap::const_iterator it = m_paramIDMap.find(index);
    if (it == m_paramIDMap.end())
	{
		return NULL;
    }
	return it->second.c_str();
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
	return bind(szParam, szValue.GetCString(), true);
}

bool SQLiteStatement::bind(const char* szParam, bool bValue)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bind(idx, bValue) : false;
}

bool SQLiteStatement::bindNull(const char* szParam)
{
	int const idx = getParameterIndex(szParam);
	return (idx > 0) ? bindNull(idx) : false;
}

bool SQLiteStatement::hasColumn(const char* szName) const
{
    return getColumnIndex(szName) != -1;
}

bool SQLiteStatement::hasBinding(const char* szParam) const
{
    return getParameterIndex(szParam) != 0;
}

// XANA: 10-27-2026 SQLite safety: DONE is success for exec, never a row for next.
bool SQLiteStatement::step(bool bLooping)
{
	m_bHasRow = false;
	if (!isPrepared() || m_bFinished)
		return false;
	bool const bFirstStep = (m_iLastResult == SQLITE_OK);
	m_iLastResult = sqlite3_step(m_statement);
	DB.refreshTransactionState();
	// XANA: 10-27-2026 SQLite may recompile a cached statement after a schema
	// change. Refresh result names after the first step, including empty results.
	if (bFirstStep && (m_iLastResult == SQLITE_ROW || m_iLastResult == SQLITE_DONE))
	{
		m_bMappedColumns = false;
		m_bMappedColumns = mapColumns();
	}
	// XANA: END schema-recompile column lookup refresh.
	m_bHasRow = (m_iLastResult == SQLITE_ROW);
	m_bFinished = !m_bHasRow;
	return bLooping ? m_bHasRow :
		(m_bHasRow || m_iLastResult == SQLITE_DONE);
}

int SQLiteStatement::getColumnType(int iColumn) const
{
	return hasRow(iColumn) ? sqlite3_column_type(m_statement, iColumn) : SQLITE_NULL;
}

int SQLiteStatement::getInt(int iColumn) const
{
	return hasRow(iColumn) ? sqlite3_column_int(m_statement, iColumn) : 0;
}

float SQLiteStatement::getFloat(int iColumn) const
{
	return hasRow(iColumn) ? static_cast<float>(sqlite3_column_double(m_statement, iColumn)) : 0.0f;
}

double SQLiteStatement::getDouble(int iColumn) const
{
	return hasRow(iColumn) ? sqlite3_column_double(m_statement, iColumn) : 0;
}

bool SQLiteStatement::getBool(int iColumn) const
{
	return hasRow(iColumn) ? sqlite3_column_int(m_statement, iColumn) != 0 : false;
}

CvString SQLiteStatement::getText(int iColumn) const
{
	return CvString(hasRow(iColumn) && sqlite3_column_text(m_statement, iColumn) ? reinterpret_cast<const char*>(sqlite3_column_text(m_statement, iColumn)) : "");
}

bool SQLiteStatement::isNull(int iColumn) const
{
	return hasRow(iColumn) ? sqlite3_column_type(m_statement, iColumn) == SQLITE_NULL : false;
}

int SQLiteStatement::getColumnCount() const
{
	return isValid() ? sqlite3_column_count(m_statement) : 0;
}

int SQLiteStatement::getParameterCount() const
{
	return isValid() ? sqlite3_bind_parameter_count(m_statement) : 0;
}

bool SQLiteStatement::bind(int index, int iValue)
{
	return isValid() ? sqlite3_bind_int(m_statement, index, iValue) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, float fValue)
{
	return bind(index, static_cast<double>(fValue));
}

bool SQLiteStatement::bind(int index, double dValue)
{
	return isValid() ? sqlite3_bind_double(m_statement, index, dValue) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, scaled rValue)
{
	return bind(index, rValue.getDouble());
}

bool SQLiteStatement::bind(int index, const char* szValue, bool bCopy)
{
	if (!szValue) return bindNull(index);
	sqlite3_destructor_type destructor = bCopy ? SQLITE_TRANSIENT : SQLITE_STATIC;
	return isValid() ? sqlite3_bind_text(m_statement, index, szValue, -1, destructor) == SQLITE_OK : false;
}

bool SQLiteStatement::bind(int index, const std::string& szValue)
{
	return bind(index, szValue.c_str(), true);
}

bool SQLiteStatement::bind(int index, const CvString& szValue)
{
	return bind(index, szValue.GetCString(), true);
}

bool SQLiteStatement::bind(int index, bool bValue)
{
	return bind(index, static_cast<int>(bValue));
}

bool SQLiteStatement::bindNull(int index)
{
	return isValid() ? sqlite3_bind_null(m_statement, index) == SQLITE_OK : false;
}

const char* SQLiteStatement::getSQLParameterName(int index) const
{
	return (isValid() && index > 0) ? sqlite3_bind_parameter_name(m_statement, index) : NULL;
}

const char* SQLiteStatement::getSQLColumnName(int col) const
{
	return (isValid() && col >= 0) ? sqlite3_column_name(m_statement, col) : NULL;
}
