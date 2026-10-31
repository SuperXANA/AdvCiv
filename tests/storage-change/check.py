#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
stub=r'''
#include <cassert>
#include <cstddef>
#define FAssert(x) assert(x)
#define FAssertMsg(x,m) FAssert(x)
#define SAFE_DELETE_ARRAY(p) do{delete[]p;p=NULL;}while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do{delete[](reinterpret_cast<char*>(p)-(n));p=NULL;}while(0)
struct FDataStreamBase {
 template<class T>void Read(T*){}
 template<class T>void Read(int,T*){}
 template<class T>void Write(T){}
 template<class T>void Write(int,T const*){}
};
struct CvXMLLoadUtility{template<class T>void SetVariableListTagPair(T**,char const*,int){}};
#include "FSimpleDataStorage.h"
int main(){
 FStaticArray<bool,2> b;b.init();b.change(0,true);assert(b.get(0));b.change(0,false);assert(!b.get(0));
 FStaticArray<int,2> a;a.init(5);a.change(0,true);assert(a.get(0)==1);a.change(0,false);assert(a.get(0)==0);a.change(0,7);assert(a.get(0)==7);a.change(0,-2);assert(a.get(0)==5);a.change(0,-0.5);assert(a.get(0)==5);
 FDynamicArray<bool> db;db.init(2);db.change(1,true);assert(db() [1]);db.change(1,false);assert(!db() [1]);
 FDynamicArray<int> di;di.init(2,8);di.change(1,true);assert(di()[1]==1);di.change(1,3);assert(di()[1]==4);di.change(1,-0.5);assert(di()[1]==4);
 FDynamic2DArray<bool> tb;tb.init(1,2);tb.change(1,true);assert(tb()[1]);tb.change(1,false);assert(!tb()[1]);
 FDynamic2DArray<int> ti;ti.init(1,2,9);ti.change(1,true);assert(ti()[1]==1);ti.change(1,4);assert(ti()[1]==5);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'FSimpleDataStorage.h').write_text((root/'CvGameCoreDLL/FSimpleDataStorage.h').read_text());(p/'test.cpp').write_text(stub)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual full header parsed; all three bool/int change templates; C++03/ASan/UBSan. Stream/XML/allocation macros stubbed; other methods unverified.')
