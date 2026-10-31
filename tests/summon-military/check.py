#!/usr/bin/env python3
"""Complete actual military helper; city/player/unit/iteration/RNG/transfer interfaces stubbed."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvPlayer.cpp').read_text()
start=source.index('void doWorldMilitaryUnitBreachforSummonedPlayer(')
end=source.index('{',start)+1
depth=1
while depth:
    depth+=(source[end]=='{')-(source[end]=='}')
    end+=1
helper=source[start:end]
prefix=r'''
#include <cassert>
#include <cstddef>
#include <vector>
#include <iostream>
typedef int PlayerTypes;
enum {NO_PLAYER=-1};
struct CvUnit {
    int id,owner;
    bool greatPerson,settler;
    bool isGreatPerson()const{return greatPerson;}
    bool canFoundCity()const{return settler;}
    int getVisualOwner()const{return owner;}
};
struct CvCity {
    int population;
    int getPopulation()const{return population;}
    int getConscriptUnit()const{return 7;}
    int getX()const{return 11;}
    int getY()const{return 13;}
};
struct CvPlot {
    CvCity city;
    std::vector<CvUnit*> units;
    int iterations,cityReads;
    CvPlot():iterations(0),cityReads(0){}
    CvCity* getPlotCity(){++cityReads;return &city;}
};
#define FOR_EACH_UNIT_IN(u,p) for(size_t idx=0,total=(++(p).iterations,(p).units.size());idx<total;++idx) for(CvUnit* u=(p).units[idx];u!=NULL;u=NULL)
struct CvEventInfo {
    int createChance,defectChance;
    mutable int defectReads;
    int getSummonUnitCreateChance()const{return createChance;}
    int getSummonUnitDefectChance()const{++defectReads;return defectChance;}
};
struct CvPlayer {
    int created;
    std::vector<int> transferCalls;
    CvPlayer():created(0){}
    int getID()const{return 2;}
    void initUnit(int type,int x,int y){assert(type==7&&x==11&&y==13);++created;}
};
int rollValue,randomCalls;
int SyncRandNum(int max){assert(max==100);++randomCalls;return rollValue;}
void defectUnitToPlayer(CvUnit* u,CvPlayer& player){assert(u);player.transferCalls.push_back(u->id);}
'''
code=prefix+helper+r'''
int main(){
 int const populations[]={0,1,2,3,4,7,10};
 int const capacities[]={1,1,1,1,2,3,5};
 int const chances[]={0,1,50,100},summoners[]={NO_PLAYER,0,1,2},rolls[]={0,49,99};
 int cases=0;
 for(int pop=0;pop<7;++pop)for(int create=0;create<4;++create)
 for(int defect=0;defect<4;++defect)for(int summoner=0;summoner<4;++summoner)for(int roll=0;roll<3;++roll){
    CvPlot plot;plot.city.population=populations[pop];CvUnit units[16];int id=0;
    for(int owner=-1;owner<=2;++owner)for(int great=0;great<2;++great)for(int settler=0;settler<2;++settler){
        units[id].id=id;units[id].owner=owner;units[id].greatPerson=(great!=0);units[id].settler=(settler!=0);plot.units.push_back(&units[id]);++id;
    }
    CvEventInfo event={chances[create],chances[defect],0};CvPlayer player;
    rollValue=rolls[roll];randomCalls=0;
    doWorldMilitaryUnitBreachforSummonedPlayer(event,plot,player,summoners[summoner]);
    int expectedCreated=event.createChance>0 ? 1+(capacities[pop]-1)*(rollValue<event.createChance) : 0;
    assert(player.created==expectedCreated);
    assert(plot.cityReads==(event.createChance>0?1:0));
    int expectedRandom=event.createChance>0?capacities[pop]-1:0;
    std::vector<int> expectedTransfers;
    if(summoners[summoner]!=NO_PLAYER&&event.defectChance>0){
        for(int i=0;i<16;++i)if(!units[i].greatPerson&&!units[i].settler&&units[i].owner!=player.getID()&&units[i].owner==summoners[summoner]){
            ++expectedRandom;
            if(rollValue<event.defectChance)expectedTransfers.push_back(i);
        }
    }
    assert(randomCalls==expectedRandom);
    assert(event.defectReads==(summoners[summoner]!=NO_PLAYER?1:0));
    assert(plot.iterations==((summoners[summoner]!=NO_PLAYER&&event.defectChance>0)?1:0));
    assert(player.transferCalls==expectedTransfers);
    ++cases;
 }
 assert(cases==1344);std::cout<<cases<<" military creation/defection configurations passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(code)
    command=['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
             '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')]
    # Negative-control mode only: reach the behavior of the old empty if statement.
    if os.environ.get('SUMMON_TEST_OLD_EMPTY_IF')=='1':
        command[1:1]=['-Wno-empty-body','-Wno-misleading-indentation']
    subprocess.run(command,check=True)
    subprocess.run([str(p/'check')],check=True,
                   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
