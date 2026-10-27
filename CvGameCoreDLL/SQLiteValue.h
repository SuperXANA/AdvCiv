#pragma once

#include "CvGameCoreDLL.h"
// XANA: 10-27-2026 Check integer conversion bounds before narrowing.
#include <cerrno>
#include <climits>
#include <cstdlib>
// XANA: END integer conversion includes.

#ifndef CV_SQLITEVALUE_H
#define CV_SQLITEVALUE_H

// XANA: 10-27-2026 Values own their data and must be copyable in C++03.
class SQLiteValue
{
public:
	SQLiteValue() : m_eType(NULL_TYPE) { m_data.i = 0; }
	explicit SQLiteValue(int val) : m_eType(INTEGER) { m_data.i = val; }
	explicit SQLiteValue(bool val) : m_eType(INTEGER) { m_data.i = (val ? static_cast<int>(true) : static_cast<int>(false)); }
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
				// XANA: 10-27-2026 Compare before casting; NaN also fails these bounds.
				// Truncation toward zero permits fractions just outside the endpoints.
				double const dLower = static_cast<double>(INT_MIN) - 1.0;
				double const dUpper = static_cast<double>(INT_MAX) + 1.0;
				return (m_data.d > dLower && m_data.d < dUpper) ?
					static_cast<int>(m_data.d) : 0;
				// XANA: END floating-to-integer range guard.
			}
			case TEXT:
			{
				// XANA: 10-27-2026 strtol reports overflow before narrowing to int.
				// Keep atoi's decimal-prefix behavior for ordinary text.
				errno = 0;
				long const iValue = std::strtol(m_szValue.GetCString(), NULL, 10);
				return (errno != ERANGE && iValue >= INT_MIN && iValue <= INT_MAX) ?
					static_cast<int>(iValue) : 0;
				// XANA: END text-to-integer range guard.
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
			case TEXT:
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
	operator bool() const { return operator int() != static_cast<int>(false); }
	operator CvString() const
	{
		switch (m_eType)
		{
			case TEXT:
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
				return CvString();
			}
		}
	}
	operator scaled() const
	{ 
		double const d = operator double();
		return (d >= scaled::MIN && d <= scaled::MAX) ? scaled::fromDouble(d) : scaled();
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