#!/usr/bin/env python3
"""Usage: python check.py BASELINE_ScaledNum.h AUTOFIX_ScaledNum.h.
Compile actual floor/ceil bodies in minimal integer-storage templates.
This isolates arithmetic, not the complete engine header or DLL.
"""
from pathlib import Path
import subprocess, tempfile, os, sys
def bodies(path):
 s=Path(path).read_text()
 result=[]
 for name in ['floor','ceil']:
  start=s.index('int '+name+'() const'); end=s.index('{',start)+1; depth=1
  while depth:
   depth+=(s[end]=='{')-(s[end]=='}'); end+=1
  result.append(s[start:end])
 return '\n'.join(result)
code='''#include <cassert>
#include <climits>
#include <iostream>
'''
for name,path in zip(['Baseline','Autofix'],sys.argv[1:]):
 code+='template<int Scale,class T> struct '+name+' { T m_i; static T const SCALE=static_cast<T>(Scale);\n'+bodies(path)+'\n};\n'
code+=r'''
unsigned long checks=0;
template<int S,class T> void check(T raw) {
 Baseline<S,T> a; Autofix<S,T> b; a.m_i=b.m_i=raw;
 // Reference uses division/remainder; avoids subtraction and multiplication.
 int q=static_cast<int>(raw / static_cast<T>(S));
 int expected=q + ((raw>0 && raw%static_cast<T>(S)!=0)?1:0);
 assert(a.ceil()==expected && b.ceil()==expected); ++checks;
}
template<int S> void small() {
 for(int i=SHRT_MIN;i<=SHRT_MAX;++i) check<S,short>(static_cast<short>(i));
 for(unsigned int i=0;i<=USHRT_MAX;++i) check<S,unsigned short>(static_cast<unsigned short>(i));
}
template<int S> void wide() {
 int values[]={INT_MIN,INT_MIN+1,-S-1,-S,-S+1,-1,0,1,S-1,S,S+1,INT_MAX-1,INT_MAX};
 for(unsigned int i=0;i<sizeof(values)/sizeof(values[0]);++i) check<S,int>(values[i]);
 unsigned int state=123456789;
 for(int i=0;i<100000;++i) {
  state=1664525u*state+1013904223u;
  // ceil returns int: restrict to values whose ceiling fits int.
  unsigned int maxRaw=S==1?static_cast<unsigned int>(INT_MAX):UINT_MAX-(S==2?1u:0u);
  unsigned int raw=state>maxRaw?maxRaw:state;
  check<S,unsigned int>(raw);
  check<S,int>(static_cast<int>(state & INT_MAX));
 }
 unsigned int edges[]={0,1,static_cast<unsigned int>(S)-1,static_cast<unsigned int>(S),static_cast<unsigned int>(S)+1,static_cast<unsigned int>(INT_MAX)};
 for(unsigned int i=0;i<sizeof(edges)/sizeof(edges[0]);++i) check<S,unsigned int>(edges[i]);
 if(S>2) check<S,unsigned int>(UINT_MAX);
}
int main() {
 assert(sizeof(int)==4 && sizeof(short)==2);
 small<1>(); small<2>(); small<3>(); small<10>(); small<100>(); small<2048>();
 wide<1>(); wide<2>(); wide<3>(); wide<10>(); wide<100>(); wide<2048>();
 std::cout << checks << " comparisons passed\n";
}
'''
if len(sys.argv)!=3: raise SystemExit(__doc__)
with tempfile.TemporaryDirectory() as d:
 p=Path(d); (p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-Wno-type-limits','-fsanitize=address,undefined','-g',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
