#include "CvGameCoreDLL.h"
#include "SQLiteTransaction.h"

SQLiteTransaction::SQLiteTransaction() : m_bProcessing(false)
{
	if (DB.ready())
	{
		int const sqliteReturnCode = DB.exec("BEGIN TRANSACTION;");
		if (sqliteReturnCode != SQLITE_OK)
			DB.log(sqliteReturnCode, "SQLiteTransaction: Failed creating transaction for database!");
		else m_bProcessing = true;
	}
}

SQLiteTransaction::~SQLiteTransaction()
{
	if (ready())
	{
		rollback();
	}
}

bool SQLiteTransaction::commit()
{
	if (ready())
	{
		int const sqliteReturnCode = DB.exec("COMMIT;");
		if (sqliteReturnCode != SQLITE_OK)
		{
			DB.log(sqliteReturnCode, "SQLiteTransaction: Commit failed on database! Rolling back transction.");
			return rollback();
		}
		else
		{
			m_bProcessing = false;
			return sqliteReturnCode == SQLITE_OK;
		}
	}
	else return false;
}

bool SQLiteTransaction::rollback()
{
	if (ready())
	{
		m_bProcessing = false;
		return DB.exec("ROLLBACK;") == SQLITE_OK;
	}
	else return false;
}