#include "CvDatabaseManager.h"
#include "SQLiteStatement.h"
#include "SQLiteResults.h"
#include "CvDatabaseFwd.h"

SQLiteStatement::SQLiteStatement()
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false)
	{}

SQLiteStatement::SQLiteStatement(const CvString& szSQL)
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false)
	{
		prepare(szSQL);
	}

SQLiteStatement::SQLiteStatement(const char* sql)
	: m_statement(NULL), m_bHasRow(false), m_bMappedColumns(false), m_bFinalized(false), m_bPrepared(false)
	{
		prepare(sql);
	}

SQLiteStatement::~SQLiteStatement()
{
	finalize();
}

bool SQLiteStatement::isValid(bool bCheckDatabaseConnection) const
{
	return (bCheckDatabaseConnection ? (GC.getDatabaseInstance.isValid() && m_statement != NULL && !m_bFinalized) : (m_statement != NULL && !m_bFinalized));
}

bool SQLiteStatement::prepare(const char* sql)
{
	if (!GC.getDatabaseInstance.isValid() || !sql || m_bFinalized)
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
	int const rc = sqlite3_prepare_v2(GC.getDatabaseInstance().getSQLite(), sql, -1, &m_statement, NULL);
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

bool SQLiteStatement::prepare(const CvString& szSQL)
{
	return prepare(szSQL.c_str());
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
	m_bHasRow = (rc == SQLITE_ROW);
	if (!m_bHasRow)
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

SQLiteResults SQLiteStatement::getResults()
{
	return SQLiteResults(this);
}
