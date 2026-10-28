from pathlib import Path
import os,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
s=Path(os.environ.get('ALIGN_SOURCE',str(root/'CvGameCoreDLL/AlignmentScore.cpp'))).read_text()
helper=s[s.index('// XANA:'):s.index('void AlignmentScore::nextTurn')] if '// XANA:' in s else ''
names=['changeAlignmentTowardsPositive','changeAlignmentTowardsNegative','changePermanentAlignmentTowardsPositive','changePermanentAlignmentTowardsNegative']
methods=[]
for name in names:
 a=s.index('void AlignmentScore::'+name+'(');methods.append(s[a:s.index('\n}',a)+2])
prefix=r'''
#include <cassert>
#include <climits>
#include <algorithm>
#include <utility>
#include <cmath>
#define MAX_INT INT_MAX
#define MIN_INT INT_MIN
class FDataStreamBase;
struct AlignmentValue {AlignmentValue(int h=0,int l=0):iHigh(h),iLow(l){} int iHigh,iLow;};
#define private public
#include "AlignmentScore.h"
#undef private
'''
test=r'''
int expected(int a,int b,bool sub,int upper){
 double n=double(a)+(sub?-double(b):double(b));
 n=std::max(double(INT_MIN),std::min(double(upper),n));return int(n);
}
int main(){
 int values[]={INT_MIN,INT_MIN+1,-100,-1,0,1,100,INT_MAX-1,INT_MAX};
 int caps[]={INT_MIN,-100,0,100,INT_MAX};
 for(int a=0;a<9;++a)for(int b=0;b<9;++b)for(int c=0;c<5;++c)for(int independent=0;independent<2;++independent){
  AlignmentScore x(0,0,0,0,caps[c],independent!=0);
  x.m_buffer[0].iHigh=x.m_buffer[0].iLow=values[a];
  x.changeAlignmentTowardsPositive(values[b]);
  assert(x.m_buffer[0].iHigh==(values[b]==0?values[a]:expected(values[a],values[b],false,caps[c])));
  assert(x.m_buffer[0].iLow==((independent||values[b]==0)?values[a]:expected(values[a],values[b],true,caps[c])));
  x.m_buffer[0].iHigh=x.m_buffer[0].iLow=values[a];
  x.changeAlignmentTowardsNegative(values[b]);
  assert(x.m_buffer[0].iLow==(values[b]==0?values[a]:expected(values[a],values[b],false,caps[c])));
  assert(x.m_buffer[0].iHigh==((independent||values[b]==0)?values[a]:expected(values[a],values[b],true,caps[c])));
  x.m_iPermHigh=x.m_iPermLow=values[a];
  x.changePermanentAlignmentTowardsPositive(values[b]);
  x.changePermanentAlignmentTowardsNegative(values[b]);
  assert(x.m_iPermHigh==expected(values[a],values[b],false,INT_MAX));
  assert(x.m_iPermLow==x.m_iPermHigh);
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'AlignmentScore.h').write_text((root/'CvGameCoreDLL/AlignmentScore.h').read_text());(p/'test.cpp').write_text(prefix+helper+'\n'.join(methods)+test)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-Wno-reorder','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: 810 edge combinations; actual four methods and class header; C++03/ASan/UBSan')
