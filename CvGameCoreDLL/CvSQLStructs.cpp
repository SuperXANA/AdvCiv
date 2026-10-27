// XANA: 10-04-2025 Data Storage Interface for Advanced Civ
#include "CvGameCoreDLL.h"
#include "CvSQLStructs.h"
#include "CvDatabaseManager.h"
#include "CvDatabaseQuery.h"
#include "SQLiteTransaction.h"
#include "SQLiteStatement.h"
#include "SQLiteValue.h"

int SQLSchemaData::query()
{
	const CvString szName("SQL Schema Version Check");
	const CvString szSQL("PRAGMA user_version;");	
	SQLiteStatement kStatement(szName, szSQL);
	if (kStatement.exec())
	{
		return kStatement.getInt(0);
	}
	return -1;
}

bool SQLSchemaData::update(const CvString& szSQL)
{
	SQLiteTransaction kTransaction;
	if (kTransaction.isValid())
	{
		if (DB.exec(szSQL))
		{
			return kTransaction.commit();
		}
	}
	return false;
}