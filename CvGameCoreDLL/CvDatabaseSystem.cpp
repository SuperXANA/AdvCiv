#include "CvGameCoreDLL.h"
#include "CvDatabaseSystem.h"

CvDatabaseManager::CvDatabaseManager() : m_db(new SQLiteConnection("MLPCiv.sqlite"))
{}

SQLiteStatement CvDatabaseManager::makeStatement(CvString const& szSQL)
{
	SQLiteStatement kStatement(szSQL);
	return kStatement;
}

void CvDatabaseManager::log(int const iReturnCode, const char* szContext)
{
	SQLiteException(iReturnCode) problem;
	problem.log(szContext);
}