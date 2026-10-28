#!/usr/bin/env python3
"""Actual hated-history method and marked cache blocks, with engine stubs."""
import os
import pathlib
import re
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
def source(name):
    return (pathlib.Path(os.environ.get('HATED_SOURCE_DIR', root / 'CvGameCoreDLL')) / name).read_text()
cpp = source('CvPlayerAI.cpp')
info = source('CvInfo_Civilization.cpp')
header = source('CvInfo_Civilization.h')
ai_header = source('CvPlayerAI.h')
def method(name):
    start = cpp.index('void CvPlayerAI::' + name + '(')
    return cpp[start:cpp.index('\n}', start) + 2]
name = 'AI_changeHateCivicCounter'
decl = next(s.strip() for s in ai_header.splitlines() if 'void '+name+'(' in s)
fields = re.findall(r'^\s*int (m_iHate(?:Religion|Civic)Attitude\w+);', header, re.M)
assert len(fields) == 6
marker = '// XANA: 05-24-2025 Hate Civic and Religion Diplomacy'
blocks = info.split(marker)[1::2]
read = [b for b in blocks if 'stream->Read(&m_iHate' in b]
write = [b for b in blocks if 'stream->Write(m_iHate' in b]
assert len(read) == len(write) == 2
fixture = r'''
#include <cassert>
#include <vector>
#include <cstddef>
enum { MAX_PLAYERS=4 };
typedef int PlayerTypes;
#define FAssertMsg(c,m) assert(c)
#define FAssert(c) assert(c)
struct CvPlayerAI {
    int m_aiFavoriteCivicCounter[MAX_PLAYERS],m_aiHateCivicCounter[MAX_PLAYERS];
    int AI_getHateCivicCounter(PlayerTypes p)const{return m_aiHateCivicCounter[p];}
    DECL
};
METHOD
struct Stream {
    std::vector<int> data; std::size_t pos;
    Stream():pos(0){}
    void Write(int n){data.push_back(n);}
    void Read(int* n){assert(pos<data.size());*n=data[pos++];}
};
struct CvLeaderHeadInfo {
    FIELDS
    void read(Stream* stream){READ}
    void write(Stream* stream){WRITE}
};
int main(){
    CvPlayerAI player;
    for(int p=0;p<MAX_PLAYERS;++p){
        player.m_aiFavoriteCivicCounter[p]=17+p;
        player.m_aiHateCivicCounter[p]=3+p;
    }
    for(int target=0;target<MAX_PLAYERS;++target){
        int before[MAX_PLAYERS];
        for(int p=0;p<MAX_PLAYERS;++p)before[p]=player.m_aiHateCivicCounter[p];
        player.AI_changeHateCivicCounter(target,2);
        for(int p=0;p<MAX_PLAYERS;++p){
            assert(player.m_aiFavoriteCivicCounter[p]==17+p);
            assert(player.m_aiHateCivicCounter[p]==before[p]+(p==target?2:0));
        }
        player.AI_changeHateCivicCounter(target,-2);
        player.AI_changeHateCivicCounter(target,0);
        for(int p=0;p<MAX_PLAYERS;++p)assert(player.m_aiHateCivicCounter[p]==before[p]);
    }
    CvLeaderHeadInfo from,to;
    INIT
    Stream stream;from.write(&stream);
    assert(stream.data.size()==6);
    for(int i=0;i<6;++i)assert(stream.data[i]==100+7*i);
    stream.Write(1234567);to.read(&stream);
    CHECK
    assert(stream.pos==6);int sentinel=0;stream.Read(&sentinel);assert(sentinel==1234567);
}
'''
replacements = dict(DECL=decl, METHOD=method(name),
    FIELDS='\n'.join('int '+f+';' for f in fields), READ='\n'.join(read), WRITE='\n'.join(write),
    INIT='\n'.join('from.%s=%d;to.%s=0;' % (f,100+7*i,f) for i,f in enumerate(fields)),
    CHECK='\n'.join('assert(to.%s==from.%s);' % (f,f) for f in fields))
for key,value in replacements.items():
    fixture=fixture.replace(key,value)
with tempfile.TemporaryDirectory() as temp:
    cpp_path=pathlib.Path(temp)/'check.cpp'
    exe=pathlib.Path(temp)/'check'
    cpp_path.write_text(fixture)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer',str(cpp_path),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True,env=dict(os.environ,
        ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('Hated history isolation and six-field cache checks passed: C++03/ASan/UBSan')
