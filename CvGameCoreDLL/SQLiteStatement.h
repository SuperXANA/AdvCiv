#pragma once

#include "CvGameCoreDLL.h"
extern "C" { #include "sqlite3.h" }

class SQLiteStatement
{
public:
	SQLiteStatement(CvString const& szSQL) : m_statement(NULL), m_bPrepared(false), m_bFinalized(false)
	{
		if (DB.ready())
		{
			int const sqliteReturnCode = sqlite3_prepare_v2(DB.getSQLite(), szSQL.c_str(), -1, &m_statement, NULL);
			if (sqliteReturnCode != SQLITE_OK)
			{
				DB.log(sqliteReturnCode, "SQLiteStatement: Failed preparing SQL statement for database!");
				m_statement = NULL;
			}
			else m_bPrepared = true;
		}
	}
	~SQLiteStatement();
	bool ready() const { return m_statement != NULL && m_bPrepared && m_bFinalized == false; }
	template <typename ValueType>
	static bool bindNamedParamToValue(CvString const& sSQLParam, ValueType const& tValue)
	{
		if (ready())
		{
			int const iParamIndex = bindNamedParam(sSQLParam);
			if (iParamIndex > 0)
			{
				return bindValueAtIndex<ValueType>(iParamIndex, tValue);
			}
		}
		return false;
	}
	void finalize();
	bool reset() const
	{
		if (ready())
{
			return sqlite3_reset(m_statement) == SQLITE_OK;
		}
		return false;
	}
	sqlite3_stmt* getStatement() { return m_statement; }
	sqlite3_stmt* passStatement()
	{
		sqlite3_stmt* releasedPointer = m_statement;
		m_statement = NULL;
		return releasedPointer;
	}
private:
	int bindNamedParam(CvString const& szSQLParam) const
	{
		if (ready())
			return sqlite3_bind_parameter_index(m_statement, szSQLParam.c_str());
		return 0;
	}
	template <typename T>
	static int bindValue(int const i, T const& v) { return SQLITE_ERROR; }
	template <>
	static int bindValue<int>(int const i, int const& v) { return sqlite3_bind_int(m_statement, i, v); }
	template <>
	static int bindValue<scaled>(int const i, scaled const& v) { return sqlite3_bind_int(m_statement, i, static_cast<int>(v)); }
	template <>
	static int bindValue<float>(int const i, float const& v) { return sqlite3_bind_double(m_statement, i, static_cast<double>(v)); }
	template <>
	static int bindValue<double>(int const i, double const& v) { return sqlite3_bind_double(m_statement, i, v); }
	template <>
	static int bindValue<CvString>(int const i, CvString const& v) { return sqlite3_bind_text(m_statement, i, v.c_str(), -1, SQLITE_TRANSIENT); }
	template <typename T>
    bool bindValueAtIndex(int const i, T const& tValue) const
    {
        if (ready())
		{
            int sqliteReturnCode = bindValue<T>(i, tValue);
            return sqliteReturnCode == SQLITE_OK;
        }
        return false;
    }
    sqlite3_stmt* m_statement;
	bool m_bPrepared;
	bool m_bFinalized;
};