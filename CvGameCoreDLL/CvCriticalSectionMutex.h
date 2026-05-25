#pragma once

#ifndef CIV4_MUTEX_H
#define CIV4_MUTEX_H
	
#include <windows.h>

// 1. The Critical Section wrapper manages the lock's system resources
class CvCriticalSection
{
private:
	CRITICAL_SECTION cs_;

	// Prevent copying (Crucial for C++03)
	CvCriticalSection(const CvCriticalSection&);
	CvCriticalSection& operator=(const CvCriticalSection&);

public:
	CvCriticalSection()
	{
		InitializeCriticalSection(&cs_);
	}
	~CvCriticalSection()
	{
		DeleteCriticalSection(&cs_);
	}
	void lock()
	{
		EnterCriticalSection(&cs_);
	}
	void unlock()
	{
		LeaveCriticalSection(&cs_);
	}
};

// 2. The RAII Scoped Lock automates lock acquisition and release
class CvFunctionMutex
{
private:
	CvCriticalSection& cs_ref_;

	// Prevent copying to avoid multiple destructors unlocking the same resource
	CvFunctionMutex(const CvFunctionMutex&);
	CvFunctionMutex& operator=(const CvFunctionMutex&);

public:
	// Lock automatically happens on construction
	explicit CvFunctionMutex(CvCriticalSection& cs) : cs_ref_(cs)
	{
		cs_ref_.lock();
	}

	// Unlock automatically happens on destruction (even during exceptions)
	~CvFunctionMutex()
	{
		cs_ref_.unlock();
	}
};

#endif