#!/usr/bin/env python3
"""Actual hook/reset/locator/entry with simulated CvGame, map, Win32 and UI."""
from pathlib import Path
import ast
import os
import re
import subprocess
import tempfile
root=Path(__file__).resolve().parents[2]
tree=ast.parse((root/'tests/sid-discovery/check.py').read_text())
strings={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):strings[node.targets[0].id]=node.value.value
stub=strings['stub']
old='struct FakeGC { bool disabled; bool getDefineBOOL(char const*) { return disabled; } } GC;'
assert old in stub
stub=stub.replace(old,'struct FakeMap {int plots;int numPlots()const{return plots;}}; struct FakeGC {bool disabled;FakeMap map;FakeMap& getMap(){return map;}bool getDefineBOOL(char const*){return disabled;}} GC;')
setup=strings['checks'][strings['checks'].index('void put('):strings['checks'].index('int main()')]
source=(root/'CvGameCoreDLL/SelfMod.cpp').read_text();header=(root/'CvGameCoreDLL/SelfMod.h').read_text()
locator=source[source.index('class SidSaysLocator'):];locator=locator[:locator.index('// XANA:')]
entry=source[source.index('void Civ4BeyondSwordPatches::patchSidSays()'):]
game=(root/'CvGameCoreDLL/CvGame.cpp').read_text();game_header=(root/'CvGameCoreDLL/CvGame.h').read_text()
assert 'bool m_bSidSaysPatchTestDone' not in game_header
group=game_header[game_header.index('\tbool m_bScoreDirty;'):game_header.index('\tHandicapTypes m_eHandicap;')]
assert len(re.findall(r'\bbool m_b',group))==16
start=game.index('if (isFinalInitialized() &&',game.index('void CvGame::update()'))
hook=game[start:game.index('\n\t// XANA:',start)]
reset='smc::BtS_EXE.resetSidSaysDiscovery();'
assert reset in game[game.index('void CvGame::reset('):game.index('void CvGame::reset(')+15000]
driver=r'''
#include <cstddef>
#include <iostream>
namespace smc {Civ4BeyondSwordPatches BtS_EXE;}
std::vector<std::string> playerErrors;
void (*onError)()=NULL;
void Civ4BeyondSwordPatches::showErrorMsgToPlayer(CvWString msg){playerErrors.push_back(msg);if(onError)onError();}
struct GameHarness {
    bool ready;
    bool isFinalInitialized()const{return ready;}
    void resetHook(){RESET}
    void updateHook(){HOOK}
};
struct OldBoolGroup{bool values[16];int next;};
struct AddedBoolGroup{bool values[17];int next;};
GameHarness* activeGame=NULL;
int callbacks=0;
void reenter(){++callbacks;assert(callbacks==1);activeGame->updateHook();}
int main(){
    assert(sizeof(bool)==1&&sizeof(int)==4);
    assert(offsetof(OldBoolGroup,next)==16&&offsetof(AddedBoolGroup,next)==20);
    int cases=0;int const plots[]={-1,0,1,5};
    for(int ready=0;ready<2;++ready)for(int p=0;p<4;++p)for(int disabled=0;disabled<2;++disabled)for(int missing=0;missing<2;++missing){
        setup();smc::BtS_EXE.resetSidSaysDiscovery();GameHarness game;game.ready=ready!=0;
        GC.map.plots=plots[p];GC.disabled=disabled!=0;noModule=missing!=0;std::vector<byte> before=image;
        bool eligible=game.ready&&plots[p]>0;
        for(int frame=0;frame<100;++frame)game.updateHook();
        assert(smc::BtS_EXE.isSidSaysDiscoveryDone()==eligible);
        assert(!smc::BtS_EXE.isSidSaysPatched()&&image==before);
        assert(playerErrors.size()==(eligible&&!disabled?1u:0u));
        if(!eligible||disabled||missing)assert(reads==0);
        size_t first=reads;game.ready=true;GC.map.plots=5;game.updateHook();
        assert(smc::BtS_EXE.isSidSaysDiscoveryDone());
        if(eligible)assert(reads==first);
        GC.disabled=false;first=reads;game.updateHook();assert(reads==first);
        game.resetHook();assert(!smc::BtS_EXE.isSidSaysDiscoveryDone());
        setup();GC.map.plots=3;game.ready=false;game.updateHook();assert(reads==0);
        game.ready=true;game.updateHook();assert(reads>0&&playerErrors.size()==1);
        first=reads;game.updateHook();assert(reads==first&&playerErrors.size()==1);++cases;
    }
    setup();GC.map.plots=1;GameHarness game;game.ready=true;game.resetHook();activeGame=&game;onError=reenter;
    game.updateHook();assert(callbacks==1&&playerErrors.size()==1);onError=NULL;++cases;
    std::cout<<cases<<" scheduling/reset/reentry configurations passed\n";
}
'''
code=stub+'\n'+header.replace('#pragma once','')+'\n'+locator+'\n'+entry+'\nextern std::vector<std::string> playerErrors;\n'+setup+'\n'+driver.replace('RESET',reset).replace('HOOK',hook)
bad=code.replace('isFinalInitialized() && GC.getMap().numPlots() > 0 &&','')
assert bad!=code
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory)
    for name,text in [('positive',code),('no-readiness-gate',bad)]:
        (p/'check.cpp').write_text(text)
        subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
        r=subprocess.run([str(p/'check')],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
        if name=='positive':assert r.returncode==0,r.stderr;print(r.stdout.strip())
        else:assert r.returncode!=0,name;print('Negative control detected: '+name)
