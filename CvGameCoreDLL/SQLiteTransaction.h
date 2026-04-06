#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITETRANSACTION_H
#define CV_SQLITETRANSACTION_H

class SQLiteTransaction : private boost::noncopyable
{
public:
	SQLiteTransaction();
	~SQLiteTransaction();

	bool sqlReady() const;
	bool commit();
	bool rollback();
	bool isActive() const { return m_bActive; }
	bool wasCommitted() const { return m_bCommitted; }
	bool isValid() const { return (isActive() && !wasCommitted()); }
	
private:
	bool m_bActive;
	bool m_bCommitted;
};
#endif

