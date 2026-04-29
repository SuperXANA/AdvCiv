#pragma once

#include "CvGameCoreDLL.h"

#ifndef CV_SQLITEVALUE_H
#define CV_SQLITEVALUE_H

class SQLiteValue : private boost::noncopyable
{
public:
	SQLiteValue() : m_eType(NULL_TYPE) { m_data.i = 0; }
	explicit SQLiteValue(int val) : m_eType(INTEGER) { m_data.i = val; }
	explicit SQLiteValue(bool val) : m_eType(INTEGER) { m_data.i = (val ? (static_cast<int>true) : (static_cast<int>false)); }
	explicit SQLiteValue(double val) : m_eType(FLOAT) { m_data.d = val; }
	explicit SQLiteValue(const CvString& val) : m_eType(TEXT) { m_data.i = 0; m_szValue = val; }
	operator int() const
	{
		switch (m_eType)
		{
			case INTEGER:
			{
				return m_data.i;
			}
			case FLOAT:
			{
				return (int)m_data.d;
			}
			case TEXT;
			{
				return atoi(m_szValue.GetCString());
			}
			default:
			{
				return 0;
			}
		}
	}
	operator double() const
	{
		switch (m_eType)
		{
			case FLOAT:
			{
				return m_data.d;
			}
			case INTEGER:
			{
				return (double)m_data.i;
			}
			case TEXT;
			{
				return atof(m_szValue.GetCString());
			}
			default:
			{
				return 0;
			}
		}
	}
	operator float() const { return (float)operator double(); }
	operator bool() const { return operator int() != (static_cast<int>false); }
	operator CvString() const
	{
		switch (m_eType)
		{
			case TEXT;
			{
				return m_szValue;
			}
			case INTEGER:
			{
				std::ostringstream kStream;
				kStream << m_data.i;
				return CvString(kStream.str());
			}
			case FLOAT:
			{
				std::ostringstream kStream;
				kStream << m_data.d;
				return CvString(kStream.str());
			}
			default:
			{
				return CvString(NULL);
			}
		}
	}
	operator scaled() const
	{ 
		return scaled(operator float(), 100); 
	}
	bool isNull() const
	{ 
		return (m_eType == NULL_TYPE); 
	}

private:
	enum Type { NULL_TYPE, INTEGER, FLOAT, TEXT };
	Type m_eType;
	union Data
	{
		int i;
		double d;
	} m_data;
	CvString m_szValue;
};
#endif