#!/usr/bin/env python3
"""Actual vote-history blocks/version; raw-owner, stream and enum-map codec stand-ins."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvPlayerAI.cpp').read_text()
def block(kind):
    start=source.index('void CvPlayerAI::'+kind+'(')
    a=source.index('// <ChatGPT 2026-10-31: versioned vote-history persistence>',start)
    marker='// </ChatGPT 2026-10-31: versioned vote-history persistence>'
    b=source.index(marker,a)+len(marker)
    assert b<source.index('m_pUWAI->'+kind+'(pStream)',start)
    return source[a:b]
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
enum VoteTypes{NO_VOTE=-1,VOTE0=0,VOTE_FIXTURE_MAX=63};
enum CivTeamTypes{NO_CIV_TEAM=-1,TEAM0=0,TEAM_FIXTURE_MAX=63};
enum CivPlayerTypes{NO_CIV_PLAYER=-1,PLAYER0=0,PLAYER_FIXTURE_MAX=63};
struct Globals{int votes;int getNumVoteInfos()const{return votes;}} GC;
struct FDataStreamBase {
    std::vector<char> data;size_t pos;
    FDataStreamBase():pos(0){}
    template<class T>void Write(T value){char const* p=reinterpret_cast<char const*>(&value);data.insert(data.end(),p,p+sizeof(T));}
    template<class T>void Read(T* value){assert(pos+sizeof(T)<=data.size());std::memcpy(value,&data[pos],sizeof(T));pos+=sizeof(T);}
    void Write(int n,int const* values){for(int i=0;i<n;++i)Write(values[i]);}
    void Read(int n,int* values){for(int i=0;i<n;++i)Read(&values[i]);}
};
template<class E>int length();
template<>int length<VoteTypes>(){return GC.votes;}
template<>int length<CivTeamTypes>(){return NUM_CIV_TEAM_TYPES;}
template<>int length<CivPlayerTypes>(){return NUM_CIV_PLAYER_TYPES;}
// Models the inspected ArrayEnumMap<int,int,0> bool-presence/current-length payload shape.
// The actual engine EnumMap implementation and real save stream are not executed here.
template<class E,class V,class CV,int Default>struct ArrayEnumMap {
    std::vector<int> values;
    ArrayEnumMap():values(length<E>(),Default){}
    void set(E key,int value){assert(key>=0&&static_cast<size_t>(key)<values.size());values[key]=value;}
    int get(E key)const{assert(key>=0&&static_cast<size_t>(key)<values.size());return values[key];}
    void write(FDataStreamBase* stream)const{
        bool any=false;for(size_t i=0;i<values.size();++i)if(values[i]!=Default)any=true;
        stream->Write(any);if(any)stream->Write(static_cast<int>(values.size()),&values[0]);
    }
    void read(FDataStreamBase* stream){bool any;stream->Read(&any);if(any){assert(!values.empty());stream->Read(static_cast<int>(values.size()),&values[0]);}}
};
struct CvPlayerAI {
    int *m_aiVoteAlignment,*m_aiElectionTeamPreference,*m_aiCityAssignmentPlayerPreference;
    CvPlayerAI():m_aiVoteAlignment(NULL),m_aiElectionTeamPreference(NULL),m_aiCityAssignmentPlayerPreference(NULL){}
    ~CvPlayerAI(){delete[] m_aiVoteAlignment;delete[] m_aiElectionTeamPreference;delete[] m_aiCityAssignmentPlayerPreference;}
    int*& array(int n){return n==0?m_aiVoteAlignment:(n==1?m_aiElectionTeamPreference:m_aiCityAssignmentPlayerPreference);}
    int size(int n)const{return n==0?GC.votes:(n==1?NUM_CIV_TEAM_TYPES:NUM_CIV_PLAYER_TYPES);}
    void initialize(int value){for(int a=0;a<3;++a){int n=size(a);if(n>0){array(a)=new int[n];for(int i=0;i<n;++i)array(a)[i]=value;}}}
    void readHistory(FDataStreamBase*,uint);
    void writeHistory(FDataStreamBase*);
};
int patternValue(int pattern,int domain,int index){
    switch(pattern){
    case 0:case 1:return 0;
    case 2:return domain==0?index+1:0;
    case 3:return domain==1?index+1:0;
    case 4:return domain==2?index+1:0;
    case 5:return -1-index;
    case 6:return (index%2==0?1:-1)*(1+domain*7+index);
    default:return index%2==0?100:-100;
    }
}
'''
code=prefix+'void CvPlayerAI::readHistory(FDataStreamBase* pStream,uint uiFlag){\n'+block('read')+'\n}\n'
code+='void CvPlayerAI::writeHistory(FDataStreamBase* pStream){\n'+version+'\n'+block('write')+'\n}\n'
code+=r'''
int main(){int voteCounts[]={0,1,2,5};int cases=0;
 for(int count=0;count<4;++count)for(uint flag=21;flag<=23;++flag)
 for(int pattern=0;pattern<8;++pattern)for(int initialized=0;initialized<2;++initialized){
    GC.votes=voteCounts[count];CvPlayerAI original;
    if(pattern!=0){original.initialize(0);for(int a=0;a<3;++a)for(int i=0;i<original.size(a);++i)original.array(a)[i]=patternValue(pattern,a,i);}
    FDataStreamBase stream;
    if(flag==23){original.writeHistory(&stream);uint written;stream.Read(&written);assert(written==23);}
    size_t const boundary=stream.data.size();
    // Opaque following UWAI/object payload, not an implementation of the UWAI cache.
    int sentinels[]={0x1234567,-71,0,8675309};for(int i=0;i<4;++i)stream.Write(sentinels[i]);
    CvPlayerAI loaded;if(initialized)loaded.initialize(77);
    loaded.readHistory(&stream,flag);assert(stream.pos==boundary);
    for(int a=0;a<3;++a)for(int i=0;i<loaded.size(a);++i){
        assert(loaded.array(a)!=NULL);int expected=flag<23?0:patternValue(pattern,a,i);assert(loaded.array(a)[i]==expected);
    }
    for(int i=0;i<4;++i){int n;stream.Read(&n);assert(n==sentinels[i]);}assert(stream.pos==stream.data.size());
    if(flag==23){FDataStreamBase rewritten;loaded.writeHistory(&rewritten);assert(rewritten.data.size()==boundary);assert(rewritten.data==std::vector<char>(stream.data.begin(),stream.data.begin()+boundary));}
    ++cases;
 }
 assert(cases==192);std::cout<<cases<<" history-stream cases passed with teams="<<NUM_CIV_TEAM_TYPES<<" players="<<NUM_CIV_PLAYER_TYPES<<"\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(code)
    for teams,players in [(1,1),(2,3),(18,18)]:
        subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g','-DNUM_CIV_TEAM_TYPES='+str(teams),
                        '-DNUM_CIV_PLAYER_TYPES='+str(players),str(p/'check.cpp'),'-o',str(p/'check')],check=True)
        subprocess.run([str(p/'check')],check=True,env=dict(os.environ,
                       ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
