#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]; s=Path(os.environ.get('SUMMON_SOURCE',str(root/'CvGameCoreDLL/CvPlayer.cpp'))).read_text()
a=s.index('\tLeaderHeadTypes selectCompatibleLeaderForSummonCiv('); b=s.index('\n\t// Master resolver.',a)
function=s[a:b]
helper=''
if '\tbool addSummonWeight(' in s:
 h=s.index('\tbool addSummonWeight('); helper=s[h:s.index('\n\t}',h)+3]

assert s.count('selectCompatibleLeaderForSummonCiv(eOutCiv, &kEvent, aeEligibleLeaders)')==2
assert s.count('selectCompatibleLeaderForSummonCiv(eOutCiv, NULL, aeEligibleLeaders)')==2
stub=r'''
#include <vector>
#include <cstddef>
#include <cassert>
enum LeaderHeadTypes{NO_LEADER=-1,L0,L1,L2,L3,LEADER_ENUM_MAX=127};
enum CivilizationTypes{NO_CIVILIZATION=-1,C0,C1,CIV_ENUM_MAX=127};
enum{GAMEOPTION_LEAD_ANY_CIV};
struct CvCivilizationInfo{bool leaders[4];bool isLeaders(int i)const{assert(i>=0&&i<4);return leaders[i];}};
struct Game{bool any;bool isOption(int)const{return any;}};
struct Globals{Game game;CvCivilizationInfo civs[2];int getNumCivilizationInfos()const{return 2;}int getNumLeaderHeadInfos()const{return 4;}CvCivilizationInfo const& getInfo(CivilizationTypes c)const{assert(c>=0&&c<2);return civs[c];}Game const& getGame()const{return game;}}GC;
struct CvEventInfo{int weights[4];bool present;int* getSummonLeaderWeightArray()const{return present?const_cast<int*>(weights):NULL;}int getSummonLeaderWeight(LeaderHeadTypes l)const{assert(l>=0&&l<4);return weights[l];}};
int nextRoll=0,calls=0,lastBound=0;
int roll(int n){assert(n>0&&n<=65535&&nextRoll>=0&&nextRoll<n);++calls;lastBound=n;return nextRoll;}
#define SyncRandNum(n) roll(n)
'''
checks=r'''
int main(){
 for(int c=0;c<2;++c)for(int l=0;l<4;++l)GC.civs[c].leaders[l]=false;
 GC.civs[0].leaders[0]=GC.civs[0].leaders[1]=true;
 std::vector<LeaderHeadTypes> pool;pool.push_back(L1);pool.push_back(L2);
 GC.game.any=false;
 // L0 is compatible but already in use, so omitted from the supplied pool.
 assert(selectCompatibleLeaderForSummonCiv(C0,NULL,pool)==L1&&lastBound==1);
 CvEventInfo e;e.present=true;e.weights[0]=100;e.weights[1]=0;e.weights[2]=10;e.weights[3]=0;
 int before=calls;assert(selectCompatibleLeaderForSummonCiv(C0,&e,pool)==NO_LEADER&&calls==before);
 GC.game.any=true;assert(selectCompatibleLeaderForSummonCiv(C0,&e,pool)==L2&&lastBound==10);
 e.weights[1]=2;e.weights[2]=3;
 for(int i=0;i<5;++i){nextRoll=i;assert(selectCompatibleLeaderForSummonCiv(C0,&e,pool)==(i<2?L1:L2));}
 e.present=false;nextRoll=1;assert(selectCompatibleLeaderForSummonCiv(C0,&e,pool)==L2&&lastBound==2);
 pool.clear();before=calls;assert(selectCompatibleLeaderForSummonCiv(C0,NULL,pool)==NO_LEADER&&calls==before);
 pool.push_back(NO_LEADER);pool.push_back(static_cast<LeaderHeadTypes>(99));
 assert(selectCompatibleLeaderForSummonCiv(C0,NULL,pool)==NO_LEADER&&calls==before);
 assert(selectCompatibleLeaderForSummonCiv(NO_CIVILIZATION,NULL,pool)==NO_LEADER&&calls==before);
 assert(selectCompatibleLeaderForSummonCiv(static_cast<CivilizationTypes>(99),NULL,pool)==NO_LEADER&&calls==before);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(stub+helper+function+checks)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual compatible-leader helper, available pool, compatibility/lead-any gates, filter weights, RNG bounds and invalid IDs. Engine/RNG stubbed; resolver call sites structural only.')
