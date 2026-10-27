#include "CvGameCoreDLL.h"
#include "CvDatabaseManager.h"
#include "CvGame.h"
#include "SQLiteConnection.h"
#include "CvDatabaseFwd.h"
#include <fstream>

CvDatabaseManager::CvDatabaseManager() : m_sqlite(NULL), m_bDoCache(false), m_bSqlLoaded(false), m_bActive(false), m_iTransactionGeneration(0), m_bTransactionOpen(false)
{}

CvDatabaseManager::~CvDatabaseManager()
{
	uninit();
}

bool CvDatabaseManager::exec(const CvString& szSQL)
{
	if (!isValid() || !szSQL.GetCString())
	{
		return false;
	}
	bool bOK = m_sqlite->exec(szSQL);
	refreshTransactionState();
	return bOK;
}

// XANA: 10-27-2026 Configure connection-wide integrity before schema transactions.
bool CvDatabaseManager::configureConnection()
{
	if (m_sqlite == NULL || !m_sqlite->isValid())
		return false;
	installTransactionTracking();
	if (!m_sqlite->exec("PRAGMA foreign_keys = ON;"))
		return false;
	sqlite3_stmt* pStatement = NULL;
	if (!m_sqlite->prepare(pStatement, "PRAGMA foreign_keys;"))
		return false;
	bool bEnabled = sqlite3_step(pStatement) == SQLITE_ROW &&
		sqlite3_column_int(pStatement, 0) == 1;
	sqlite3_finalize(pStatement);
	return bEnabled;
}
// XANA: END connection integrity configuration.

// XANA: 10-27-2026 Observe boundaries before each statement and after execution.
// The trace callback catches intermediate COMMIT; BEGIN; boundaries in a batch,
// including read-only transactions that do not invoke SQLite's commit hook.
void CvDatabaseManager::installTransactionTracking()
{
	m_bTransactionOpen = sqlite3_get_autocommit(m_sqlite->m_database) == 0;
	sqlite3_trace(m_sqlite->m_database, traceTransactionState, this);
}

void CvDatabaseManager::traceTransactionState(void* pManager, const char*)
{
	static_cast<CvDatabaseManager*>(pManager)->refreshTransactionState();
}

void CvDatabaseManager::refreshTransactionState()
{
	bool bOpen = m_sqlite != NULL && m_sqlite->isValid() &&
		sqlite3_get_autocommit(m_sqlite->m_database) == 0;
	if (bOpen != m_bTransactionOpen)
	{
		++m_iTransactionGeneration;
		m_bTransactionOpen = bOpen;
	}
}

unsigned long CvDatabaseManager::getTransactionGeneration()
{
	refreshTransactionState();
	return m_iTransactionGeneration;
}

bool CvDatabaseManager::isTransactionCurrent(unsigned long iGeneration)
{
	refreshTransactionState();
	return isValid() && m_bTransactionOpen &&
		iGeneration == m_iTransactionGeneration;
}
// XANA: END transaction generation tracking.

bool CvDatabaseManager::isValid() const
{
	return ((m_sqlite && m_bActive && m_bSqlLoaded) ? m_sqlite->isValid() : false);
}

bool CvDatabaseManager::init()
{
	if (isValid())
		return true;
	if (!uninit())
		return false;
	// No schema has been supplied for this feature branch yet.
	if (SQL_SCHEMA_VERSION <= 0)
		return false;
	CvWString szDatabasePath(getLocationForFile());
	if (szDatabasePath.empty())
		return false;
	m_sqlite = new SQLiteConnection(szDatabasePath);
	if (!m_sqlite->open())
	{
		uninit();
		return false;
	}
	if (!configureConnection())
	{
		uninit();
		return false;
	}

	// XANA: 10-27-2026 Bootstrap through the private connection. Public queries
	// stay unavailable until the schema has been successfully verified.
	int iVersion = -1;
	bool bReady = testSchemaVersion(iVersion);
	if (!bReady && iVersion == 0)
		bReady = writeSchemaToDatabase();
	else if (!bReady && iVersion > 0 && iVersion < SQL_SCHEMA_VERSION)
		bReady = migrateDatabaseSchema();
	if (bReady)
		bReady = testSchemaVersion(iVersion);
	if (!bReady)
	{
		// Unknown/newer versions and failed reads must never erase user data.
		uninit();
		return false;
	}
	m_bActive = true;
	m_bSqlLoaded = true;
	m_bDoCache = true;
	return true;
}

bool CvDatabaseManager::uninit()
{
	++m_iTransactionGeneration;
	m_bTransactionOpen = false;
	m_bDoCache = false;
	clearStatementPool();
	m_bActive = false;
	m_bSqlLoaded = false;
	if (m_sqlite != NULL && m_sqlite->close())
		SAFE_DELETE(m_sqlite);
	// Outstanding borrowed statements can return safely, then close can retry.
	return m_sqlite == NULL;
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
			const char* szCachedSQL = sqlite3_sql(pStatement);
			if (szCachedSQL != NULL && szSQL == szCachedSQL)
				return pStatement;
			sqlite3_finalize(pStatement);
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
	if (isValid() && m_bDoCache && szKey.GetCString())
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
	iVersion = -1;
	if (m_sqlite == NULL || !m_sqlite->isValid())
		return false;
	sqlite3_stmt* pStatement = NULL;
	if (!m_sqlite->prepare(pStatement, "PRAGMA user_version;"))
		return false;
	if (sqlite3_step(pStatement) == SQLITE_ROW)
		iVersion = sqlite3_column_int(pStatement, 0);
	sqlite3_finalize(pStatement);
	// Version zero denotes an uninitialized schema, not a supported version.
	return SQL_SCHEMA_VERSION > 0 && iVersion == SQL_SCHEMA_VERSION;
}

