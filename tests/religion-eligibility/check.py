#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
h=(root/'CvGameCoreDLL/CvPlayer.h').read_text();s=(root/'CvGameCoreDLL/CvPlayer.cpp').read_text()
def extract(source,sig):
 a=source.index(sig);b=source.index('{',a)+1;depth=1
 while depth:
  depth+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
inline=extract(h,'bool canDoReligion(ReligionTypes eReligion) const')
helper=extract(s,'bool CvPlayer::isAllowedReligion(')
code=r'''
#include <cassert>
enum ReligionTypes{NO_RELIGION=-1,R0};
const int NO_CIVILIZATION=-1,NO_LEADER=-1;
struct CvReligionInfo{int civ,leader;int getPrereqCivilization()const{return civ;}int getPrereqLeader()const{return leader;}};
struct Globals{CvReligionInfo info;mutable int reads;CvReligionInfo const& getInfo(ReligionTypes r)const{assert(r==R0);++reads;return info;}}GC;
struct CvPlayer{
 int civ,leader,count,noneCount;mutable int countReads;
 int getCivilizationType()const{return civ;}
 int getLeaderType()const{return leader;}
 int getHasReligionCount(ReligionTypes r)const{++countReads;return r==NO_RELIGION?noneCount:count;}
 bool isAllowedReligion(ReligionTypes)const;
'''+inline+'\n};\n'+helper+r'''
int main(){
 CvPlayer p;int cases=0;
 for(int civ=0;civ<2;++civ)for(int leader=0;leader<2;++leader)
 for(int requiredCiv=-1;requiredCiv<2;++requiredCiv)for(int requiredLeader=-1;requiredLeader<2;++requiredLeader)
 for(int count=0;count<=2;count+=2){
  p.civ=civ;p.leader=leader;p.count=count;p.noneCount=0;p.countReads=0;GC.info.civ=requiredCiv;GC.info.leader=requiredLeader;GC.reads=0;
  bool allowed=(requiredCiv==-1||requiredCiv==civ)&&(requiredLeader==-1||requiredLeader==leader);
  assert(p.canDoReligion(R0)==(allowed&&count>0));assert(GC.reads==1);assert(p.countReads==(allowed?1:0));
  ++cases;
 }
 assert(cases==72);
 for(int none=0;none<=2;none+=2){p.noneCount=none;p.countReads=0;GC.reads=0;assert(p.canDoReligion(NO_RELIGION)==(none>0));assert(GC.reads==0&&p.countReads==1);}
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual inline canDoReligion and isAllowedReligion; 72 prerequisite/presence combinations and sentinel preservation. C++03/ASan/UBSan; engine stubbed.')
