from pathlib import Path
import os,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
s=Path(os.environ.get('EVENT_SOURCE',str(root/'CvGameCoreDLL/CvPlayerAI.cpp'))).read_text()
marker='// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process'
a=s.index('int CvPlayerAI::AI_eventValue(');chunks=s[a:].split(marker)
blocks=chunks[1:4:2]
assert len(blocks)==2
h=(root/'CvGameCoreDLL/CvXMLStructs.h').read_text();a=h.index('struct EventPreferenceData');h=h[a:h.index('\n};',a)+4]
defs=(root/'CvGameCoreDLL/CvXMLStructs.cpp').read_text();methods=[]
for name in ['getEventValueModifierPercent','isPreferredChoice','isNotPreferredChoice']:
 a=defs.index('EventPreferenceData::'+name);a=defs.rfind('\n',0,a)+1;methods.append(defs[a:defs.index('\n}',a)+2])
prefix=r'''
#include <cassert>
#include <cstddef>
enum {NO_EVENT=-1,NO_EVENTPREFERENCE=-1};
class CvXMLLoadUtility;
'''
stub=r'''
struct CvEventPreferenceInfo {
 EventPreferenceData data;int index;
 int getEventPreferenceIndex(int)const{return index;}
 EventPreferenceData const& getEventPreference(int i)const{assert(i==0);return data;}
};
struct Globals{CvEventPreferenceInfo prefs[2];CvEventPreferenceInfo const& getInfo(int i)const{return prefs[i];}}GC;
struct CvPlayerAI{
 int leader,civ;
 int AI_getLeaderEventPreferences()const{return leader;}
 int AI_getCivilizationEventPreferences()const{return civ;}
 int evaluate(int eEvent,int iValue)const;
};
'''
checks=r'''
int main(){
 int percents[]={0,50,100,150};
 for(int leader=-1;leader<=0;++leader)for(int civ=-1;civ<=1;civ+=2)
 for(int l=0;l<4;++l)for(int c=0;c<4;++c)for(int lp=0;lp<4;++lp)for(int cp=0;cp<4;++cp){
  CvPlayerAI ai;ai.leader=leader;ai.civ=civ;
  GC.prefs[0].index=GC.prefs[1].index=0;
  GC.prefs[0].data.bPreferredChoice=l&1;GC.prefs[0].data.bNotPreferredChoice=l&2;
  GC.prefs[1].data.bPreferredChoice=c&1;GC.prefs[1].data.bNotPreferredChoice=c&2;
  GC.prefs[0].data.iEventValueModifierPercent=percents[lp];GC.prefs[1].data.iEventValueModifierPercent=percents[cp];
  int expected=20;
  if(leader!=-1){if(l&1)expected+=10000;else if(l&2)expected=0;}
  if(civ!=-1){if(c&1)expected+=10000;else if(c&2)expected=0;}
  if(leader!=-1&&percents[lp])expected=expected*percents[lp]/100;
  if(civ!=-1&&percents[cp])expected=expected*percents[cp]/100;
  assert(ai.evaluate(0,20)==expected);
  GC.prefs[0].index=GC.prefs[1].index=-1;assert(ai.evaluate(0,20)==20);
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(prefix+h+'\n'.join(methods)+stub+'int CvPlayerAI::evaluate(int eEvent,int iValue)const{'+''.join(blocks)+'return iValue;}'+checks)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual event preference blocks/data accessors; 1024 configurations plus missing entries; C++03/ASan/UBSan')
