from pathlib import Path
import os,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
s=Path(os.environ.get('GENDER_SOURCE',str(root/'CvGameCoreDLL/CvPlayerAI.cpp'))).read_text()
a=s.index('void CvPlayerAI::AI_updateStrategyHash(');marker='// XANA: 10-25-2025 Gender Specific Diplomacy'
block=s[a:].split(marker)[1]
prefix=r'''
#include <cassert>
#include <vector>
typedef int GenderTypes;
enum{NO_GENDER=-1,FREE_MAJOR_CIV,KNOWN_POTENTIAL_ENEMY_OF};
struct CvLeaderHeadInfo {int own,fav,hate;int getGender()const{return own;}
int getFavoriteGender()const{return fav;}int getHateGender()const{return hate;}};
struct Globals{CvLeaderHeadInfo info;CvLeaderHeadInfo const& getInfo(int)const{return info;}}GC;
struct Rival{int gender;int getGender()const{return gender;}};
std::vector<Rival> rivals;
template<int A,int B>class PlayerAIIter {
 std::size_t pos;
public:explicit PlayerAIIter(int):pos(0){}bool hasNext()const{return pos<rivals.size();}
 void operator++(){++pos;}Rival const* operator->()const{return &rivals[pos];}
};
struct CvPlayerAI {int getPersonalityType()const{return 0;}int getTeam()const{return 0;}
int adjust(int iParanoia)const;};
'''
test=r'''
int main(){
 for(int own=-1;own<3;++own)for(int fav=-1;fav<3;++fav)for(int hate=-1;hate<3;++hate)
 for(int count=0;count<=4;++count)for(int target=-1;target<3;++target){
  GC.info.own=own;GC.info.fav=fav;GC.info.hate=hate;rivals.clear();int delta=0;
  for(int n=0;n<count;++n){Rival r;r.gender=(target+n+1)%4-1;rivals.push_back(r);
   if(fav!=-1 && ((own==fav)==(r.gender==own)))delta-=10;
   if(hate!=-1 && ((own!=hate)==(r.gender!=own)))delta+=10;
  }
  CvPlayerAI ai;assert(ai.adjust(200)==200+delta);assert(ai.adjust(-20)==-20+delta);
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(prefix+'int CvPlayerAI::adjust(int iParanoia)const{'+block+'return iParanoia;}'+test)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual gender paranoia block; 1280 configurations/two starting scores; C++03/ASan/UBSan; iterator/metadata stubbed')
