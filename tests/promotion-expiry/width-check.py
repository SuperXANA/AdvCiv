#!/usr/bin/env python3
"""Actual unit map declaration and read/write/get/set/expiry statements.

Engine interfaces and the bool-plus-compact-array EnumMap codec are stand-ins.
No complete engine save or MSVC result is implied by this fixture.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvUnit.cpp').read_text()
header = (root / 'CvGameCoreDLL/CvUnit.h').read_text()

def function(text, name):
    start = text.index(name)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

reader = function(source, 'void CvUnit::read(')
reader = reader[reader.rindex('\tif (uiFlag >= 7)'):reader.rindex('}')]
write_start = source.index('void CvUnit::write(')
flag_start = source.index('\tuint uiFlag;', write_start)
flag_end = source.index('\tpStream->Write(uiFlag);', flag_start) + len('\tpStream->Write(uiFlag);')
tail_start = source.index('\tm_aiTerrainDoubleMoveCount.write(pStream);', write_start)
tail_end = source.index('\n}', tail_start)
writer = source[flag_start:flag_end] + '\n' + source[tail_start:tail_end]
member = re.search(r'ArrayEnumMap<PromotionTypes,int,\w+> m_aiPromotionExpireTurns;', header).group()
getter = function(header, 'int getPromotionExpireTurn(')
setter = function(source, 'void CvUnit::setPromotionExpireTurn(')
expire = function(source, 'void CvUnit::doExpireTempPromotions(')

prefix = r'''
#include <cassert>
#include <climits>
#include <cstring>
#include <vector>
#include <iostream>
typedef unsigned int uint;
typedef int PromotionTypes;
static int gCount=1;
#define FAssert(x) assert(x)
#define FOR_EACH_ENUM(x) for(PromotionTypes eLoopPromotion=0;eLoopPromotion<gCount;++eLoopPromotion)
#define REPRO_TEST_END_WRITE()
struct FDataStreamBase {
    std::vector<char> bytes;size_t pos;
    FDataStreamBase():pos(0){}
    template<class T>void Write(T v){char const* p=reinterpret_cast<char const*>(&v);bytes.insert(bytes.end(),p,p+sizeof(T));}
    template<class T>void Read(T* p){assert(pos+sizeof(T)<=bytes.size());std::memcpy(p,&bytes[pos],sizeof(T));pos+=sizeof(T);}
};
template<class E,class V,class C> struct ArrayEnumMap {
    std::vector<C> values;
    ArrayEnumMap():values(gCount,0){}
    void reset(){values.assign(gCount,0);}
    V get(E i)const{return values.at(i);}
    void set(E i,V v){values.at(i)=static_cast<C>(v);}
    void write(FDataStreamBase* s)const{
        bool any=false;for(int i=0;i<gCount;++i)any=any||values[i]!=0;
        s->Write(any);if(any)for(int i=0;i<gCount;++i)s->Write(values[i]);
    }
    void read(FDataStreamBase* s){bool any;s->Read(&any);if(any)for(int i=0;i<gCount;++i)s->Read(&values[i]);}
    template<class T>void readArray(FDataStreamBase* s){for(int i=0;i<gCount;++i){T v;s->Read(&v);values[i]=static_cast<C>(v);}}
};
typedef ArrayEnumMap<int,int,int> Map;
struct Game {int turn;int getGameTurn()const{return turn;}};
struct Globals {Game game;Game& getGame(){return game;}} GC;
struct CvUnit {
    Map m_aiTerrainDoubleMoveCount,m_aiFeatureDoubleMoveCount,m_aiExtraTerrainAttackPercent,
        m_aiExtraTerrainDefensePercent,m_aiExtraFeatureAttackPercent,m_aiExtraFeatureDefensePercent,
        m_aiExtraUnitCombatModifier;
    MEMBER
    std::vector<bool> held;
    CvUnit():held(gCount,true){}
    GETTER
    void setPromotionExpireTurn(PromotionTypes,int);
    void doExpireTempPromotions();
    bool isHasPromotion(PromotionTypes p)const{return held.at(p);}
    void setHasPromotion(PromotionTypes p,bool b){held.at(p)=b;if(!b)m_aiPromotionExpireTurns.set(p,0);}
    void readTail(FDataStreamBase* pStream,uint uiFlag){READER}
    void writeTail(FDataStreamBase* pStream){WRITER}
};
SETTER
EXPIRE
int main(){
    assert(sizeof(int)==4&&sizeof(short)==2);
    int cases=0;
    int const values[]={-1,0,1,32766,32767,32768,65535,65536,INT_MAX};
    for(gCount=1;gCount<=5;++gCount)for(int n=0;n<9;++n){
        CvUnit u;u.setPromotionExpireTurn(0,values[n]);
        assert(u.getPromotionExpireTurn(0)==values[n]);
        GC.game.turn=values[n]>0?values[n]-1:0;u.doExpireTempPromotions();
        assert(u.isHasPromotion(0));
        if(values[n]>0){GC.game.turn=values[n];u.doExpireTempPromotions();assert(!u.isHasPromotion(0));}
        ++cases;
    }
    int const counts[]={0,1,2,5};
    for(int count=0;count<4;++count)for(uint version=6;version<=10;++version)
    for(int seed=0;seed<9;++seed)for(int stale=0;stale<2;++stale){
        gCount=counts[count];FDataStreamBase stream;
        for(int m=0;m<7;++m){
            if(version<7){for(int i=0;i<gCount;++i)stream.Write(10+m+i);}
            else{Map a;for(int i=0;i<gCount;++i)a.set(i,10+m+i);a.write(&stream);}
        }
        int deadline=values[seed];
        if(version==9&&deadline>SHRT_MAX)deadline=SHRT_MAX;
        size_t prefixBytes=stream.bytes.size();
        if(version==9){ArrayEnumMap<int,int,short> a;for(int i=0;i<gCount;++i)a.set(i,deadline);a.write(&stream);}
        else if(version>=10){Map a;for(int i=0;i<gCount;++i)a.set(i,deadline);a.write(&stream);}
        size_t boundary=stream.bytes.size();
        if(version>=9)assert(boundary-prefixBytes==sizeof(bool)+(gCount>0&&deadline!=0?gCount*(version==9?sizeof(short):sizeof(int)):0));
        stream.Write(0x12345678);stream.Write(-9876543);
        CvUnit u;for(int i=0;i<gCount;++i)u.m_aiPromotionExpireTurns.set(i,stale?17:0);
        u.readTail(&stream,version);assert(stream.pos==boundary);
        for(int i=0;i<gCount;++i)assert(u.getPromotionExpireTurn(i)==(version>=9?deadline:0));
        int sentinel;stream.Read(&sentinel);assert(sentinel==0x12345678);stream.Read(&sentinel);assert(sentinel==-9876543);
        FDataStreamBase out;u.writeTail(&out);uint emitted;out.Read(&emitted);assert(emitted==10);
        CvUnit restored;restored.readTail(&out,emitted);assert(out.pos==out.bytes.size());
        for(int i=0;i<gCount;++i)assert(restored.getPromotionExpireTurn(i)==u.getPromotionExpireTurn(i));
        ++cases;
    }
    std::cout<<cases<<" full-width/deadline-codec cases passed\n";
}
'''
code = prefix.replace('MEMBER', member).replace('GETTER', getter).replace('READER', reader).replace('WRITER', writer).replace('SETTER', setter).replace('EXPIRE', expire)
variants = [('positive',code),
            ('short-runtime-storage',code.replace(member,member.replace(',int> m_ai',',short> m_ai'))),
            ('wrong-version9-codec',code.replace('else if (uiFlag == 9)','else if (uiFlag == 9)').replace('ArrayEnumMap<PromotionTypes,int,short> aiLegacyExpireTurns','ArrayEnumMap<PromotionTypes,int,int> aiLegacyExpireTurns')),
            ('stale-empty-map',code.replace('m_aiPromotionExpireTurns.reset();','')),
            ('old-writer-version',code.replace('uiFlag = 10;', 'uiFlag = 9;'))]
with tempfile.TemporaryDirectory() as directory:
    path=Path(directory)
    for name,text in variants:
        (path/'check.cpp').write_text(text)
        subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g',str(path/'check.cpp'),'-o',str(path/'check')],check=True)
        result=subprocess.run([str(path/'check')],capture_output=True,text=True,
                              env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
        if name=='positive':
            assert result.returncode==0,result.stderr
            print(result.stdout.strip())
        else:
            assert text!=code and result.returncode!=0,name
            print('Negative control detected: '+name)
