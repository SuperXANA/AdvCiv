#pragma once

#include "CvGameCoreDLL.h"
extern "C" { #include "sqlite3.h" }

class SQLiteException : private boost::noncopyable
{
public:
	SQLiteException(int rc) : sqliteReturnCode(rc) {}
private:
	void log(char* context) { gDLL->messageControlLog(context +" SQLite Error #"+sqliteReturnCode+": "+sqlite3_errmsg(DB.getSQLite())); }
	int sqliteReturnCode;
};