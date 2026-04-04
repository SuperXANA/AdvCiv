#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITETRANSACTION_H
#define CV_SQLITETRANSACTION_H

class SQLiteTransaction : private boost::noncopyable
{
public:
	SQLiteTransaction();
	~SQLiteTransaction();

	bool commit() const;
	bool rollback() const;
	bool isActive() const { return m_bActive; }

private:
	bool m_bActive;
	bool m_bCommitted;
};
#endif

