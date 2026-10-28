#!/usr/bin/env python3
"""Compile actual readPass2 with both assertion configurations; XML is stubbed."""
import pathlib, subprocess, tempfile, os
root=pathlib.Path(__file__).resolve().parents[2]
s=pathlib.Path(os.environ.get('FIRST_SOURCE',str(root/'CvGameCoreDLL/CvInfo_Civilization.cpp'))).read_text()
a=s.index('bool CvLeaderHeadInfo::readPass2(')
method=s[a:s.index('\n}',a)+2]
prefix=r'''
#include <cassert>
#include <string>
struct Globals {int getNumLeaderHeadInfos()const{return 149;}} GC;
struct CvXMLLoadUtility {
 int calls;
 CvXMLLoadUtility():calls(0){}
 void SetVariableListTagPair(int** p,char const* tag,int count){
  assert(std::string(tag)=="FirstImpressionChanges");assert(count==149);++calls;
  *p=new int[count];for(int i=0;i<count;++i)(*p)[i]=i-74;
 }
};
#define FOR_EACH_ENUM(T) for(int eLoopLeaderHead=0;eLoopLeaderHead<149;++eLoopLeaderHead)
#define FAssert(x) assert(x)
struct CvLeaderHeadInfo {
 int* m_piFirstImpressionModifier;
 CvLeaderHeadInfo():m_piFirstImpressionModifier(NULL){}
 ~CvLeaderHeadInfo(){delete[]m_piFirstImpressionModifier;}
 bool isDefaultsType()const{return false;}
 bool readPass2(CvXMLLoadUtility*);
};
'''
suffix=r'''
int main(){CvXMLLoadUtility xml;CvLeaderHeadInfo info;
assert(info.readPass2(&xml));assert(xml.calls==1);
for(int i=0;i<149;++i)assert(info.m_piFirstImpressionModifier[i]==i-74);}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=pathlib.Path(tmp)/'check.cpp';p.write_text(prefix+method+suffix)
 for flags in [[],['-DFASSERT_ENABLE']]:
  exe=pathlib.Path(tmp)/'check'
  subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
    '-fsanitize=address,undefined',*flags,str(p),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('readPass2 passed C++03/ASan/UBSan with FASSERT_ENABLE on and off; loader stub only')
