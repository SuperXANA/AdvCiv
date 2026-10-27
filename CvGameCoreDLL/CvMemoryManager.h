#pragma once

#ifndef CV_MEMORY_MANAGER_H
#define CV_MEMORY_MANAGER_H

// advc.003o: Cut from CvGameCoreDLL.h

#define SAFE_DELETE(p)			{ if(p) { delete (p);     (p)=NULL; } }
#define SAFE_DELETE_ARRAY(p)	{ if(p) { delete[] (p);   (p)=NULL; } }
#define SAFE_RELEASE(p)			{ if(p) { (p)->Release(); (p)=NULL; } }
// <advc.006>
#define ASSERT_DELETE(p) \
{ \
	if ((p) == NULL) \
	{ \
		FAssertMsg((p) != NULL, "Attempted to free memory twice"); \
		return; \
	} \
	delete (p); \
} // </advc.006>

// Deletes a 2D array (array of pointers to arrays)
// p: The double pointer array (e.g., m_aiiDoubleArray)
// size: The size of the outer array (e.g., numRows, or GC.getNumTraitInfos())
#define SAFE_DELETE_2D_ARRAY(p, size) \
 /* XANA (note): The do {...} while(false) loop causes the macro statement to run only once, and forces the macro to require a semicolon after it */ \
    do \
	{ \
		if (p != NULL) \
		{ \
            for (int i = 0; i < (size); ++i) \
			{ \
                SAFE_DELETE_ARRAY(p[i]); /* Reuse the simple array macro */ \
            } \
            SAFE_DELETE_ARRAY(p); /* Reuse the simple array macro */ \
        } \
    } \
	while (false)

#ifdef _DEBUG
//#define MEMORY_TRACKING
#endif

#ifdef MEMORY_TRACKING
class CMemoryTrack
{
#define	MAX_TRACKED_ALLOCS	1000
	void*	m_track[MAX_TRACKED_ALLOCS];
	int		m_highWater;
	const char* m_name;
	bool	m_valid;
#define MAX_TRACK_DEPTH		50
	static	CMemoryTrack*	trackStack[MAX_TRACK_DEPTH];
	static	m_trackStackDepth;

public:
	CMemoryTrack(const char* name, bool valid);

	~CMemoryTrack();

	void NoteAlloc(void* ptr);
	void NoteDeAlloc(void* ptr);

	static CMemoryTrack* GetCurrent(void);
};

class CMemoryTrace
{
	int		m_start;
	const char* m_name;

public:
	CMemoryTrace(const char* name);

	~CMemoryTrace();
};

void DumpMemUsage(const char* fn, int line);

#define DUMP_MEMORY_USAGE()	DumpMemUsage(__FUNCTION__,__LINE__);
#define MEMORY_TRACK()	CMemoryTrack __memoryTrack(__FUNCTION__, true);
#define MEMORY_TRACK_EXEMPT()	CMemoryTrack __memoryTrackExemption(NULL, false);
#define MEMORY_TRACE_FUNCTION()	CMemoryTrace __memoryTrace(__FUNCTION__);
#else
#define DUMP_MEMORY_USAGE()
#define	MEMORY_TRACK()
#define MEMORY_TRACK_EXEMPT()
#define MEMORY_TRACE_FUNCTION()
#endif

#endif
