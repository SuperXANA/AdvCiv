#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
s=(root/'CvGameCoreDLL/CvPlayerAI.cpp').read_text()
start=s.index('int CvPlayerAI::AI_getFavoriteGenderAttitude(')
end=s.index('// XANA: 10-25-2025 Gender Specific Diplomacy',start)
methods=s[start:end]
stub=r'''
#include <cassert>
typedef int PlayerTypes;
enum GenderTypes { NO_GENDER=-1, A, B, C };
enum { ALLY_GENDER, ENEMY_GENDER };
struct CvPlayer {
 GenderTypes gender,fav,hate;
 GenderTypes getGender()const{return gender;}
 GenderTypes getFavoriteGender()const{return fav;}
 GenderTypes getHateGender()const{return hate;}
} target;
#define GET_PLAYER(x) target
struct CvLeaderHeadInfo {
 int base;
 int getFavoriteGenderAttitudeChange()const{return base;}
 int getHateGenderAttitudeChange()const{return base;}
 int getFavoriteGenderAttitudeDivisor()const{return 10;}
 int getHateGenderAttitudeDivisor()const{return -10;}
 int getFavoriteGenderAttitudeChangeLimit()const{return 4;}
 int getHateGenderAttitudeChangeLimit()const{return -4;}
} personality;
struct Globals { CvLeaderHeadInfo const& getInfo(int)const{return personality;} } GC;
struct CvPlayerAI: CvPlayer {
 mutable int calls,marker,divisor,limit;
 int getPersonalityType()const{return 0;}
 int AI_getFavoriteGenderCounter(int)const{return 17;}
 int AI_getHateGenderCounter(int)const{return 23;}
 int AI_ideologyAttitudeChange(int,int m,int count,int d,int l)const {
  assert(count==(m==ALLY_GENDER?17:23)); ++calls; marker=m; divisor=d;limit=l;return 0;
 }
 int AI_getFavoriteGenderAttitude(PlayerTypes)const;
 int AI_getHateGenderAttitude(PlayerTypes)const;
};
'''
checks=r'''
int main(){
 CvPlayerAI self; int cases=0;
 for(int own=-1;own<3;++own)for(int fav=-1;fav<3;++fav)for(int hate=-1;hate<3;++hate)
 for(int other=-1;other<3;++other)for(int otherFav=-1;otherFav<3;++otherFav)for(int otherHate=-1;otherHate<3;++otherHate)
 for(int base=-3;base<=3;++base){
  self.gender=static_cast<GenderTypes>(own);self.fav=static_cast<GenderTypes>(fav);self.hate=static_cast<GenderTypes>(hate);
  target.gender=static_cast<GenderTypes>(other);target.fav=static_cast<GenderTypes>(otherFav);target.hate=static_cast<GenderTypes>(otherHate);personality.base=base;
  bool match=fav!=-1&&fav!=hate&&fav==other;
  int expected=match?base+(fav==otherFav?1:0):0;
  self.calls=0; assert(self.AI_getFavoriteGenderAttitude(0)==expected);assert(self.calls==(match?1:0));
  if(match){ assert(self.marker==ALLY_GENDER);assert(self.divisor==(expected<0?-10:10));assert(self.limit==(expected<0?-4:4));
   bool preferOwn=own==fav;assert(!(preferOwn?own!=other:own==other));assert(preferOwn?own==other:own!=other); }
  match=hate!=-1&&hate!=fav&&hate==other;
  expected=match?base-(hate==otherFav?1:0):0;
  self.calls=0;assert(self.AI_getHateGenderAttitude(0)==expected);assert(self.calls==(match?1:0));
  if(match){ assert(self.marker==ENEMY_GENDER);assert(self.divisor==(expected>0?10:-10));assert(self.limit==(expected>0?4:-4));
   bool preferOwn=own!=hate;assert(!(preferOwn?own==other:own!=other));assert(preferOwn?own!=other:own==other); }
  ++cases;
 }
 assert(cases==28672);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(stub+methods+checks)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
print('PASS: actual two attitude helpers, 28,672 input combinations; C++03/ASan/UBSan, ideology helper/engine stubbed.')
