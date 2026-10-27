#!/usr/bin/env python3
"""Syntax-check the real Windows path body against minimal API/type declarations.
Not a Windows runtime test or ABI check; catches incomplete type and string-width
mistakes hidden by the portable database harness's substituted path function.
"""
import pathlib, subprocess, tempfile
root=pathlib.Path(__file__).resolve().parents[1]
source=(root/'CvGameCoreDLL/CvDatabaseManager.cpp').read_text()
assert source.startswith('#include "CvGameCoreDLL.h"\n')
assert '#include "CvGame.h"' in source
body=source[source.index('CvWString CvDatabaseManager::getLocationForFile()'):]
prelude=r'''
#include <string>
#include <cstddef>
#define __stdcall
#define WINAPI
#define MAX_PATH 260
#define SUCCEEDED(x) ((x)>=0)
#define ERROR_ALREADY_EXISTS 183
// Deliberately model CvWString's wide storage, not a permissive narrow stub.
class CvWString : public std::wstring { public:
 CvWString() {} CvWString(const wchar_t* s):std::wstring(s) {}
 CvWString(const std::wstring& s):std::wstring(s) {}
 CvWString(const std::string& s) { assign(s.begin(),s.end()); }
 CvWString(const char* s) { while(*s) push_back(*s++); }
};
typedef long HRESULT; typedef int BOOL; typedef unsigned long DWORD;
typedef void* HWND; typedef void* HANDLE; typedef void* HMODULE;
typedef const wchar_t* LPCWSTR; typedef void* LPSECURITY_ATTRIBUTES;
typedef void (*FARPROC)();
HMODULE LoadLibraryA(const char*); FARPROC GetProcAddress(HMODULE,const char*);
BOOL FreeLibrary(HMODULE); DWORD GetLastError();
class CvGame { public: bool isGameMultiPlayer() const; CvWString const& getName(); };
class ModName { public: std::string getName()const; };
class Globals { public: ModName getModName()const; CvGame& getGame()const; };
extern Globals GC;
class CvDatabaseManager { public: CvWString getLocationForFile(); };
'''
with tempfile.TemporaryDirectory(prefix='sqlite-winpath-') as td:
 p=pathlib.Path(td)/'path.cpp';p.write_text(prelude+body)
 subprocess.run(['g++','-std=c++03','-pedantic-errors','-Wall','-Wextra','-fsyntax-only',str(p)],check=True)
print('Windows path-body C++03 syntax/type check passed (stub APIs; no Windows runtime validation)')
