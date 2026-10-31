#!/usr/bin/env python3
"""Actual temporary setter/component plus baseline feature normalization front end.

Reuse the existing engine/map fixture interfaces; no real rendering/metadata/stream run.
"""
from pathlib import Path
import ast
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
tree=ast.parse((root/'tests/plot-restoration/check.py').read_text())
strings={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
        strings[node.targets[0].id]=node.value.value
plot,core=strings['plot'],strings['core']
source=(root/'CvGameCoreDLL/CvPlot.cpp').read_text()
start=source.index('void CvPlot::setTempFeatureType(');opening=source.index('{',start);end=opening+1;depth=1
while depth:
    depth+=(source[end]=='{')-(source[end]=='}');end+=1
temporary=source[start:end]
ordinary_start=source.index('void CvPlot::setFeatureType(')
ordinary_end=source.index('\tbool bUpdateSight = false;',ordinary_start)
ordinary=source[ordinary_start:ordinary_end]+'\tfeature=eNewValue; m_iFeatureVariety=iVariety; ++changes[1];\n}\n'
old='    void setFeatureType(FeatureTypes t, int v = -1) { feature = t; variety = v; ++changes[1]; }'
assert old in plot
plot=plot.replace(old,'    void setFeatureType(FeatureTypes eNewValue, int iVariety = -1);')
plot=plot.replace('int variety, changes[5];','int m_iFeatureVariety, changes[5], latitude;')
plot=plot.replace('variety(2)', 'm_iFeatureVariety(2), latitude(45)')
plot=plot.replace('return variety;', 'return m_iFeatureVariety;')
plot=plot.replace('    PlotNumTypes plotNum()', '    int getLatitude() const { return latitude; }\n    PlotNumTypes plotNum()')
start=core.index('struct Globals {');end=core.index('extern Globals GC;',start)+len('extern Globals GC;')
core=core[:start]+r'''
inline int range(int n,int low,int high){return std::max(low,std::min(n,high));}
struct FeatureArt {int varieties;int getNumVarieties()const{return varieties;}};
struct FeatureInfo {FeatureArt art;FeatureArt const* getArtInfo()const{return &art;}};
struct Globals {
    Map map;FeatureInfo infos[3];Map& getMap(){return map;}
    FeatureInfo const& getInfo(FeatureTypes f)const{assert(f>=0&&f<3);return infos[f];}
};
extern Globals GC;
'''+core[end:]
driver=r'''
#include "CvGameCoreDLL.h"
#include "PlotTempChangeMap.h"
#include <iostream>
Globals GC;
ORDINARY
TEMPORARY
int main(){int cases=0;int const durations[]={1,2,5};
    for(int varieties=1;varieties<=4;++varieties){
        for(int f=0;f<3;++f)GC.infos[f].art.varieties=varieties;
        for(int f=0;f<3;++f)for(int base=0;base<varieties;++base)
        for(int first=0;first<varieties;++first)for(int second=0;second<varieties;++second)
        for(int d=0;d<3;++d)for(int replacement=0;replacement<3;++replacement)
        for(int age=0;age<durations[d];++age){
            PlotTempChangeMap map;GC.map.changes=&map;CvPlot p(PLOT_0);
            p.feature=static_cast<FeatureTypes>(f);p.m_iFeatureVariety=base;
            p.setTempFeatureType(p.feature,first,durations[d]);
            assert(p.getFeatureVariety()==first);
            assert(map.getTempFeatureTimer(p)==(first!=base?durations[d]:0));
            for(int step=0;step<age;++step)map.update(p);
            int remaining=first!=base?durations[d]-age:0;
            p.setTempFeatureType(p.feature,second,durations[replacement]);
            if(second!=first)remaining=durations[replacement];
            assert(p.getFeatureVariety()==second&&map.getTempFeatureTimer(p)==remaining);
            if(remaining>0){std::pair<FeatureTypes,int> saved=map.getRealFeatureType(p);assert(saved.first==p.feature&&saved.second==base);}
            for(int tick=1;tick<=remaining;++tick){map.update(p);assert(p.feature==f);assert(p.getFeatureVariety()==(tick==remaining?base:second));}
            assert(p.getFeatureVariety()==base&&map.getTempFeatureTimer(p)==0);
            int changes=(first!=base)+(second!=first)+(remaining>0&&second!=base);
            assert(p.changes[1]==changes);
            map.update(p);assert(p.getFeatureVariety()==base&&p.changes[1]==changes);
            assert(p.terrain==TERRAIN_1&&p.bonus==BONUS_1&&p.improvement==IMPROVEMENT_1&&p.route==ROUTE_1);
            for(int k=0;k<5;++k)if(k!=1)assert(p.changes[k]==0);
            ++cases;
        }
        for(int f=0;f<3;++f)for(int base=0;base<varieties;++base){
            int const requests[]={-2,-1,varieties};
            for(int n=0;n<3;++n){PlotTempChangeMap map;GC.map.changes=&map;CvPlot p(PLOT_0);
                p.feature=static_cast<FeatureTypes>(f);p.m_iFeatureVariety=base;
                p.setTempFeatureType(p.feature,requests[n],5);
                assert(p.getFeatureVariety()==base&&map.getTempFeatureTimer(p)==0&&p.changes[1]==0);++cases;
            }
        }
    }
    int const emptyRequests[]={-1,0,1,99};
    for(int n=0;n<4;++n){PlotTempChangeMap map;GC.map.changes=&map;CvPlot p(PLOT_0);
        p.feature=NO_FEATURE;p.m_iFeatureVariety=0;p.setTempFeatureType(NO_FEATURE,emptyRequests[n],5);
        assert(p.feature==NO_FEATURE&&p.getFeatureVariety()==0&&map.getTempFeatureTimer(p)==0&&p.changes[1]==0);++cases;
    }
    std::cout<<cases<<" temporary feature-variety sequences passed\n";
}
'''
guard='if (eFeature != getFeatureType() ||\n\t\t(eFeature != NO_FEATURE && iVariety >= 0 && iVariety != getFeatureVariety() &&\n\t\tiVariety < GC.getInfo(eFeature).getArtInfo()->getNumVarieties()))'
assert guard in temporary
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'CvPlot.h').write_text(plot);(p/'CvGameCoreDLL.h').write_text(core)
    for name in ['PlotTempChangeMap.h','PlotTempChangeMap.cpp']:(p/name).write_text((root/'CvGameCoreDLL'/name).read_text())
    for name,body in [('positive',temporary),('type-only-guard',temporary.replace(guard,'if (eFeature != getFeatureType())'))]:
        (p/'check.cpp').write_text(driver.replace('ORDINARY',ordinary).replace('TEMPORARY',body))
        subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g','-I'+str(p),str(p/'check.cpp'),str(p/'PlotTempChangeMap.cpp'),'-o',str(p/'check')],check=True)
        r=subprocess.run([str(p/'check')],capture_output=True,text=True,
                         env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
        if name=='positive':
            assert r.returncode==0,r.stderr
            print(r.stdout.strip())
        else:
            assert body!=temporary and r.returncode!=0,name
            print('Negative control detected: '+name)
