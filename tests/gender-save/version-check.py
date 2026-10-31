#!/usr/bin/env python3
"""Actual AI gender-counter stream block/version; surrounding engine/map interfaces stubbed."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvPlayerAI.cpp').read_text()
def block(kind):
    start=source.index('void CvPlayerAI::'+kind+'(')
    op='Read' if kind=='read' else 'Write'
    start=source.index('\tpStream->'+op+'(MAX_PLAYERS, m_aiSameReligionCounter);',start)
    ending='\t\tm_arExpansionistHate.read(pStream); // </advc.130w>' if kind=='read' else '\tm_arExpansionistHate.write(pStream); // advc.130w'
    return source[start:source.index(ending,start)+len(ending)]
a=source.index('\tuint uiFlag;',source.index('void CvPlayerAI::write('))
b=source.index('\tpStream->Write(uiFlag);',a)+len('\tpStream->Write(uiFlag);')
version=source[a:b]
prefix=r'''
#include <cassert>
#include <cstddef>
#include <cstring>
#include <vector>
#include <iostream>
typedef unsigned int uint;
struct FDataStreamBase {
    std::vector<char> data;
    size_t pos;
    FDataStreamBase():pos(0){}
    template<class T>void Write(T v){char const* p=reinterpret_cast<char const*>(&v);data.insert(data.end(),p,p+sizeof(T));}
    template<class T>void Read(T* v){assert(pos+sizeof(T)<=data.size());std::memcpy(v,&data[pos],sizeof(T));pos+=sizeof(T);}
    void Write(int n,int const* values){for(int i=0;i<n;++i)Write(values[i]);}
    void Read(int n,int* values){for(int i=0;i<n;++i)Read(&values[i]);}
};
struct Map {
    int value,reads;
    Map():value(0),reads(0){}
    void read(FDataStreamBase* s){++reads;s->Read(&value);}
    void write(FDataStreamBase* s){s->Write(value);}
};
struct CvPlayerAI {
    int m_aiSameReligionCounter[MAX_PLAYERS],m_aiDifferentReligionCounter[MAX_PLAYERS],m_aiFavoriteCivicCounter[MAX_PLAYERS],
        m_aiFavoriteGenderCounter[MAX_PLAYERS],m_aiHateGenderCounter[MAX_PLAYERS],m_aiBonusTradeCounter[MAX_PLAYERS],
        m_aiPeacetimeTradeValue[MAX_PLAYERS],m_aiPeacetimeGrantValue[MAX_PLAYERS],m_aiGoldTradedTo[MAX_PLAYERS],m_aiAttitudeExtra[MAX_PLAYERS];
    Map m_arExpansionistHate;
    int* array(int i){switch(i){
        case 0:return m_aiSameReligionCounter;case 1:return m_aiDifferentReligionCounter;case 2:return m_aiFavoriteCivicCounter;
        case 3:return m_aiFavoriteGenderCounter;case 4:return m_aiHateGenderCounter;case 5:return m_aiBonusTradeCounter;
        case 6:return m_aiPeacetimeTradeValue;case 7:return m_aiPeacetimeGrantValue;case 8:return m_aiGoldTradedTo;default:return m_aiAttitudeExtra;}}
    CvPlayerAI(){for(int a=0;a<10;++a)for(int i=0;i<MAX_PLAYERS;++i)array(a)[i]=99;}
    void readCounters(FDataStreamBase*,uint);
    void writeCounters(FDataStreamBase*);
};
'''
code=prefix+'void CvPlayerAI::readCounters(FDataStreamBase* pStream,uint uiFlag){\n'+block('read')+'\n}\n'
code+='void CvPlayerAI::writeCounters(FDataStreamBase* pStream){\n'+version+'\n'+block('write')+'\n}\n'
code+=r'''
int main(){int const values[]={-100,-17,-1,0,1,17,100};int cases=0;
 for(uint flag=21;flag<=23;++flag)for(int seed=0;seed<7;++seed)for(int flavor=0;flavor<3;++flavor){
    CvPlayerAI original;
    for(int a=0;a<10;++a)for(int i=0;i<MAX_PLAYERS;++i)original.array(a)[i]=((a*31+i*7+seed*13+flavor*19)%201)-100;
    for(int i=0;i<MAX_PLAYERS;++i){original.m_aiFavoriteGenderCounter[i]=values[seed];original.m_aiHateGenderCounter[i]=-values[seed];}
    original.m_arExpansionistHate.value=1700+seed*10+flavor;
    FDataStreamBase stream;
    if(flag==23){original.writeCounters(&stream);uint written;stream.Read(&written);assert(written==23);}
    else {
        // Baseline encoding contains eight arrays, with neither gender array.
        for(int a=0;a<10;++a)if(a!=3&&a!=4)stream.Write(MAX_PLAYERS,original.array(a));
        if(flag>=22)original.m_arExpansionistHate.write(&stream);
    }
    size_t const boundary=stream.data.size();
    // Opaque following-object words also allow an old ungated reader to expose displacement without a buffer overread.
    for(int i=0;i<2*MAX_PLAYERS+2;++i)stream.Write(10000+i);
    CvPlayerAI loaded;loaded.readCounters(&stream,flag);
    assert(stream.pos==boundary);
    for(int a=0;a<10;++a)for(int i=0;i<MAX_PLAYERS;++i){
        int expected=(flag<23&&(a==3||a==4))?0:original.array(a)[i];
        assert(loaded.array(a)[i]==expected);
    }
    assert(loaded.m_arExpansionistHate.reads==(flag>=22?1:0));
    assert(loaded.m_arExpansionistHate.value==(flag>=22?original.m_arExpansionistHate.value:0));
    for(int i=0;i<2*MAX_PLAYERS+2;++i){int next;stream.Read(&next);assert(next==10000+i);}
    assert(stream.pos==stream.data.size());
    if(flag==23){FDataStreamBase rewritten;loaded.writeCounters(&rewritten);assert(rewritten.data.size()==boundary);assert(rewritten.data==std::vector<char>(stream.data.begin(),stream.data.begin()+boundary));}
    ++cases;
 }
 assert(cases==63);std::cout<<cases<<" counter-stream cases passed with MAX_PLAYERS="<<MAX_PLAYERS<<"\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(code)
    for players in [1,2,4,19]:
        subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g','-DMAX_PLAYERS='+str(players),str(p/'check.cpp'),'-o',str(p/'check')],check=True)
        subprocess.run([str(p/'check')],check=True,
                       env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
