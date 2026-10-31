#!/usr/bin/env python3
"""Promotion debug suffix only; actual block with reduced string/game interfaces."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source_path=root/'CvGameCoreDLL/CvGameTextMgr.cpp'
if source_path.exists():
    source=source_path.read_text()
    start=source.index('int const iExpireTurn = pUnit->getPromotionExpireTurn')
    end=source.index('\n\t\t\t\t}',start)
    block=source[start:end]
else:
    block=(root/'help-block.txt').read_text()
prefix=r'''
#include <cassert>
#include <climits>
#include <cwchar>
#include <string>
#include <iostream>
struct CvWString : std::wstring {
    static CvWString format(wchar_t const* f,int n){wchar_t b[64];std::swprintf(b,64,f,n);CvWString s;s.assign(b);return s;}
};
struct Unit {int deadline;int getPromotionExpireTurn(int)const{return deadline;}};
struct Game {int turn;int getGameTurn()const{return turn;}};
struct Globals {Game game;Game& getGame(){return game;}} GC;
CvWString suffix(Unit* pUnit){int eLoopPromotion=0;CvWString szTempBuffer;BLOCK return szTempBuffer;}
int main(){int count=0;
    int const deadlines[]={-1,0,1,32767,32768,65536,INT_MAX};
    int const turns[]={0,1,32766,32767,32768,65536,INT_MAX};
    for(int d=0;d<7;++d)for(int t=0;t<7;++t){
        Unit u;u.deadline=deadlines[d];GC.game.turn=turns[t];
        CvWString actual=suffix(&u);std::wstring expected;
        if(u.deadline>0&&u.deadline>=GC.game.turn){wchar_t b[64];std::swprintf(b,64,L"(%d)",u.deadline-GC.game.turn);expected=b;}
        assert(actual==expected);++count;
    }
    std::cout<<count<<" promotion-help suffix cases passed\n";
}
'''
code=prefix.replace('BLOCK',block)
old=code.replace('szTempBuffer.append(CvWString::format(L"(%d)", iExpireTurn - iGameTurn));',
                 'szTempBuffer.append(L"(%d)", iExpireTurn - iGameTurn);')
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory)
    for name,text in [('positive',code),('length-based-append',old)]:
        (p/'check.cpp').write_text(text)
        subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
        r=subprocess.run([str(p/'check')],capture_output=True,text=True,
                         env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
        if name=='positive':
            assert r.returncode==0,r.stderr
            print(r.stdout.strip())
        else:
            assert text!=code and r.returncode!=0,name
            print('Negative control detected: '+name)
