#!/usr/bin/env python3
"""Extract the production method; game interfaces and 2048-scale arithmetic are stand-ins."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvPlayerAI.cpp').read_text()
start = source.index('int CvPlayerAI::AI_getShareRelativeProgressAttitude(')
end = source.index('{', start) + 1
depth = 1
while depth:
    depth += (source[end] == '{') - (source[end] == '}')
    end += 1
method = source[start:end]
prefix = r'''
#include <cassert>
#include <stdint.h>
#include <cstdlib>
#include <cmath>
#include <iostream>
typedef int PlayerTypes;
typedef int AttitudeTypes;
int nearest(long double x) {return static_cast<int>(x>=0?std::floor(x+0.5L):std::ceil(x-0.5L));}
int mulDiv(int a,int b,int d) {
    assert(d!=0);int64_t n=static_cast<int64_t>(a)*b,den=d;
    if(den<0){den=-den;n=-n;}
    return static_cast<int>(n>=0?(n+den/2)/den:-((-n+den/2)/den));
}
struct scaled {
    int raw;
    scaled(int x=0):raw(x*2048){}
    scaled(int n,int d):raw(mulDiv(2048,n,d)){}
    static scaled fromRaw(int n){scaled r;r.raw=n;return r;}
    int round() const{return (raw+(raw>=0?1024:-1024))/2048;}
};
scaled operator+(int a,scaled b){return scaled::fromRaw(a*2048+b.raw);}
scaled operator-(scaled a,scaled b){return scaled::fromRaw(a.raw-b.raw);}
scaled operator*(scaled a,scaled b){return scaled::fromRaw(mulDiv(a.raw,b.raw,2048));}
scaled operator*(scaled a,int b){return scaled::fromRaw(a.raw*b);}
scaled fixp(double x){assert(x==0.5);return scaled::fromRaw(1024);}
int range(int n,int lo,int hi){return n<lo?lo:(n>hi?hi:n);}
struct CvLeaderHeadInfo {
    int divisor,threshold,base,limit;
    int getShareRelativeProgressAttitudeChangeDivisor()const{return divisor;}
    int getShareRelativeProgressCooperationAttitudeThreshold()const{return threshold;}
    int getShareRelativeProgressAttitudeChange()const{return base;}
    int getShareRelativeProgressAttitudeChangeLimit()const{return limit;}
};
struct CvGame {
    int count,our,their;
    int getPlayerRank(int p)const{return p==0?our:their;}
    int getCivPlayersEverAlive()const{return count;}
};
struct Globals {
    CvLeaderHeadInfo info;CvGame game;
    CvLeaderHeadInfo const& getInfo(int)const{return info;}
    CvGame const& getGame()const{return game;}
} GC;
struct CvPlayerAI {
    int counter;
    int getPersonalityType()const{return 0;}
    int getID()const{return 0;}
    int AI_getAttitudeFromValue(int x)const{return x;}
    int AI_getShareRelativeProgressCounter(int)const{return counter;}
    int AI_getShareRelativeProgressAttitude(PlayerTypes,int)const;
};
int reference(int attitude,int counter) {
    CvLeaderHeadInfo const& p=GC.info;CvGame const& g=GC.game;
    if(p.divisor==0||p.threshold<=0||attitude<=p.threshold||g.count<=1||
       g.our*p.threshold<g.count||g.their*p.threshold<g.count)return 0;
    // Independent long-double reference, quantized at the documented 2048-scale operation boundaries.
    long double rank=nearest(2048.0L*(g.our+g.their)/(2*(g.count-1)))/2048.0L;
    long double duration=nearest(2048.0L*counter/p.divisor)/2048.0L;
    long double contribution=nearest(2048.0L*(rank-0.5L)*duration)/2048.0L;
    int value=nearest(p.base+contribution);
    return p.limit==0?value:range(value,-std::abs(p.limit),std::abs(p.limit));
}
'''
main = r'''
int main(){
    CvPlayerAI unit;GC.info.divisor=2;GC.info.threshold=2;GC.info.base=0;GC.info.limit=0;
    GC.game.count=6;GC.game.our=3;GC.game.their=4;unit.counter=20;
    assert(unit.AI_getShareRelativeProgressAttitude(1,4)==2);
    GC.game.our=4;GC.game.their=5;unit.counter=3;
    assert(unit.AI_getShareRelativeProgressAttitude(1,4)==1);
    int players[]={2,3,6,12,18},divisors[]={-7,-2,0,2,7},counters[]={0,1,3,8,20,101};
    int attitudes[]={0,3,4},bases[]={-3,0,3},limits[]={-4,0,4};
    unsigned long cases=0;
    for(int n=0;n<5;++n)for(int a=0;a<players[n];++a)for(int b=0;b<players[n];++b){
        if(a==b)continue;
        GC.game.count=players[n];GC.game.our=a;GC.game.their=b;
        for(int t=-1;t<=4;++t)for(int at=0;at<3;++at)for(int d=0;d<5;++d)
        for(int c=0;c<6;++c)for(int bs=0;bs<3;++bs)for(int lim=0;lim<3;++lim){
            GC.info.threshold=t;GC.info.divisor=divisors[d];GC.info.base=bases[bs];GC.info.limit=limits[lim];unit.counter=counters[c];
            assert(unit.AI_getShareRelativeProgressAttitude(1,attitudes[at])==reference(attitudes[at],unit.counter));++cases;
        }
    }
    GC.info.divisor=2;GC.info.threshold=2;GC.game.our=0;GC.game.their=0;
    for(int n=0;n<=1;++n){GC.game.count=n;assert(unit.AI_getShareRelativeProgressAttitude(1,4)==0);++cases;}
    assert(cases==2313362UL);
    std::cout<<cases<<" extracted-method cases passed with game/fixed-point stand-ins\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p = Path(directory)
    (p/'check.cpp').write_text(prefix+'\n'+method+'\n'+main)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
