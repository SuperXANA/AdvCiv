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
#include <cmath>
#include <limits>
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
// Match the production scaled API: integral ratio constructors, explicit
// floating conversion, and 1/2048 precision. A double ratio stub hid truncation.
class scaled { int i; public:
 enum { MIN=INT_MIN/2048, MAX=INT_MAX/2048 };
 scaled():i(0){} scaled(int n):i(n*2048){} scaled(unsigned n):i(n*2048){}
 scaled(int n,int den):i(n*2048/den){} scaled(unsigned n,unsigned den):i(n*2048/den){}
 static scaled fromDouble(double d) { scaled r;r.i=static_cast<int>(std::floor(d*2048+0.5));return r; }
 double getDouble()const{return i/2048.0;}
};
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
 assert(DB.configureConnection());
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
 // Declared relationships must reject orphans and apply cascades.
 assert(DB.exec("CREATE TABLE parent(id INTEGER PRIMARY KEY); CREATE TABLE child(pid INTEGER REFERENCES parent(id) ON DELETE CASCADE)"));
 assert(!DB.exec("INSERT INTO child VALUES(999)"));
 assert(DB.exec("INSERT INTO parent VALUES(1); INSERT INTO child VALUES(1); DELETE FROM parent WHERE id=1"));
 { SQLiteStatement s("children", "SELECT count(*) FROM child");assert(s.exec());assert(s.getInt(0)==0); }
 { SQLiteStatement s("insert","INSERT INTO t VALUES(:v,:txt)");assert(s.bind(":v",1));assert(s.bind(":txt","one")); assert(s.exec());assert(s.getLastResult()==SQLITE_DONE);assert(!s.exec()); }
 assert(countRows()==1);
 { SQLiteStatement s("insert","INSERT INTO t VALUES(:v,:txt)");assert(s.bind(":v",1));assert(!s.exec());assert(s.getLastResult()==SQLITE_CONSTRAINT); }
 { SQLiteStatement s("select","SELECT v,txt FROM t");assert(s.next());assert(s.getInt("v")==1);assert(s.getText("txt")=="one");assert(!s.hasRow(2));assert(!s.hasRow(-1));assert(!s.next());assert(!s.next()); }
 // Parameter maps are initialized, names expose stable c_str() data.
 { SQLiteStatement s("params","SELECT :p AS result");assert(s.hasBinding(":p"));assert(s.bind(":p",7));assert(s.exec());assert(s.getInt("result")==7);assert(std::string(s.getParameterName(1))==":p");assert(std::string(s.getColumnName(0))=="result");SQLiteValue v=s.getValue(0);assert(int(v)==7); }
 // Invalid database doubles must not overflow the fixed-point conversion.
 { SQLiteStatement s("scaled-range","SELECT 1e100 AS n");assert(s.exec());assert(s.getScaled("n").getDouble()==0); }
 { SQLiteValue v(std::numeric_limits<double>::quiet_NaN());assert(v.operator scaled().getDouble()==0); }
 { SQLiteValue v(std::numeric_limits<double>::infinity());assert(v.operator scaled().getDouble()==0); }
 { SQLiteValue v(double(scaled::MIN));assert(v.operator scaled().getDouble()==scaled::MIN); }
 { SQLiteValue v(double(scaled::MAX));assert(v.operator scaled().getDouble()==scaled::MAX); }
 // Reusing a cache key with new SQL must not execute the old SQL.
 { SQLiteStatement s("collision","SELECT 11 AS n");assert(s.exec());assert(s.getInt(0)==11); }
 { SQLiteStatement s("collision","SELECT 22 AS n");assert(s.exec());assert(s.getInt(0)==22);assert(s.prepare("SELECT 33 AS n"));assert(s.exec());assert(s.getInt(0)==33);s.reset(false);assert(s.prepare("SELECT :newparam AS newcolumn"));assert(s.bind(":newparam",44));assert(s.exec());assert(s.getInt("newcolumn")==44); }
 { SQLiteStatement s("null","SELECT NULL AS n");assert(s.exec());assert(s.getText(0).empty());assert(s.isNull(0)); }
 { SQLiteTransaction t;assert(t.isActive());assert(DB.exec("INSERT INTO t VALUES(2,'rollback')")); }
 assert(countRows()==1);
 { SQLiteTransaction t;assert(t.commit());assert(t.wasCommitted());assert(t.begin());assert(t.isActive());assert(!t.wasCommitted());assert(DB.exec("INSERT INTO t VALUES(2,'committed')"));assert(t.commit()); }
 assert(countRows()==2);
 { SQLiteTransaction outer;SQLiteTransaction nested;assert(!nested.isActive());assert(!nested.commit());assert(outer.rollback()); }


 // Failed reuse must not report the success of an earlier transaction.
 { SQLiteTransaction reused;assert(reused.commit());SQLiteTransaction outer;
   assert(!reused.begin());assert(!reused.wasCommitted());assert(!reused.commit());assert(outer.rollback()); }
 // OR ROLLBACK ends ownership; stale objects cannot act on a newer transaction.
 { SQLiteTransaction old;
   assert(!DB.exec("INSERT OR ROLLBACK INTO t VALUES(1,'duplicate')"));assert(!old.isActive());
   SQLiteTransaction current;assert(current.isActive());
   assert(DB.exec("INSERT INTO t VALUES(91,'current')"));
   assert(!old.commit());assert(!old.rollback());assert(current.rollback()); }
 assert(countRows()==2);
 // The same ownership check is required after a prepared statement fails.
 { SQLiteTransaction old;SQLiteStatement conflict("rollback-conflict", "INSERT OR ROLLBACK INTO t VALUES(1,'duplicate')");
   assert(!conflict.exec());assert(!old.isActive());SQLiteTransaction current;
   assert(!old.commit());assert(current.rollback()); }
 // Transaction boundaries inside one exec string must also invalidate ownership.
 { SQLiteTransaction old;assert(DB.exec("COMMIT; BEGIN;"));assert(!old.isActive());
   assert(!old.commit());assert(!old.rollback());assert(DB.exec("ROLLBACK")); }
 // Destruction of an old wrapper must leave a current transaction active.
 { SQLiteTransaction* old=new SQLiteTransaction;
   assert(DB.exec("ROLLBACK; BEGIN;"));delete old;assert(DB.exec("ROLLBACK")); }

 // Fractional scaled data keeps its value across binding and both read APIs.
 { SQLiteStatement s("scaled", "SELECT :positive AS pos, :negative AS neg");
   assert(s.bind(":positive",scaled(5,4)));assert(s.bind(":negative",scaled(-5,2)));
   assert(s.exec());assert(s.getDouble("pos")==1.25);assert(s.getDouble("neg")==-2.5);
   assert(s.getScaled("pos").getDouble()==1.25);assert(s.getScaled("neg").getDouble()==-2.5);
   scaled pos=s.getValue("pos");scaled neg=s.getValue("neg");
   assert(pos.getDouble()==1.25);assert(neg.getDouble()==-2.5);
 }
 // SQLite v2 statements can recompile on step after a schema change.
 assert(DB.exec("CREATE TABLE metadata(a); INSERT INTO metadata VALUES(3)"));
 { SQLiteStatement s("metadata", "SELECT * FROM metadata");assert(s.exec());assert(s.getInt("a")==3); }
 assert(DB.exec("ALTER TABLE metadata ADD COLUMN b DEFAULT 7"));
 { SQLiteStatement s("metadata", "SELECT * FROM metadata");assert(s.exec());assert(s.hasColumn("b"));assert(s.getInt("b")==7); }
 // An equal-size result can change names too; count-only invalidation is insufficient.
 assert(DB.exec("CREATE VIEW metadata_view AS SELECT a AS before FROM metadata"));
 { SQLiteStatement s("viewmetadata", "SELECT * FROM metadata_view");assert(s.exec());assert(s.getInt("before")==3); }
 assert(DB.exec("DROP VIEW metadata_view; CREATE VIEW metadata_view AS SELECT a AS after FROM metadata"));
 { SQLiteStatement s("viewmetadata", "SELECT * FROM metadata_view");assert(s.exec());assert(!s.hasColumn("before"));assert(s.getInt("after")==3); }

 // Outstanding statement remains usable until returned, close fails safely.
 { SQLiteStatement borrowed("borrowed","SELECT 1");assert(borrowed.isPrepared());assert(!DB.uninit());assert(DB.m_sqlite!=NULL);assert(borrowed.exec());assert(borrowed.getInt(0)==1);borrowed.finalize();assert(DB.uninit()); }
 assert(DB.m_sqlite==NULL);
 { DB.m_sqlite=new SQLiteConnection(CvWString(":memory:"));assert(DB.m_sqlite->open());assert(DB.configureConnection());
   DB.m_bActive=DB.m_bSqlLoaded=DB.m_bDoCache=true;SQLiteTransaction old;
   assert(DB.uninit());DB.m_sqlite=new SQLiteConnection(CvWString(":memory:"));assert(DB.m_sqlite->open());assert(DB.configureConnection());
   DB.m_bActive=DB.m_bSqlLoaded=DB.m_bDoCache=true;SQLiteTransaction current;
   assert(!old.isActive());assert(!old.commit());assert(!old.rollback());assert(current.rollback());assert(DB.uninit()); }

 // SQLITE_BUSY at COMMIT leaves ownership intact so callers can retry.
 { DB.m_sqlite=new SQLiteConnection(CvWString("busy-commit.db"));assert(DB.m_sqlite->open());assert(DB.configureConnection());
   DB.m_bActive=DB.m_bSqlLoaded=DB.m_bDoCache=true;
   assert(DB.exec("CREATE TABLE locked(v); INSERT INTO locked VALUES(1)"));
   sqlite3* reader=NULL;assert(sqlite3_open("busy-commit.db",&reader)==SQLITE_OK);
   assert(sqlite3_exec(reader,"BEGIN; SELECT * FROM locked",NULL,NULL,NULL)==SQLITE_OK);
   SQLiteTransaction writer;assert(writer.isActive());assert(DB.exec("UPDATE locked SET v=2"));
   assert(!writer.commit());assert(sqlite3_errcode(DB.m_sqlite->m_database)==SQLITE_BUSY);
   assert(writer.isActive());assert(!writer.wasCommitted());
   assert(sqlite3_exec(reader,"ROLLBACK",NULL,NULL,NULL)==SQLITE_OK);assert(sqlite3_close(reader)==SQLITE_OK);
   assert(writer.commit());assert(writer.wasCommitted());assert(!writer.isActive());
   { SQLiteStatement saved("busy-commit-result", "SELECT v FROM locked");assert(saved.exec());assert(saved.getInt(0)==2); }
   assert(DB.uninit()); }

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
 (d/'CvGameCoreDLL.h').write_text(STUB);(d/'CvGame.h').write_text('');(d/'test.cpp').write_text(TEST)
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
