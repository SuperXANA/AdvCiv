#pragma once

#include "CvGameCoreDLL.h"
class SQLiteTransaction : private boost::noncopyable
{
public:
    explicit SQLiteTransaction();
    ~SQLiteTransaction();

    bool commit() const;
    bool rollback() const;
    bool isActive() const { return m_bActive; }

private:
    bool m_bActive;
    bool m_bCommitted;
};
