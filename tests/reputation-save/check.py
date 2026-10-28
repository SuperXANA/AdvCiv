#!/usr/bin/env python3
"""Actual score methods and CvPlayer score stream blocks, engine stream stubbed."""
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
s=(root/'CvGameCoreDLL/ReputationScore.cpp').read_text()
def method(sig):
 start=s.index(sig); end=s.index('{',start)+1; depth=1
 while depth:
  depth+=(s[end]=='{')-(s[end]=='}'); end+=1
 return s[start:end]
p=(root/'CvGameCoreDLL/CvPlayer.cpp').read_text()
start=p.index('\tm_reputationScores.clear();',p.index('void CvPlayer::read('))
end=p.index('// XANA: 11-15-2025 Reputation System for Advanced Civ',start)
reader=p[start:end]
start=p.index('\tuint iSize = m_reputationScores.size();',p.index('void CvPlayer::write('))
end=p.index('// XANA: 11-15-2025 Reputation System for Advanced Civ',start)
writer=p[start:end]
code=r'''
#include <algorithm>
#include <vector>
#include <cmath>
#include <cassert>
#include <cstring>
typedef unsigned int uint;
#define FAssert(x) assert(x)
#define PROFILE_FUNC()
struct FDataStreamBase {
 std::vector<char> data; size_t pos;
 FDataStreamBase():pos(0) {}
 template<class T> void Write(T value) {
  char const* bytes=reinterpret_cast<char const*>(&value);
  data.insert(data.end(),bytes,bytes+sizeof(T));
 }
 void Write(int n,int const* values) { for(int i=0;i<n;++i) Write(values[i]); }
 template<class T> void Read(T* out) {
  assert(pos+sizeof(T)<=data.size()); std::memcpy(out,&data[pos],sizeof(T)); pos+=sizeof(T);
 }
 void Read(int n,int* values) { for(int i=0;i<n;++i) Read(&values[i]); }
};
#include "ReputationScore.h"
'''
code+='\n'.join(method(sig) for sig in ['void ReputationScore::grow(', 'int ReputationScore::get(', 'void ReputationScore::set(', 'void ReputationScore::read(', 'void ReputationScore::write('])
code+='\nstruct PlayerFixture { std::vector<ReputationScore> m_reputationScores;\nvoid readScores(FDataStreamBase* pStream,uint uiFlag) {\n'+reader+'\n}\nvoid writeScores(FDataStreamBase* pStream) const {\n'+writer+'\n}\n};\n'
code+=r'''
int main() {
 PlayerFixture a;
 for(int i=0;i<3;++i) {
  ReputationScore r;
  r.set(0,10*(i+1)); r.set(1,20*(i+1));
  a.m_reputationScores.push_back(r);
 }
 FDataStreamBase stream;
 PlayerFixture const& ca=a; ca.writeScores(&stream);
 unsigned int marker=0x1234abcd; stream.Write(marker);
 PlayerFixture b; b.m_reputationScores.resize(7);
 b.readScores(&stream,13);
 assert(b.m_reputationScores.size()==3);
 for(int i=0;i<3;++i) assert(b.m_reputationScores[i].get(2)==15*(i+1));
 unsigned int loaded; stream.Read(&loaded); assert(loaded==marker && stream.pos==stream.data.size());
 FDataStreamBase rewritten; b.writeScores(&rewritten);
 // Identical encoding, without the fixture's trailing sentinel.
 assert(rewritten.data.size()+sizeof(marker)==stream.data.size());
 assert(std::equal(rewritten.data.begin(),rewritten.data.end(),stream.data.begin()));
 FDataStreamBase empty; empty.Write(static_cast<uint>(0)); empty.Write(marker);
 b.readScores(&empty,13); assert(b.m_reputationScores.empty());
 empty.Read(&loaded); assert(loaded==marker);
 // Legacy sparse score encoding: matches host size_t, not a Windows ABI claim.
 FDataStreamBase legacy; legacy.Write(static_cast<uint>(1));
 legacy.Write(static_cast<size_t>(2)); legacy.Write(static_cast<char>(4));
 legacy.Write(0); legacy.Write(30); legacy.Write(2); legacy.Write(60); legacy.Write(marker);
 b.readScores(&legacy,12); assert(b.m_reputationScores.size()==1);
 assert(b.m_reputationScores[0].get(3)==30);
 legacy.Read(&loaded); assert(loaded==marker);
}
'''
with tempfile.TemporaryDirectory() as d:
 t=Path(d); (t/'ReputationScore.h').write_text((root/'CvGameCoreDLL/ReputationScore.h').read_text()); (t/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-g',str(t/'test.cpp'),'-o',str(t/'test')],check=True)
 subprocess.run([str(t/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
print('PASS: actual score methods + player score read/write blocks, const writer, count/order, roundtrip, empty and host-encoded legacy streams; C++03/ASan/UBSan.')