bool CvDatabaseManager::writeSchemaToDatabase()
{
	CvString szFile(GC.getModName().getFullPath()); // XANA (note): This should resolve to "Mods\MLP Civilization is Magic" according to code comments surrounding the getFullPath function.
	if (!szFile.empty())
	{
		szFile += "\\Assets\\SQL\\CvGameDatabaseSchema.sql"; // XANA (note): The full path for a correct resolution is "Mods\MLP Civilization is Magic\Assets\SQL\CvGameDatabaseSchema.sql"
		return runSchemaScript(szFile);
	}
	return false;
}

bool CvDatabaseManager::migrateDatabaseSchema()
{
	// XANA: 10-27-2026 No version-indexed migration manifest is supplied yet.
	// Replaying every script can corrupt an already-partially-upgraded database.
	// Keep the existing file intact until explicit migration steps are defined.
	return false;
}

bool CvDatabaseManager::runSchemaScript(const CvString& szPath)
{
	if (!szPath.empty())
	{
		CvString szFileData;
		{
			std::ifstream kFile(szPath.GetCString(), std::ios::binary | std::ios::ate);
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
			if (m_sqlite == NULL || !m_sqlite->exec("BEGIN IMMEDIATE;"))
				return false;
			int iVersion = -1;
			bool bOK = m_sqlite->exec(szFileData) && testSchemaVersion(iVersion);
			if (bOK && m_sqlite->exec("COMMIT;"))
				return true;
			m_sqlite->exec("ROLLBACK;");
			return false;
		}
	}
	return false;
}

CvWString CvDatabaseManager::getLocationForFile()
{
	typedef HRESULT (__stdcall *FN_SHGetFolderPathW)(HWND, int, HANDLE, DWORD, wchar_t*);
	HMODULE hShell = LoadLibraryA("shell32.dll");
	if (!hShell) return ""; // If we can't load "shell32.lib" Windows library dynamically, fail early to avoid loading sqlite3 data from an invalid location.
	FN_SHGetFolderPathW pGetOSFilePath = reinterpret_cast<FN_SHGetFolderPathW>(GetProcAddress(hShell, "SHGetFolderPathW"));
	CvWString CvFilePath;
	if (pGetOSFilePath)
	{
		wchar_t szPath[MAX_PATH];
		szPath[0] = 0;
		// CSIDL_PERSONAL refers to the "My Documents" folder.
		// SHGFP_TYPE_CURRENT ensures we get the current path even if redirected (e.g., OneDrive).
		if (SUCCEEDED(pGetOSFilePath(NULL, /* CSIDL_PERSONAL: 0x0005 */ 0x0005, NULL, /* SHGFP_TYPE_CURRENT: 0 */ 0, szPath)) && szPath[0])
		{
			CvFilePath += (CvWString(szPath) + L"\\My Games\\");  // XANA (note): We'll put the game database inside the usual My Games folder to keep it nominally safe from modification or deletion
			CvFilePath += (CvWString(GC.getModName().getName()) + L"\\"); // XANA (note): We'll use the mod folder's name for simplictiy's sake and to keep everything neat and tidy around here
		}
	}
	FreeLibrary(hShell);
	if (!CvFilePath.empty()) // XANA (note): If we successfully found the user's valid, writable My Documents folder (path not empty)
	{
		bool bValidLocation = true;
		{
			typedef BOOL (WINAPI *PFN_CreateDirectoryW)(LPCWSTR, LPSECURITY_ATTRIBUTES);
			HMODULE hKernel = LoadLibraryA("kernel32.dll");
			if (!hKernel) return ""; // If we can't load "kernel32.lib" Windows library dynamically, fail early to avoid loading sqlite3 data from an invalid location.
			PFN_CreateDirectoryW pCreateOSDir = reinterpret_cast<PFN_CreateDirectoryW>(GetProcAddress(hKernel, "CreateDirectoryW"));
			if (pCreateOSDir)
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
						if (!pCreateOSDir(directory.c_str(), NULL))
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
			else bValidLocation = false;
			FreeLibrary(hKernel);
		}
		if (bValidLocation)
		{
			CvFilePath += L"CvGameDatabase"; // XANA (note): If the file somehow gets removed, that's fine for Civ4, it won't affect actual gameplay much since the game doesn't depend on SQL to function
			if (GC.getGame().isGameMultiPlayer())
			{
				CvFilePath += (L"-MP_" + GC.getGame().getName());
			}
			CvFilePath += L".sqlite";
			return CvFilePath;
		}
	}
	return ""; // If we reach this that means something has gone wrong with attempting sqlite database initialization, we shouldn't be trying to load any databases if we can't ensure the directory structure is okay to use
}
