#!/usr/bin/env python3
"""Actual storage header: 1D empty assignment and load, scalar int elements only."""
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
stub=r'''
#include <cassert>
#include <cstddef>
#include <vector>
#define FAssert(x) assert(x)
#define SAFE_DELETE_ARRAY(p) do{delete[]p;p=NULL;}while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do{delete[](reinterpret_cast<char*>(p)-(n));p=NULL;}while(0)
struct FDataStreamBase {
 std::vector<int> data;std::size_t pos;
 FDataStreamBase():pos(0){}
 template<class T>void Read(T* n){assert(pos<data.size());*n=static_cast<T>(data[pos++]);}
 template<class T>void Read(int n,T* p){assert(p!=NULL);for(int i=0;i<n;++i)Read(p+i);}
 template<class T>void Write(T n){data.push_back(n);}
 template<class T>void Write(int n,T const* p){for(int i=0;i<n;++i)Write(p[i]);}
};
struct CvXMLLoadUtility{template<class T>void SetVariableListTagPair(T**,char const*,int){}};
#include "FSimpleDataStorage.h"
int main(){
 for(int n=0;n<=12;++n){
  FDynamicArray<int> original;original.init(n);
  for(int i=0;i<n;++i)original.set(i,i*7-4);
  FDynamicArray<int> copy(original),assigned;assigned.init(4,99);assigned=original;
  assert(copy.size()==n && assigned.size()==n);
  for(int i=0;i<n;++i){assert(copy()[i]==i*7-4);assert(assigned()[i]==i*7-4);}
  if(n){copy.set(0,111);assert(original()[0]==-4);}
  assigned=assigned;assert(assigned.size()==n);
  FDataStreamBase stream;original.Write(&stream);stream.Write(7654321);
  FDynamicArray<int> loaded;loaded.init(6,42);loaded.Read(&stream);
  assert(loaded.size()==n);
  for(int i=0;i<n;++i)assert(loaded()[i]==i*7-4);
  int sentinel=0;stream.Read(&sentinel);assert(sentinel==7654321);
  stream.pos=0;loaded.Read(&stream);assert(loaded.size()==n);
  FDataStreamBase empty;empty.Write(0);loaded.Read(&empty);assert(loaded.size()==0);
 }

}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d)
 header=Path(os.environ.get('STORAGE_SOURCE',str(root/'CvGameCoreDLL/FSimpleDataStorage.h')))
 (p/'FSimpleDataStorage.h').write_text(header.read_text());(p/'test.cpp').write_text(stub)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
  '-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual 1D int copy/load methods; C++03/ASan/UBSan; stream and allocation macros stubbed')
