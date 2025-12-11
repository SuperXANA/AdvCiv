#include "CvGameCoreDLL.h"
#include "SQLiteStatement.h"

SQLiteStatement::~SQLiteStatement()
{
	if (ready())
	{
		finalize();
	}
}

void SQLiteStatement::finalize()
{
	if (ready())
	{
		sqlite3_finalize(m_statement);
		m_bFinalized = true;
	}
}