#!/usr/bin/env python3
"""Compile actual temporary setters and complete timer component with engine/map stubs."""
from pathlib import Path
import os
import subprocess
import tempfile
root = Path(__file__).resolve().parents[2]
source = (root / "CvGameCoreDLL/CvPlot.cpp").read_text()
def function(signature):
    start = source.index(signature)
    opening, depth = source.index("{", start), 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]
setters = "\n".join(function("void CvPlot::setTemp" + k + "Type(") for k in ["Terrain","Feature","Bonus","Improvement","Route"])
plot = r'''
#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <map>
#include <utility>
enum PlotNumTypes { PLOT_0, PLOT_1, PLOT_2 };
enum TerrainTypes { NO_TERRAIN = -1, TERRAIN_0, TERRAIN_1, TERRAIN_2 };
enum FeatureTypes { NO_FEATURE = -1, FEATURE_0, FEATURE_1, FEATURE_2 };
enum BonusTypes { NO_BONUS = -1, BONUS_0, BONUS_1, BONUS_2 };
enum ImprovementTypes { NO_IMPROVEMENT = -1, IMPROVEMENT_0, IMPROVEMENT_1, IMPROVEMENT_2 };
enum RouteTypes { NO_ROUTE = -1, ROUTE_0, ROUTE_1, ROUTE_2 };
class CvPlot {
    PlotNumTypes id;
public:
    TerrainTypes terrain;
    FeatureTypes feature;
    BonusTypes bonus;
    ImprovementTypes improvement;
    RouteTypes route;
    int variety, changes[5];
    explicit CvPlot(PlotNumTypes p) : id(p), terrain(TERRAIN_1), feature(FEATURE_1),
        bonus(BONUS_1), improvement(IMPROVEMENT_1), route(ROUTE_1), variety(2) {
        for (int i = 0; i < 5; ++i) changes[i] = 0;
    }
    PlotNumTypes plotNum() const { return id; }
    void setTerrainType(TerrainTypes t, bool = true, bool = true) { terrain = t; ++changes[0]; }
    void setFeatureType(FeatureTypes t, int v = -1) { feature = t; variety = v; ++changes[1]; }
    void setBonusType(BonusTypes t) { bonus = t; ++changes[2]; }
    void setImprovementType(ImprovementTypes t) { improvement = t; ++changes[3]; }
    void setRouteType(RouteTypes t, bool = true) { route = t; ++changes[4]; }
    void changeTempTerrainTimer(int, bool = true) const;
    void changeTempFeatureTimer(int, bool = true) const;
    void changeTempBonusTimer(int, bool = true) const;
    void changeTempImprovementTimer(int, bool = true) const;
    void changeTempRouteTimer(int, bool = true) const;
    TerrainTypes getTerrainType() const { return terrain; }
    FeatureTypes getFeatureType() const { return feature; }
    int getFeatureVariety() const { return variety; }
    BonusTypes getBonusType() const { return bonus; }
    ImprovementTypes getImprovementType() const { return improvement; }
    RouteTypes getRouteType() const { return route; }
    void setTempTerrainType(TerrainTypes,int);
    void setTempFeatureType(FeatureTypes,int,int);
    void setTempBonusType(BonusTypes,int);
    void setTempImprovementType(ImprovementTypes,int);
    void setTempRouteType(RouteTypes,int);

};
'''
core = r'''
#pragma once
#include "CvPlot.h"
class FDataStreamBase {};
template<class V> struct DefaultValue { static V get() { return static_cast<V>(-1); } };
template<> struct DefaultValue<int> { static int get() { return 0; } };
template<class E, class V, class CV = V> class ArrayEnumMap {
    std::map<E, CV> values;
public:
    V get(E key) const {
        typename std::map<E, CV>::const_iterator i = values.find(key);
        return i == values.end() ? DefaultValue<V>::get() : static_cast<V>(i->second);
    }
    void set(E key, V value) {
        if (sizeof(CV) == sizeof(short)) assert(value >= SHRT_MIN && value <= SHRT_MAX);
        values[key] = static_cast<CV>(value);
    }
    void reset() { values.clear(); }
    void read(FDataStreamBase*) {}
    void write(FDataStreamBase*) const {}
};
class PlotTempChangeMap;
struct Map {
    PlotTempChangeMap* changes;
    PlotTempChangeMap& getPlotTempChangeMap() { assert(changes); return *changes; }
};
struct Globals { Map map; Map& getMap() { return map; } };
extern Globals GC;
'''
checks = r'''
#include "CvGameCoreDLL.h"
#include "PlotTempChangeMap.h"
#include <iostream>
Globals GC;
int current(CvPlot const& p,int k) {
 switch(k) { case 0:return p.terrain;case 1:return p.feature;case 2:return p.bonus;case 3:return p.improvement;default:return p.route; }
}
void direct(CvPlot& p,int k,int v) {
 switch(k) { case 0:p.terrain=static_cast<TerrainTypes>(v);break;case 1:p.feature=static_cast<FeatureTypes>(v);break;case 2:p.bonus=static_cast<BonusTypes>(v);break;case 3:p.improvement=static_cast<ImprovementTypes>(v);break;default:p.route=static_cast<RouteTypes>(v); }
}
void temp(CvPlot& p,int k,int v,int turns,int variety) {
 switch(k) {case 0:p.setTempTerrainType(static_cast<TerrainTypes>(v),turns);break;case 1:p.setTempFeatureType(static_cast<FeatureTypes>(v),variety,turns);break;case 2:p.setTempBonusType(static_cast<BonusTypes>(v),turns);break;case 3:p.setTempImprovementType(static_cast<ImprovementTypes>(v),turns);break;default:p.setTempRouteType(static_cast<RouteTypes>(v),turns);}
}
int original(PlotTempChangeMap const& m,CvPlot const& p,int k) {
 switch(k){case 0:return m.getRealTerrainType(p);case 1:return m.getRealFeatureType(p).first;case 2:return m.getRealBonusType(p);case 3:return m.getRealImprovementType(p);default:return m.getRealRouteType(p);}
}
int timer(PlotTempChangeMap const& m,CvPlot const& p,int k) {
 switch(k){case 0:return m.getTempTerrainTimer(p);case 1:return m.getTempFeatureTimer(p);case 2:return m.getTempBonusTimer(p);case 3:return m.getTempImprovementTimer(p);default:return m.getTempRouteTimer(p);}
}
int main(){
 int durations[]={1,2,5};int count=0;
 for(int k=0;k<5;++k)for(int base=(k==0?0:-1);base<=2;++base)for(int first=(k==0?0:-1);first<=2;++first)for(int second=(k==0?0:-1);second<=2;++second) {
  if(first==base||second==first)continue;
  for(int d=0;d<3;++d)for(int d2=0;d2<3;++d2)for(int age=0;age<durations[d];++age) {
   PlotTempChangeMap m;GC.map.changes=&m;CvPlot p(PLOT_0),q(PLOT_1);
   direct(p,k,base);p.variety=(base==-1?0:1);int baseVariety=p.variety;
   temp(p,k,first,durations[d],2);assert(original(m,p,k)==base);
   for(int turn=0;turn<age;++turn)m.update(p);
   assert(current(p,k)==first);
   temp(p,k,second,durations[d2],3);
   assert(original(m,p,k)==base);assert(timer(m,p,k)==durations[d2]);
   if(k==1)assert(m.getRealFeatureType(p).second==baseVariety);
   for(int turn=1;turn<=durations[d2];++turn){
    m.update(p);assert(current(p,k)==(turn==durations[d2]?base:second));
    assert(timer(m,p,k)==durations[d2]-turn);
    for(int j=0;j<5;++j){assert(timer(m,q,j)==0);assert(current(q,j)==1);if(j!=k){assert(current(p,j)==1);assert(timer(m,p,j)==0);}}
   }
   if(k==1)assert(p.variety==baseVariety);
   m.update(p);assert(current(p,k)==base);
   ++count;
  }
 }
 std::cout<<count<<" repeated temporary-change/restoration sequences passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    (tmp / "CvPlot.h").write_text(plot)
    (tmp / "CvGameCoreDLL.h").write_text(core)
    for name in ["PlotTempChangeMap.h","PlotTempChangeMap.cpp"]:
        (tmp / name).write_text((root / "CvGameCoreDLL" / name).read_text())
    (tmp / "setters.cpp").write_text('#include "CvGameCoreDLL.h"\n#include "PlotTempChangeMap.h"\n' + setters)
    (tmp / "checks.cpp").write_text(checks)
    subprocess.run(["g++","-std=c++03","-Wall","-Wextra","-Werror","-pedantic","-fsanitize=address,undefined","-fno-omit-frame-pointer",str(tmp / "PlotTempChangeMap.cpp"),str(tmp / "setters.cpp"),str(tmp / "checks.cpp"),"-o",str(tmp / "checks")],check=True)
    env=dict(os.environ,ASAN_OPTIONS="detect_leaks=0",UBSAN_OPTIONS="halt_on_error=1")
    subprocess.run([str(tmp / "checks")],check=True,env=env)
