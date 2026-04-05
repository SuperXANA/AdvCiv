#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL)
{}

CvDatabaseManager::~CvDatabaseManager()
{
	SAFE_DELETE(m_sqlite);
}

void CvDatabaseManager::init()
{
	if (m_sqlite == NULL)
	{
		m_sqlite = new SQLiteConnection(GC.getModName().getFullPath() + "MLPCiv.sqlite");
	}
}

sqlite3* CvDatabaseManager::getSQLite()
{
	return isValid() ? m_sqlite->getDatabase() : NULL;
}

bool CvDatabaseManager::exec(const char* sql)
{
	if (!isValid() || !sql)
	{
		return false;
	}
	else return m_sqlite->exec(sql);
}

bool CvDatabaseManager::isValid() const
{
	return m_sqlite ? m_sqlite->isValid() : false;
}

/* 
XANA (note): Example of using CvSQL interface in game code which could be used to write queries elsewhere
bool testSQL() const // write a function for this query
{
	SQLiteTransaction kTransaction; // create new transaction object now, starts SQL query logic
	
	SQLiteStatement kStatement("SELECT Type, Cost, bNaval FROM Units WHERE Era <= :era AND bEnabled = 1"); // statements automatically request the sqlite3* pointer from SQLiteConnection class
	kStatement.bind(":era", 2); // bind the Industrial Era enum value, or whatever the second era number is in the mod, as :era param of SQL query
	
	SQLiteResults kResults = kStatement.getResults(); // get a Results object slice containing the data SQL found in the posed query
	while (kResults.next()) // go through all results found in the view
	{
		CvString type = kResults.getString("Type"); // get Type column header data from SQL using column name
		int cost = kResults.getInt("Cost"); // get Cost column header data from SQL using column name
		bool bNaval = kResults.getBool("bNaval");  // get bNaval column header data from SQL using column name
		
		// Use Civ4 data...
		// gDLL->logMsg("SQL.log", type); // log data output
		// m_vector.push_back(cost); // add cost number to a vector
		//if (bNaval) // check if the unit we found from the query is a naval unit type
		//	{
		//		return true; // return something indicating we found at least one valid unit
		//	}
	}
	kTransaction.commit(); // write transaction to database log
	return false; // return something indicating we found no units
} */