#!/usr/bin/env python3
"""C++03 regression tests of production SQLite wrappers with minimal Civ stubs.
Builds the bundled 3.7.5 engine by default; SQLITE_TEST_LIBRARY can override
the link library. This is not a Civ4 DLL/in-game test. The generated
manager replaces only its Windows path-discovery function with a test path.
"""
import os, pathlib, shutil, subprocess, tempfile, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
STUB=r'''
#ifndef TEST_CIV_H
#define TEST_CIV_H
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cstdarg>
#include <climits>
namespace boost { class noncopyable { protected: noncopyable() {} ~noncopyable() {} private: noncopyable(const noncopyable&); noncopyable& operator=(const noncopyable&); }; }
namespace stdext { template<class K,class V> class hash_map : public std::map<K,V> {}; }
class CvString : public std::string { public:
 CvString() {} CvString(const char* x):std::string(x ? x : "") {} CvString(const std::string& x):std::string(x) {}
 const char* GetCString() const { return c_str(); } int GetLength()const{return size();}
 static CvString format(const char* x,...) { char b[2048];va_list a;va_start(a,x);vsnprintf(b,sizeof(b),x,a);va_end(a);return b; }
};
class CvWString { std::basic_string<unsigned short> s; public:
 CvWString() {} CvWString(const char* x) { while(*x) s+=static_cast<unsigned short>(*x++); }
 bool empty()const{return s.empty();} const unsigned short* GetCString()const{return s.c_str();}
};
class scaled { double d; public: scaled(double x=0,int div=1):d(x/div){} operator int()const{return static_cast<int>(d);} };
class CvDatabaseManager; extern CvDatabaseManager g_database;
#define DB g_database
#define SAFE_DELETE(x) do { delete (x); (x)=NULL; } while(0)
#define PROFILE_FUNC() ((void)0)
#include "CvDatabaseSchema.h"
struct TestMod { CvString getFullPath()const{return ".";} };
struct TestGlobals { TestMod getModName()const{return TestMod();} }; extern TestGlobals GC;
#endif
'''
TEST=r'''
#include "CvGameCoreDLL.h"
#define private public
#include "CvDatabaseManager.h"
#include "SQLiteConnection.h"
#include "SQLiteStatement.h"
#include "SQLiteTransaction.h"
#include "SQLiteValue.h"
#include "CvDatabaseQuery.h"
#undef private
#include "CvDatabaseFwd.h"
#include <cassert>
#include <iostream>
CvDatabaseManager g_database; TestGlobals GC; CvString testDatabasePath(":memory:");
static int countRows() { SQLiteStatement s("count","SELECT count(*) AS n FROM t"); assert(s.exec());return s.getInt("n"); }
int main() {
 // Missing schema/version zero remains disabled, and init failure is retryable.
 assert(!DB.init());assert(!DB.isValid());assert(DB.m_sqlite==NULL);assert(!DB.init());
#if SQL_SCHEMA_VERSION > 0
 sqlite3* disk=NULL;assert(sqlite3_open("newer.db",&disk)==SQLITE_OK);
 assert(sqlite3_exec(disk,"CREATE TABLE sentinel(v); INSERT INTO sentinel VALUES(73); PRAGMA user_version=2",NULL,NULL,NULL)==SQLITE_OK);sqlite3_close(disk);
 testDatabasePath="newer.db";assert(!DB.init());assert(DB.m_sqlite==NULL);
 assert(sqlite3_open("newer.db",&disk)==SQLITE_OK);sqlite3_stmt* saved=NULL;
 assert(sqlite3_prepare_v2(disk,"SELECT v FROM sentinel",-1,&saved,NULL)==SQLITE_OK);assert(sqlite3_step(saved)==SQLITE_ROW);assert(sqlite3_column_int(saved,0)==73);sqlite3_finalize(saved);
 assert(sqlite3_prepare_v2(disk,"PRAGMA user_version",-1,&saved,NULL)==SQLITE_OK);assert(sqlite3_step(saved)==SQLITE_ROW);assert(sqlite3_column_int(saved,0)==2);sqlite3_finalize(saved);sqlite3_close(disk);testDatabasePath=":memory:";
#endif
 // Tests below explicitly provide a ready in-memory DB; no game schema is invented.
 DB.m_sqlite=new SQLiteConnection(CvWString(":memory:"));assert(DB.m_sqlite->open());
 // Bootstrap runs while public gameplay access remains disabled.
 assert(!DB.isValid());
 { std::ofstream script("bad.sql");script<<"CREATE TABLE partial(v); THIS IS INVALID;"; }
 assert(!DB.runSchemaScript("bad.sql"));
 sqlite3_stmt* probe=NULL;assert(!DB.m_sqlite->prepare(probe,"SELECT * FROM partial"));
#if SQL_SCHEMA_VERSION > 0
 { std::ofstream script("schema.sql");script<<"CREATE TABLE fixture(v); PRAGMA user_version=1;"; }
 assert(DB.runSchemaScript("schema.sql"));int version=-1;assert(DB.testSchemaVersion(version));assert(version==1);
 assert(DB.m_sqlite->exec("PRAGMA user_version=2"));assert(!DB.testSchemaVersion(version));assert(version==2);
 assert(DB.m_sqlite->prepare(probe,"SELECT * FROM fixture"));sqlite3_finalize(probe);
#endif
 DB.m_bActive=DB.m_bSqlLoaded=DB.m_bDoCache=true;
 assert(DB.exec("CREATE TABLE t(v INTEGER UNIQUE, txt TEXT)"));
 { SQLiteStatement s("insert","INSERT INTO t VALUES(:v,:txt)");assert(s.bind(":v",1));assert(s.bind(":txt","one")); assert(s.exec());assert(s.getLastResult()==SQLITE_DONE);assert(!s.exec()); }
 assert(countRows()==1);
 { SQLiteStatement s("insert","INSERT INTO t VALUES(:v,:txt)");assert(s.bind(":v",1));assert(!s.exec());assert(s.getLastResult()==SQLITE_CONSTRAINT); }
 { SQLiteStatement s("select","SELECT v,txt FROM t");assert(s.next());assert(s.getInt("v")==1);assert(s.getText("txt")=="one");assert(!s.hasRow(2));assert(!s.hasRow(-1));assert(!s.next());assert(!s.next()); }
 // Parameter maps are initialized, names expose stable c_str() data.
 { SQLiteStatement s("params","SELECT :p AS result");assert(s.hasBinding(":p"));assert(s.bind(":p",7));assert(s.exec());assert(s.getInt("result")==7);assert(std::string(s.getParameterName(1))==":p");assert(std::string(s.getColumnName(0))=="result");SQLiteValue v=s.getValue(0);assert(int(v)==7); }
 // Reusing a cache key with new SQL must not execute the old SQL.
 { SQLiteStatement s("collision","SELECT 11 AS n");assert(s.exec());assert(s.getInt(0)==11); }
 { SQLiteStatement s("collision","SELECT 22 AS n");assert(s.exec());assert(s.getInt(0)==22);assert(s.prepare("SELECT 33 AS n"));assert(s.exec());assert(s.getInt(0)==33);s.reset(false);assert(s.prepare("SELECT :newparam AS newcolumn"));assert(s.bind(":newparam",44));assert(s.exec());assert(s.getInt("newcolumn")==44); }
 { SQLiteStatement s("null","SELECT NULL AS n");assert(s.exec());assert(s.getText(0).empty());assert(s.isNull(0)); }
 { SQLiteTransaction t;assert(t.isActive());assert(DB.exec("INSERT INTO t VALUES(2,'rollback')")); }
 assert(countRows()==1);
 { SQLiteTransaction t;assert(t.commit());assert(t.wasCommitted());assert(t.begin());assert(t.isActive());assert(!t.wasCommitted());assert(DB.exec("INSERT INTO t VALUES(2,'committed')"));assert(t.commit()); }
 assert(countRows()==2);
 { SQLiteTransaction outer;SQLiteTransaction nested;assert(!nested.isActive());assert(!nested.commit());assert(outer.rollback()); }
 // Outstanding statement remains usable until returned, close fails safely.
 { SQLiteStatement borrowed("borrowed","SELECT 1");assert(borrowed.isPrepared());assert(!DB.uninit());assert(DB.m_sqlite!=NULL);assert(borrowed.exec());assert(borrowed.getInt(0)==1);borrowed.finalize();assert(DB.uninit()); }
 assert(DB.m_sqlite==NULL);
 { SQLiteConnection c(CvWString("/nonexistent/sqlite-test/file.db"));assert(!c.open());assert(c.m_database==NULL);assert(c.close()); }
 { CvDatabaseQuery q;assert(q.select("'100%' AS text").getSQLString()=="SELECT '100%' AS text"); }
 std::cout<<"SQLite wrapper regressions passed; runtime "<<sqlite3_libversion()<<"\n";
}
'''
with tempfile.TemporaryDirectory(prefix='advciv-sqlite-') as td:
 d=pathlib.Path(td)
 names=['SQLiteConnection','SQLiteStatement','SQLiteTransaction','CvDatabaseQuery','CvDatabaseManager']
 for n in names:
  for ext in ['h','cpp']: shutil.copy(ROOT/'CvGameCoreDLL'/(n+'.'+ext),d)
 for n in ['CvDatabaseFwd.h','CvDatabaseSchema.h','SQLiteValue.h']:shutil.copy(ROOT/'CvGameCoreDLL'/n,d)
 if os.environ.get('SQLITE_TEST_SCHEMA_FIXTURE'):
  header=d/'CvDatabaseSchema.h';header.write_text(header.read_text().replace('SQL_SCHEMA_VERSION (0)','SQL_SCHEMA_VERSION (1)'))
 (d/'sqlite').mkdir();shutil.copy(ROOT/'CvGameCoreDLL/sqlite/sqlite3.h',d/'sqlite')
 manager=d/'CvDatabaseManager.cpp';s=manager.read_text();s=s[:s.index('CvWString CvDatabaseManager::getLocationForFile()')]+'''extern CvString testDatabasePath; CvWString CvDatabaseManager::getLocationForFile() { return CvWString(testDatabasePath.c_str()); }\n''';manager.write_text(s)
 (d/'CvGameCoreDLL.h').write_text(STUB);(d/'test.cpp').write_text(TEST)
 lib=os.environ.get('SQLITE_TEST_LIBRARY')
 if not lib:
  # Use exactly the same upstream core source manifest as the Windows build.
  manifest=(ROOT/'CvGameCoreDLL/BuildSQLite/Makefile.sqlite').read_text()
  sources=re.findall(r'\$\(SQLITE_OBJ_DIR\)\\([a-zA-Z0-9_]+)\.obj',manifest)
  sources=list(dict.fromkeys(sources));assert len(sources)==83
  objects=[]
  for name in sources:
   obj=d/(name+'.o');objects.append(str(obj))
   subprocess.run(['gcc','-std=c89','-w','-DSQLITE_CORE','-DSQLITE_THREADSAFE=1','-DSQLITE_OMIT_LOAD_EXTENSION','-I',str(ROOT/'CvGameCoreDLL/sqlite'),'-c',str(ROOT/'CvGameCoreDLL/sqlite'/(name+'.c')),'-o',str(obj)],check=True)
  lib=str(d/'libsqlite3_375.a');subprocess.run(['ar','rcs',lib]+objects,check=True)
 cmd=['g++','-std=c++03','-pedantic-errors','-Wall','-Wextra','-Wno-unknown-pragmas','-Wno-long-long','-g','-I',str(d)]+[str(d/(n+'.cpp')) for n in names]+[str(d/'test.cpp'),lib,'-ldl','-lpthread','-o',str(d/'test')]
 if os.environ.get('SQLITE_TEST_SANITIZE'):cmd[1:1]=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(cmd,check=True);subprocess.run([str(d/'test')],check=True,cwd=d)
