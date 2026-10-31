#!/usr/bin/env python3
"""Actual unit stream tail/version statements; map encoding and engine stream stubbed."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvUnit.cpp').read_text()
read_start=source.index('void CvUnit::read(')
write_start=source.index('void CvUnit::write(',read_start)
reader=source[read_start:write_start]
reader=reader[reader.rindex('\tif (uiFlag >= 7)'):reader.rindex('}')]
flag_start=source.index('\tuint uiFlag;',write_start)
flag_end=source.index('\tpStream->Write(uiFlag);',flag_start)+len('\tpStream->Write(uiFlag);')
writer_start=source.index('\tm_aiTerrainDoubleMoveCount.write(pStream);',write_start)
writer_end=source.index('\n}',writer_start)
writer=source[flag_start:flag_end]+'\n'+source[writer_start:writer_end]
code=r'''
#include <cassert>
#include <cstddef>
#include <cstring>
#include <vector>
#include <iostream>
typedef unsigned int uint;
#define REPRO_TEST_END_WRITE()
struct FDataStreamBase {
    std::vector<char> bytes;
    size_t pos;
    FDataStreamBase():pos(0) {}
    template<class T> void Write(T value) {
        char const* p=reinterpret_cast<char const*>(&value);
        bytes.insert(bytes.end(),p,p+sizeof(T));
    }
    template<class T> void Read(T* value) {
        assert(pos+sizeof(T)<=bytes.size());
        std::memcpy(value,&bytes[pos],sizeof(T)); pos+=sizeof(T);
    }
};
struct Map {
    std::vector<int> values;
    int reads, legacyReads, resets;
    Map():reads(0),legacyReads(0),resets(0) {}
    void read(FDataStreamBase* s) {
        ++reads; int count; s->Read(&count);
        assert(count>=0 && count<=16);
        values.resize(count);
        for(int i=0;i<count;++i)s->Read(&values[i]);
    }
    template<class T> void readArray(FDataStreamBase* s) {
        ++legacyReads; values.resize(3);
        for(int i=0;i<3;++i){T v;s->Read(&v);values[i]=v;}
    }
    void write(FDataStreamBase* s) {
        s->Write(static_cast<int>(values.size()));
        for(size_t i=0;i<values.size();++i)s->Write(values[i]);
    }
    void reset(){++resets;values.clear();}
};
struct CvUnit {
    Map m_aiTerrainDoubleMoveCount, m_aiFeatureDoubleMoveCount,
        m_aiExtraTerrainAttackPercent, m_aiExtraTerrainDefensePercent,
        m_aiExtraFeatureAttackPercent, m_aiExtraFeatureDefensePercent,
        m_aiExtraUnitCombatModifier, m_aiPromotionExpireTurns;
    Map& map(int i) {
        switch(i) {
        case 0:return m_aiTerrainDoubleMoveCount;
        case 1:return m_aiFeatureDoubleMoveCount;
        case 2:return m_aiExtraTerrainAttackPercent;
        case 3:return m_aiExtraTerrainDefensePercent;
        case 4:return m_aiExtraFeatureAttackPercent;
        case 5:return m_aiExtraFeatureDefensePercent;
        default:return m_aiExtraUnitCombatModifier;
        }
    }
    void readTail(FDataStreamBase* pStream,uint uiFlag);
    void writeTail(FDataStreamBase* pStream);
};
'''
code+='void CvUnit::readTail(FDataStreamBase* pStream,uint uiFlag) {\n'+reader+'\n}\n'
code+='void CvUnit::writeTail(FDataStreamBase* pStream) {\n'+writer+'\n}\n'
code+=r'''
int main() {
    int cases=0;
    for(uint version=6;version<=9;++version)
    for(int length=0;length<=6;++length)
    for(int seed=0;seed<5;++seed)
    for(int mode=0;mode<(version==9?4:1);++mode) {
        CvUnit original;
        for(int m=0;m<7;++m)for(int i=0;i<(version<7?3:length);++i)
            original.map(m).values.push_back(seed*100+length*10+m*3+i);
        if(mode==1)original.m_aiPromotionExpireTurns.values.push_back(-1);
        if(mode==2)original.m_aiPromotionExpireTurns.values.push_back(0);
        if(mode==3) {
            original.m_aiPromotionExpireTurns.values.push_back(1);
            original.m_aiPromotionExpireTurns.values.push_back(17);
            original.m_aiPromotionExpireTurns.values.push_back(32767);
        }
        FDataStreamBase stream;
        if(version==9) {
            // Actual version declaration and writer tail, with unrelated unit fields omitted.
            original.writeTail(&stream);
            uint flag;stream.Read(&flag);assert(flag==9);
        } else {
            // Baseline unit tail has exactly these seven maps and no deadline field.
            for(int m=0;m<7;++m) {
                if(version>=7)original.map(m).write(&stream);
                else for(size_t i=0;i<original.map(m).values.size();++i)stream.Write(original.map(m).values[i]);
            }
        }
        size_t const endOfUnit=stream.bytes.size();
        uint const sentinel=0x1234abcd;
        stream.Write(sentinel);stream.Write(37);stream.Write(-49);
        CvUnit loaded;
        // Loading old versions must also clear prior state in reused objects.
        loaded.m_aiPromotionExpireTurns.values.push_back(99);
        loaded.readTail(&stream,version);
        assert(stream.pos==endOfUnit);
        for(int m=0;m<7;++m) {
            assert(loaded.map(m).values==original.map(m).values);
            assert(loaded.map(m).reads==(version>=7?1:0));
            assert(loaded.map(m).legacyReads==(version<7?1:0));
        }
        assert(loaded.m_aiPromotionExpireTurns.reads==(version>=9?1:0));
        assert(loaded.m_aiPromotionExpireTurns.legacyReads==0);
        assert(loaded.m_aiPromotionExpireTurns.resets==(version<9?1:0));
        assert(loaded.m_aiPromotionExpireTurns.values==original.m_aiPromotionExpireTurns.values);
        uint tail;int one,two;
        stream.Read(&tail);stream.Read(&one);stream.Read(&two);
        assert(tail==sentinel && one==37 && two==-49 && stream.pos==stream.bytes.size());
        if(version==9) {
            FDataStreamBase rewritten;loaded.writeTail(&rewritten);
            assert(rewritten.bytes.size()==endOfUnit);
            assert(std::vector<char>(stream.bytes.begin(),stream.bytes.begin()+endOfUnit)==rewritten.bytes);
        }
        ++cases;
    }
    assert(cases==245);
    std::cout<<cases<<" versioned unit-tail cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(code)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,
                   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
