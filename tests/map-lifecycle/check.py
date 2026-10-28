#!/usr/bin/env python3
"""Actual turn body and marked lifecycle snippets; remaining engine lifecycle modeled."""
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
s=(root/'CvGameCoreDLL/CvMap.cpp').read_text()
marker='// XANA: 04-26-2025 FfH Terrain Type Changes for Advanced Civ'
def function(signature):
 start=s.index(signature); end=s.index('{',start)+1; depth=1
 while depth:
  depth+=(s[end]=='{')-(s[end]=='}'); end+=1
 return s[start:end]
def snippet(signature): return function(signature).split(marker)[1]
constructor=function('CvMap::CvMap()'); reset=function('void CvMap::reset('); init=function('void CvMap::init(')
assert constructor.index('m_pTempChangesMap = NULL')<constructor.index('reset(&defaultMapData)')
assert reset.index('uninit();')<reset.index('m_pTempChangesMap = new PlotTempChangeMap;')
assert s.count('new PlotTempChangeMap')==1
assert init.index('reset(pInitInfo);')<init.index('reset() has already created')
code=r'''
#include <cassert>
#include <cstddef>
int alive=0,created=0,destroyed=0;
struct CvPlot { int turns,updates,timer; CvPlot():turns(0),updates(0),timer(3){} void doTurn(){++turns;} };
struct PlotTempChangeMap {
 PlotTempChangeMap(){++alive;++created;}
 ~PlotTempChangeMap(){--alive;++destroyed;}
 void update(CvPlot& p){assert(p.turns==p.updates+1);++p.updates;if(p.timer>0)--p.timer;}
};
#define SAFE_DELETE(p) do{delete p;p=NULL;}while(0)
struct Globals { bool graphics; bool IsGraphicsInitialized()const{return graphics;} } GC;
struct CvMap {
 PlotTempChangeMap* m_pTempChangesMap;
 CvPlot plots[3];
 CvMap(){
'''+snippet('CvMap::CvMap()')+r'''
 resetFixture();
 }
 ~CvMap(){uninitFixture();}
 void uninitFixture(){
'''+snippet('void CvMap::uninit()')+r'''
 }
 void resetFixture(){uninitFixture();
'''+snippet('void CvMap::reset(')+r'''
 }
 void initFixture(){resetFixture();
'''+snippet('void CvMap::init(')+r'''
 }
 int numPlots()const{return 3;}
 CvPlot& getPlotByIndex(int i){return plots[i];}
 PlotTempChangeMap& getPlotTempChangeMap(){assert(m_pTempChangesMap);return *m_pTempChangesMap;}
 void doTurn();
};
'''+function('void CvMap::doTurn()')+r'''
int main(){
 for(int graphics=0;graphics<2;++graphics){
  GC.graphics=graphics!=0;
  { CvMap map;assert(alive==1);map.initFixture();assert(alive==1);
   for(int i=0;i<5;++i)map.doTurn();
   for(int i=0;i<3;++i){assert(map.plots[i].turns==5&&map.plots[i].updates==5&&map.plots[i].timer==0);}
   for(int i=0;i<10;++i){map.resetFixture();assert(alive==1);}
  }
  assert(alive==0&&created==destroyed);
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
print('PASS: marked ownership snippets, modeled lifecycle, actual doTurn body; C++03/ASan/UBSan. Full engine lifecycle excluded.')
