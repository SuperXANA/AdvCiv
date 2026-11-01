from pathlib import Path
import subprocess
import tempfile
import os

root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/UWAI.cpp').read_text()
marker = '// XANA: 05-31-2025 First Impression Modified By Other Leader'
block = source.split(marker)[1]
harness = r'''
#include <vector>
#include <cassert>
#include <cstddef>
struct Globals { int n; int getNumLeaderHeadInfos() const { return n; } } GC;
struct Leader { int* m_piFirstImpressionModifier; };
#define FOR_EACH_ENUM(T) for(int eLoopLeaderHead=0; eLoopLeaderHead<GC.n; ++eLoopLeaderHead)
void collect(Leader& kLeader, std::vector<int*>& values) {
 int aiDevNull[100] = {};
 (void)aiDevNull;
 std::vector<int*>* paiPersonalityVector = &values;
 BLOCK
}
int main() {
 int counts[] = {0,1,2,99,100,101,149,257};
 int cases=0;
 for(unsigned c=0;c<sizeof(counts)/sizeof(counts[0]);++c) {
  GC.n=counts[c];
  for(int allocated=0; allocated<2; ++allocated) {
   Leader leader;
   leader.m_piFirstImpressionModifier=allocated ? new int[GC.n]() : NULL;
   int* original=leader.m_piFirstImpressionModifier;
   for(int i=0;allocated && i<GC.n;++i) original[i]=i%7-3;
   std::vector<int*> values;
   collect(leader,values);
   assert(values.size()==static_cast<std::size_t>(GC.n));
   if(allocated) assert(leader.m_piFirstImpressionModifier==original);
   for(int i=0;i<GC.n;++i) {
    assert(values[i]==&leader.m_piFirstImpressionModifier[i]);
    assert(*values[i]==(allocated ? i%7-3 : 0));
    *values[i]=i%11-5;
   }
   for(int i=0;i<GC.n;++i) assert(leader.m_piFirstImpressionModifier[i]==i%11-5);
   std::vector<int*> again;
   collect(leader,again);
   for(int i=0;i<GC.n;++i) assert(again[i]==values[i] && *again[i]==i%11-5);
   delete[] leader.m_piFirstImpressionModifier;
   ++cases;
  }
 }
 assert(cases==16);
}
'''.replace('BLOCK', block)
with tempfile.TemporaryDirectory() as tmp:
    cpp = Path(tmp) / 'check.cpp'
    cpp.write_text(harness)
    for sanitized in (False, True):
        exe = Path(tmp) / ('sanitized' if sanitized else 'normal')
        args = ['g++', '-std=c++03', '-fno-exceptions', '-Wall', '-Wextra', '-Werror', '-pedantic', str(cpp), '-o', str(exe)]
        if sanitized:
            args += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        subprocess.run(args, check=True)
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1')
        subprocess.run([str(exe)], check=True, env=env)
        print(('ASan/UBSan' if sanitized else 'normal') + ': 16 cases passed')
