#!/usr/bin/env python3
"""Actual religion-weight methods with distinct enums, GC and owning-info stand-ins."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parent
if not (root/'CvGameCoreDLL').exists():root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvInfo_Civilization.cpp').read_text()
start=source.index('int CvLeaderHeadInfo::getReligionWeightModifier(')
end=source.index('// XANA: 06-21-2026 Religion Adoption Weights',start)
methods=source[start:end]
prefix=r'''
#include <cassert>
#include <cstddef>
#include <cstdlib>
#include <new>
#include <vector>
#include <iostream>
int liveArrays=0;
bool failArray=false;
void* operator new[](std::size_t n) throw(std::bad_alloc) {
    if(failArray)throw std::bad_alloc();
    void* p=std::malloc(n?n:1);if(p==NULL)throw std::bad_alloc();++liveArrays;return p;
}
void operator delete[](void* p) throw(){if(p!=NULL){--liveArrays;std::free(p);}}
enum ReligionTypes {NO_RELIGION=-1,RELIGION_ZERO=0,RELIGION_FIXTURE_LIMIT=127};
struct Globals {int count;int getNumReligionInfos()const{return count;}} GC;
// Exercise release-mode bounds behavior; production assertions are diagnostics, not guards.
#define FAssertBounds(lo,hi,index) ((void)0)
struct CvLeaderHeadInfo {
    int* m_piReligionWeightModifier;
    CvLeaderHeadInfo():m_piReligionWeightModifier(NULL){}
    ~CvLeaderHeadInfo(){delete[] m_piReligionWeightModifier;}
    int getReligionWeightModifier(ReligionTypes)const;
    void changeReligionWeightModifier(ReligionTypes,int);
    void setReligionWeightModifier(ReligionTypes,int);
};
'''
main=r'''
int main(){int const baseline=liveArrays;int cases=0;
    int seeds[]={-10,0,7},values[]={-12,0,9},changes[]={-4,0,6};
    for(int count=0;count<=6;++count)for(int allocated=0;allocated<2;++allocated)
    for(int index=-2;index<=count+1;++index)for(int seed=0;seed<3;++seed)
    for(int value=0;value<3;++value)for(int delta=0;delta<3;++delta){
        GC.count=count;
        {
            CvLeaderHeadInfo info;std::vector<int> expected(count,0);
            if(allocated){info.m_piReligionWeightModifier=new int[count];
                for(int i=0;i<count;++i)info.m_piReligionWeightModifier[i]=expected[i]=seeds[seed]+i;}
            ReligionTypes const id=static_cast<ReligionTypes>(index);
            bool const valid=index>=0&&index<count;
            assert(info.getReligionWeightModifier(id)==(valid?expected[index]:0));
            info.setReligionWeightModifier(id,values[value]);
            if(valid)expected[index]=values[value];
            info.changeReligionWeightModifier(id,changes[delta]);
            if(valid)expected[index]+=changes[delta];
            assert(info.getReligionWeightModifier(id)==(valid?expected[index]:0));
            for(int i=0;i<count;++i)assert(info.getReligionWeightModifier(static_cast<ReligionTypes>(i))==expected[i]);
            if(!allocated&&(!valid||(values[value]==0&&changes[delta]==0)))assert(info.m_piReligionWeightModifier==NULL);
        }
        assert(liveArrays==baseline);++cases;
    }
    // First-write allocation failure preserves the implicit zero map; retry then succeeds.
    for(int count=1;count<=6;++count)for(int index=0;index<count;++index)for(int change=0;change<2;++change){
        GC.count=count;CvLeaderHeadInfo info;ReligionTypes const id=static_cast<ReligionTypes>(index);
        failArray=true;bool threw=false;
        try {if(change)info.changeReligionWeightModifier(id,5);else info.setReligionWeightModifier(id,-3);}
        catch(std::bad_alloc const&){threw=true;}
        failArray=false;assert(threw&&info.m_piReligionWeightModifier==NULL);
        for(int i=0;i<count;++i)assert(info.getReligionWeightModifier(static_cast<ReligionTypes>(i))==0);
        if(change)info.changeReligionWeightModifier(id,5);else info.setReligionWeightModifier(id,-3);
        assert(info.getReligionWeightModifier(id)==(change?5:-3));++cases;
    }
    // Invalid and zero writes must not attempt allocation even when allocation is disabled.
    for(int count=0;count<=6;++count){
        GC.count=count;CvLeaderHeadInfo info;failArray=true;
        info.setReligionWeightModifier(NO_RELIGION,7);
        info.changeReligionWeightModifier(static_cast<ReligionTypes>(count),7);
        if(count>0){info.setReligionWeightModifier(RELIGION_ZERO,0);info.changeReligionWeightModifier(RELIGION_ZERO,0);}
        failArray=false;assert(info.m_piReligionWeightModifier==NULL);++cases;
    }
    assert(liveArrays==baseline);assert(cases==2695);
    std::cout<<cases<<" religion-weight mutation/bounds/allocation-failure cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(prefix+methods+main)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
