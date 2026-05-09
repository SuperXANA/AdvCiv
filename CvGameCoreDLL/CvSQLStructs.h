#pragma once

#include "CvDatabaseSchema.h"

#ifndef CVSQLSTRUCTS_H
#define CVSQLSTRUCTS_H

class CvDatabaseManager;
class CvDatabaseQuery;
class SQLiteTransaction;
class SQLiteStatement;
class SQLiteValue;

struct SQLSchemaData
{
	int query();
	bool update(const CvString& szSQL);
};


#endif	// CVSQLSTRUCTS_H