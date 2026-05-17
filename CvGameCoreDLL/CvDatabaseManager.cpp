#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"
#include <fstream>
#include <shlobj.h>
#include <iostream>

#pragma comment(lib, "shell32.lib")

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL), m_bDoCache(false), m_bActive(false), m_bSqlLoaded(false)
{}

CvDatabaseManager::~CvDatabaseManager()
{}

bool CvDatabaseManager::exec(const CvString& szSQL)
{
	if (!isValid() || !szSQL.GetCString())
	{
		return false;
	}
	return m_sqlite->exec(szSQL);
}

bool CvDatabaseManager::isValid() const
{
	return ((m_sqlite && m_bActive && m_bSqlLoaded) ? m_sqlite->isValid() : false);
}

bool CvDatabaseManager::init()
{
	if (m_sqlite == NULL)
	{
		/* XANA (note): For network games, we must ensure that the sqlite3 database will be kept in sync between the players or there will be out-of-sync errors. */
		CvWString szDatabasePath(getLocationForFile());
		if (!szDatabasePath.empty()) // XANA (note): If we successfully found the user's valid, writable My Documents folder (path not empty)
		{
			m_sqlite = new SQLiteConnection(szDatabasePath);
		}
		else return false; // XANA (note): We can't save a database file in an invalid, empty location, so don't initialize at all
		if (m_sqlite != NULL && m_sqlite->open())
		{
			if (!m_bActive)
			{
				m_bActive = true;
			}
			if (!m_bSqlLoaded)
			{
				if (!m_bDoCache)
				{
					m_bDoCache = true;
				}
				int iVersion = SQL_SCHEMA_VERSION;
				if (testSchemaVersion(iVersion))
				{
					m_bSqlLoaded = true;
					return m_bSqlLoaded; // XANA (note): Database schema matches the schema required in the DLL header, everything is ready!
				}
				else if (iVersion >= 0 && iVersion != SQL_SCHEMA_VERSION) /* XANA (note): If the above test returned false and it found a lower sehema version than expected, then that means we need to migrate the data */
				{
					// XANA (note): Need to determine how to operate a "migration script" when the database needs to be rebuilt...
					bool const bErasedDatabase = migrateDatabaseSchema(); /* TODO: Edit function so that it's not a SQL erase query... */
					/* XANA (note): For now, we will just erase whatever's in our database and use the below function to recreate it... */
					m_bSqlLoaded = (bErasedDatabase && writeSchemaToDatabase());
				}	return m_bSqlLoaded;
				else
				{
					// XANA (note): We have a fresh & never-used database, so we'll set it up now!
					m_bSqlLoaded = writeSchemaToDatabase();
					return m_bSqlLoaded;
				}
			}
			else return true;
		}
		else return false;
	}
	if (isValid())
	{	
		return m_bSqlLoaded;
	}
	return false;
}

bool CvDatabaseManager::uninit()
{
	m_bDoCache = false;
	clearStatementPool();
	if (isValid())
	{
		if (m_sqlite->close())
		{
			SAFE_DELETE(m_sqlite);
		}
	}
	m_bActive = false;
	m_bSqlLoaded = false;
	return (m_sqlite == NULL);
}

sqlite3_stmt* CvDatabaseManager::prepareStatementFromCache(const CvString& szKey, const CvString& szSQL)
{
	if (!isValid() || !szKey.GetCString())
	{
		return NULL;
	}
	StatementPool::iterator it = m_statementPool.find(szKey);
	if (it != m_statementPool.end())
	{
		std::vector<sqlite3_stmt*>& vPool = it->second;
		// XANA (note): If we have cached a statement like this before, meaning the vector pool wasn't empty, give what we found back to the caller now so it can be processed immediately.
		if (!vPool.empty())
		{
			sqlite3_stmt* pStatement = vPool.back();
			vPool.pop_back();
			return pStatement;
		}
	}
	/* XANA (note): If we fell through when checking against szKey's vector storage, there's clearly nothing to use here from our memory.
	We'll get a new statement ready now, using the query text for szSQL, and the caller will automatically add it back to the cache once it's finished processing. */
	sqlite3_stmt* pStatement = NULL;
	if (prepare(pStatement, szSQL))
	{
		return pStatement;
	}
	else
	{
		pStatement = NULL;
	}
	return NULL;
}

void CvDatabaseManager::returnStatementToCache(const CvString& szKey, sqlite3_stmt*& kStatement)
{
	if (!kStatement) // XANA (note): Don't push NULL pointers to the cache, just return to keep things operating normally
	{
		return;
	}
	if (isValid() && m_doCache && szKey.GetCString())
	{
		sqlite3_reset(kStatement);
		sqlite3_clear_bindings(kStatement);
		m_statementPool[szKey].push_back(kStatement);
	}
	// XANA (note): If the database isn't ready, for example when the game shutdown process has started, or if we aren't in a position to perform caching, we shouldn't keep anything to save on memory space.
	else
	{
		sqlite3_finalize(kStatement);
	}
	kStatement = NULL; // XANA (note): Clear the caller's statement pointer that it was holding, since we have taken ownership of it in the cache or deleted it if the game is closing, to guard against problems with the game memory
}

