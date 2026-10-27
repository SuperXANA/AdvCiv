#ifndef TEST_WINDOWS_H
#define TEST_WINDOWS_H
#include <pthread.h>
#include <cstdlib>
#include <cstring>
#include <cassert>
typedef unsigned long DWORD;
typedef int BOOL;
typedef void* HANDLE;
typedef void* LPVOID;
#define HEAP_ZERO_MEMORY 8
struct CRITICAL_SECTION { pthread_mutex_t mutex; };
inline void InitializeCriticalSection(CRITICAL_SECTION* p) { pthread_mutexattr_t attr; pthread_mutexattr_init(&attr); pthread_mutexattr_settype(&attr,PTHREAD_MUTEX_RECURSIVE); pthread_mutex_init(&p->mutex,&attr); pthread_mutexattr_destroy(&attr); }
inline void DeleteCriticalSection(CRITICAL_SECTION* p) { pthread_mutex_destroy(&p->mutex); }
inline void EnterCriticalSection(CRITICAL_SECTION* p) { pthread_mutex_lock(&p->mutex); }
inline void LeaveCriticalSection(CRITICAL_SECTION* p) { pthread_mutex_unlock(&p->mutex); }
inline HANDLE GetProcessHeap() { return reinterpret_cast<HANDLE>(1); }
inline LPVOID HeapAlloc(HANDLE,DWORD flags,size_t bytes) { return flags & HEAP_ZERO_MEMORY ? std::calloc(1,bytes) : std::malloc(bytes); }
inline BOOL HeapFree(HANDLE,DWORD,LPVOID ptr) { std::free(ptr); return 1; }
inline DWORD GetCurrentThreadId() { return (DWORD)pthread_self(); }
inline void ZeroMemory(void* p,size_t n) { std::memset(p,0,n); }
#endif
