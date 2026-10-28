#!/usr/bin/env python3
"""Actual ReputationScore header + grow/get/set methods; engine stream stubbed."""
from pathlib import Path
import subprocess, tempfile, os
root = Path(__file__).resolve().parents[2]
source = (root/'CvGameCoreDLL/ReputationScore.cpp').read_text()
def method(signature):
    start=source.index(signature); end=source.index('{',start)+1; depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}'); end+=1
    return source[start:end]
code='''#include <algorithm>
#include <vector>
#include <cmath>
#include <climits>
#include <cassert>
class FDataStreamBase;
#define FAssert(x) assert(x)
#include "ReputationScore.h"
'''
code+='\n'.join(method(s) for s in ['void ReputationScore::grow(', 'int ReputationScore::get(', 'void ReputationScore::set('])
code+='''
int main() {
 ReputationScore r;
 assert(r.get(-1)==0 && r.get(0)==0 && r.get(1)==0);
 r.set(0,10); assert(r.get(1)==10);
 r.set(1,20); assert(r.get(2)==15);
 r.set(2,30); r.set(3,40); r.set(4,100);
 assert(r.get(4)==25); // all four completed turns; excludes current 100
 assert(r.get(5)==48); // (20+30+40+100)/4 = 47.5
 r.changeSampleSize(-3); assert(r.get(4)==40);
 r.reset(); r.changeSampleSize(96);
 for(int i=0;i<100;++i) r.set(i,INT_MAX);
 assert(r.get(100)==INT_MAX);
 for(int i=0;i<100;++i) r.set(i,INT_MIN);
 assert(r.get(100)==INT_MIN);
 for(int i=0;i<100;++i) r.set(i,i%2?INT_MIN:INT_MAX);
 assert(r.get(100)==-1); // -0.5, ties away from zero
 r.reset(); r.set(0,-10); r.set(1,-11); assert(r.get(2)==-11);
 r.clear(); assert(r.get(1)==0);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d); (p/'ReputationScore.h').write_text((root/'CvGameCoreDLL/ReputationScore.h').read_text())
 (p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-g',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
print('PASS: actual header and grow/get/set; C++03 + ASan/UBSan; stream/engine excluded.')