void CvDatabaseManager::clearStatementPool()
{
	for (StatementPool::iterator it = m_statementPool.begin(); it != m_statementPool.end(); ++it)
	{
		std::vector<sqlite3_stmt*>& vPool = it->second;
		for (int j = 0; j < (int)vPool.size(); ++j)
		{
			if (vPool[j] != NULL)
			{
				sqlite3_finalize(vPool[j]);
				vPool[j] = NULL;
			}
		}
		vPool.clear();
	}
	m_statementPool.clear();
}

bool CvDatabaseManager::prepare(sqlite3_stmt*& kStatement, const CvString& szSQL)
{
	if (!isValid() || !szSQL.GetCString())
	{
		return false;
	}
	return m_sqlite->prepare(kStatement, szSQL);
}

bool CvDatabaseManager::testSchemaVersion(int& iVersion)
{
	SQLSchemaData kStruct;
	iVersion = kStruct.query();
	if (iVersion >= 0)
	{
		return (iVersion == SQL_SCHEMA_VERSION);
	}
	return false;
}

bool CvDatabaseManager::writeSchemaToDatabase()
{
	CvString szFileData;
	{
		CvString szFile(GC.getModName().getFullPath()); // XANA (note): This should resolve to "Mods\MLP Civilization is Magic" according to code comments surrounding the getFullPath function.
		szFile += "\\SQL\\CvGameDatabaseSchema.sql" // XANA (note): The full path for a correct resolution is "Mods\MLP Civilization is Magic\Assets\SQL\CvGameDatabaseSchema.sql"
		std::ifstream kFile(szFile.GetCString(), std::ios::binary | std::ios::ate);
		if (kFile.is_open())
		{
			std::streamsize size = kFile.tellg();
			if (size > 0)
			{
				kFile.seekg(0, std::ios::beg);
				std::vector<char> kBuffer(static_cast<size_t>(size));
				if (kFile.read(&kBuffer[0], size))
				{
					szFileData = CvString(std::string(kBuffer.begin(), kBuffer.end()).c_str());
				}
			}
			kFile.close();
		}
	}
	if (!szFileData.empty())
	{
		SQLSchemaData kStruct;
		return kStruct.update(szFileData);
	}
	return false;
}

bool CvDatabaseManager::migrateDatabaseSchema()
{
	return exec(CvString("PRAGMA writable_schema = 1;"
		"DELETE FROM sqlite_master;"
		"PRAGMA writable_schema = 0;"
		"VACUUM;"));
	// TODO - Need to enumerate over all scripts and figure out how to run them...
	#if 0
	std::vector<CvString> aszFiles;
	gDLL->enumerateFiles(aszFiles, "SQL\\*_CvGameDatabaseMigrationScript.sql");
	for (std::vector<CvString>::iterator it = aszFiles.begin(); it != aszFiles.end(); ++it)
	{
		if (!ExecScript(*it)) // TODO - Need something that takes a pointer to the file location found in the vector and runs the SQL script through sqlite's exec function
			return false;
	}
	#endif
}

CvWString CvDatabaseManager::getLocationForFile()
{
	CvWString CvFilePath;
	{
		wchar_t szPath[MAX_PATH];
		// CSIDL_PERSONAL refers to the "My Documents" folder.
		// SHGFP_TYPE_CURRENT ensures we get the current path even if redirected (e.g., OneDrive).
		HRESULT hr = SHGetFolderPathW(NULL, CSIDL_PERSONAL, NULL, SHGFP_TYPE_CURRENT, szPath);
		if (SUCCEEDED(hr))
		{
			CvFilePath += (szPath + L"\\My Games\\Beyond the Sword\\");  // XANA (note): We'll put the game database inside the main BtS folder to keep it nominally safe from modification or deletion
			CvFilePath += (CvWString(GC.getModName().getName()) + L"\\"); // XANA (note): We'll use the mod folder's name for simplictiy's sake and to keep everything neat and tidy around here
		}
	}
	if (!CvFilePath.empty()) // XANA (note): If we successfully found the user's valid, writable My Documents folder (path not empty)
	{
		bool bValidLocation = true;
		{
			// XANA (note): Create the location for the database file if needed (otherwise verify that the directory structure already exists)
			size_t position = 0;
			do
			{
				// Find the next slash (handle both \ and / just in case)
				position = CvFilePath.find_first_of(L"\\/", position + 1);
				std::wstring directory = CvFilePath.substr(0, position);
				// Skip drive letters like "C:" to avoid access errors
				if (directory.length() > 0 && directory[directory.length() - 1] != L':')
				{
					if (!CreateDirectoryW(directory.c_str(), NULL))
					{
						DWORD error = GetLastError();
						// If it already exists, we are good to keep going, however if there was some other error then that is a problem and it means we should stop immediately
						if (error != ERROR_ALREADY_EXISTS)
						{
							bValidLocation = false;
							break;
						}
					}
				}
			}
			while (position != std::wstring::npos);
		}
		if (bValidLocation)
		{
			CvFilePath += L"CvGameDatabase"; // XANA (note): If the file somehow gets removed, that's fine for Civ4, it won't affect actual gameplay much since the game doesn't depend on SQL to function
			if (GC.getGame().isGameMultiPlayer())
			{
				CvFilePath += (L"-MP_" + GC.getGame().getName());
			}
			CvFilePath += L".sqlite"
			return CvFilePath;
		}
	}
	return L""; // If we reach this that means something has gone wrong with attempting sqlite database initialization, we shouldn't be trying to load any databases if we can't ensure the directory structure is okay to use
}