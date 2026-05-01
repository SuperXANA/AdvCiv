#pragma once

#ifndef CV_SQLITEFWD_H
#define CV_SQLITEFWD_H

// Silence specific MSVC 7.1 warnings for this code block during inclusion
#pragma warning(push)
#pragma warning(disable: 4100) // Unreferenced formal parameter
#pragma warning(disable: 4244) // Conversion, possible loss of data
#pragma warning(disable: 4018) // Signed/unsigned mismatch

extern "C"
{
	#include "sqlite3.h"
}

#pragma warning(pop) // Restore original Civ4 mod warning levels

#endif