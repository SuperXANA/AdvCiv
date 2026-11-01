from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
player=(root/'CvGameCoreDLL/CvPlayer.cpp').read_text()
ai=(root/'CvGameCoreDLL/CvPlayerAI.cpp').read_text()
start=player.index('if (it->getStateReligion() != NO_RELIGION ||',player.index('void CvPlayer::setLastStateReligion('))
end=player.index('\n\t\t\t{',start)
predicate=player[start+4:end].rstrip()
assert predicate.endswith(')')
predicate=predicate[:-1]
start=ai.index('int CvPlayerAI::AI_getHateReligionAttitude(')
end=ai.index('\n}',start)+2
method=ai[start:end]
prefix=r'''
#include <cassert>
#include <iostream>
typedef int PlayerTypes;
typedef int ReligionTypes;
enum {NO_RELIGION=-1, ENEMY_RELIGION=1};
struct Info {int getHateReligionAttitudeChange()const{return -3;}
 int getHateReligionAttitudeDivisor()const{return -10;}
 int getHateReligionAttitudeChangeLimit()const{return -5;}};
typedef Info CvLeaderHeadInfo;
struct Globals {Info info;Info const& getInfo(int)const{return info;}} GC;
struct CvPlayerAI {
 int id,state,hated;bool holy;
 int getID()const{return id;}
 int getPersonalityType()const{return id;}
 int getStateReligion()const{return state;}
 int getHateReligion()const{return hated;}
 bool hasHolyCity(int)const{return holy;}
 int AI_getHateReligionCounter(int)const{return 0;}
 int AI_ideologyAttitudeChange(int,int,int,int,int)const{return 0;}
 int AI_getHateReligionAttitude(int)const;
} players[3];
#define GET_PLAYER(i) players[i]
int converter;
int getID(){return converter;}
bool shouldRefresh(CvPlayerAI const* it){return PREDICATE;}
'''.replace('PREDICATE',predicate)
main=r'''
int main(){
 int cases=0,changedReligionless=0;
 for(converter=0;converter<3;++converter)
 for(int observer=0;observer<3;++observer)if(observer!=converter)
 for(int before=-1;before<2;++before)
 for(int after=-1;after<2;++after)if(before!=after)
 for(int religion=-1;religion<2;++religion)
 for(int hate=-1;hate<2;++hate)
 for(int holy=0;holy<2;++holy){
  for(int i=0;i<3;++i){players[i].id=i;players[i].state=-1;players[i].hated=-1;players[i].holy=false;}
  players[observer].state=religion;players[observer].hated=hate;
  players[converter].state=before;players[converter].holy=holy!=0;
  int cached=players[observer].AI_getHateReligionAttitude(converter);
  players[converter].state=after;
  int actual=players[observer].AI_getHateReligionAttitude(converter);
  bool refresh=shouldRefresh(&players[observer]);
  assert(refresh==(religion!=-1 || hate!=-1));
  if(refresh)cached=actual;
  assert(cached==actual);
  if(religion==-1 && before==hate && hate!=-1){assert(refresh);++changedReligionless;}
  assert(shouldRefresh(&players[converter]));
  ++cases;
 }
 assert(cases==648 && changedReligionless>0);
 std::cout<<cases<<" conversion/filter/cache cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);source=prefix+method+main
 for negative in (False,True):
  candidate=source
  if negative:
   candidate=candidate.replace('it->getHateReligion() != NO_RELIGION ||','')
   candidate=candidate.replace('assert(refresh==(religion!=-1 || hate!=-1));','')
  (p/'check.cpp').write_text(candidate)
  subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
  result=subprocess.run([str(p/'check')],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
  if negative:
   assert result.returncode!=0 and 'cached==actual' in result.stderr
   print('Original filter fails refresh regression')
  else:
   assert result.returncode==0,result.stderr
   print(result.stdout.strip())
