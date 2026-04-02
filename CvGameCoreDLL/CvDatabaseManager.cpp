#include "CvDatabaseManager.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(new SQLiteConnection("MLPCiv.sqlite"))
{}

CvDatabaseManager::~CvDatabaseManager()
{
	SAFE_DELETE(m_sqlite);
}

CvString CvDatabaseManager::getErrorMsg() const
{
	return CvString(getErrorInfo());
}

int CvDatabaseManager::getErrorCode() const
{
	if (!m_sqlite)
	{
		return SQLITE_ERROR;
	}
	return sqlite3_errcode(getSQLite());
}

bool CvDatabaseManager::testSQL() const
{
    SQLiteTransaction kTransaction(getSQLite());
    
    SQLiteStatement kStatement;
    if (!kStatement.prepare(getSQLite(), "SELECT Type, Cost, bNaval FROM Units WHERE Era <= :era AND bEnabled = 1")) {
        return false;
    }
    
    kStatement.bind(":era", 2);
    
    SQLiteResults kResults = kStatement.getResults();
    while (kResults.step())
	{
        CvString type = kResults.getString("Type");
        int cost = kResults.getInt("Cost");
        bool bNaval = kResults.getBool("bNaval");
        
        // Use Civ4 data...
        // gDLL->logMsg("SQL.log", type);
		// m_vector.push_back(cost);
		//if bNaval
		//	{
		//		return true;
		//	}
    }
    kTransaction.commit();
    return false;
}