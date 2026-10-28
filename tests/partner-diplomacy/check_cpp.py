#!/usr/bin/env python3
"""Actual response declarations/getters/cache methods with a simulated stream."""
from pathlib import Path
import os
import subprocess
import tempfile
root = Path(__file__).resolve().parents[2]
dll = root / 'CvGameCoreDLL'
ch = (dll / 'CvInfo_Civilization.h').read_text()
mh = (dll / 'CvInfo_Misc.h').read_text()
cc = (dll / 'CvInfo_Civilization.cpp').read_text()
mc = (dll / 'CvInfo_Misc.cpp').read_text()

def body(text, signature):
    start = text.index(signature)
    opening, depth = text.index('{', start), 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def declaration(text, name):
    start = text.index('class ' + name)
    return text[start:text.index('\n};', start) + 3]

fields = ['OtherCivilizationTypes', 'OtherNotCivilizationTypes', 'OtherLeaderHeadTypes', 'OtherNotLeaderHeadTypes']
definitions = []
for name in ['CvDiplomacyResponse', 'CvDiplomacyInfo', 'CvDiplomacyTextInfo']:
    text = mc if name == 'CvDiplomacyTextInfo' else cc
    for field in fields:
        definitions.append(body(text, 'bool ' + name + '::get' + field + '('))
for signature in ['CvDiplomacyResponse::CvDiplomacyResponse()', 'CvDiplomacyResponse::~CvDiplomacyResponse()',
                  'int CvDiplomacyResponse::getNumDiplomacyText()', 'CvDiplomacyInfo::~CvDiplomacyInfo()',
                  'int CvDiplomacyInfo::getNumResponses()', 'void CvDiplomacyResponse::read(FDataStreamBase',
                  'void CvDiplomacyResponse::write(FDataStreamBase']:
    definitions.append(body(cc, signature))
for signature in ['CvDiplomacyTextInfo::CvDiplomacyTextInfo()', 'void CvDiplomacyTextInfo::init(int',
                  'void CvDiplomacyTextInfo::uninit()', 'int CvDiplomacyTextInfo::getNumResponses()',
                  'void CvDiplomacyTextInfo::Response::read(', 'void CvDiplomacyTextInfo::Response::write(',
                  'void CvDiplomacyTextInfo::read(FDataStreamBase', 'void CvDiplomacyTextInfo::write(FDataStreamBase']:
    definitions.append(body(mc, signature))
stub = r'''
#include <cassert>
#include <cstddef>
#include <cstring>
#include <string>
#include <vector>
#define ENABLE_XML_FILE_CACHE 1
#define SAFE_DELETE_ARRAY(p) { delete[] (p); (p) = NULL; }
#define SAFE_DELETE(p) { delete (p); (p) = NULL; }
#define FAssertBounds(low, high, value) assert((value) >= (low) && (value) < (high))
typedef unsigned int uint;
typedef char TCHAR;
typedef std::string CvString;
const int NUM_ATTITUDE_TYPES = 2, NUM_DIPLOMACYPOWER_TYPES = 2;
struct Globals {
    int getNumCivilizationInfos() const { return 3; }
    int getNumLeaderHeadInfos() const { return 4; }
} GC;
class CvXMLLoadUtility;
struct FDataStreamBase {
    std::vector<unsigned char> bytes;
    size_t pos;
    FDataStreamBase() : pos(0) {}
    void rawWrite(void const* p, size_t n) {
        assert(p != NULL || n == 0);
        unsigned char const* b = static_cast<unsigned char const*>(p);
        bytes.insert(bytes.end(), b, b + n);
    }
    void rawRead(void* p, size_t n) {
        assert(pos + n <= bytes.size()); memcpy(p, &bytes[pos], n); pos += n;
    }
    void Write(uint n) { rawWrite(&n, sizeof(n)); }
    void Write(int n) { rawWrite(&n, sizeof(n)); }
    void Read(uint* n) { rawRead(n, sizeof(*n)); }
    void Read(int* n) { rawRead(n, sizeof(*n)); }
    void Write(int n, bool const* p) {
        assert(n == 0 || p != NULL);
        for (int i = 0; i < n; ++i) bytes.push_back(p[i] ? 1 : 0);
    }
    void Read(int n, bool* p) { for (int i = 0; i < n; ++i) { assert(pos < bytes.size()); p[i] = bytes[pos++] != 0; } }
    void WriteString(int n, CvString const* p) {
        for (int i = 0; i < n; ++i) { Write(static_cast<int>(p[i].size())); rawWrite(p[i].data(), p[i].size()); }
    }
    void ReadString(int n, CvString* p) {
        for (int i = 0; i < n; ++i) { int size; Read(&size); assert(size >= 0 && pos + size <= bytes.size()); p[i].assign(reinterpret_cast<char const*>(&bytes[pos]), size); pos += size; }
    }
};
struct CvInfoBase {
    void read(FDataStreamBase*) {}
    void write(FDataStreamBase*) {}
};
#include "PartnerDiplomacyCache.h"
'''
checks = r'''
template<class T> void seedOriginal(T& r) {
    r.m_iNumDiplomacyText = 1; r.m_paszDiplomacyText = new CvString[1]; r.m_paszDiplomacyText[0] = "fixture";
    r.m_pbCivilizationTypes = new bool[3](); r.m_pbLeaderHeadTypes = new bool[4]();
    r.m_pbAttitudeTypes = new bool[2](); r.m_pbDiplomacyPowerTypes = new bool[2]();
}
struct TestResponse : CvDiplomacyResponse {
    void seed() {
        m_iNumDiplomacyText = 1; m_paszDiplomacyText = new CvString[1]; m_paszDiplomacyText[0] = "fixture";
        m_pbCivilizationTypes = new bool[3](); m_pbLeaderHeadTypes = new bool[4]();
        m_pbAttitudeTypes = new bool[2](); m_pbDiplomacyPowerTypes = new bool[2]();
    }
    void allow() {
        m_pbOtherCivilizationTypes = new bool[3](); m_pbOtherCivilizationTypes[1] = true;
        m_pbOtherNotCivilizationTypes = new bool[3](); m_pbOtherNotCivilizationTypes[2] = true;
        m_pbOtherLeaderHeadTypes = new bool[4](); m_pbOtherLeaderHeadTypes[3] = true;
        m_pbOtherNotLeaderHeadTypes = new bool[4](); m_pbOtherNotLeaderHeadTypes[0] = true;
    }
    void writeOld(FDataStreamBase& s) {
        s.Write(uint(0)); s.Write(m_iNumDiplomacyText);
        s.Write(3, m_pbCivilizationTypes); s.Write(4, m_pbLeaderHeadTypes);
        s.Write(2, m_pbAttitudeTypes); s.Write(2, m_pbDiplomacyPowerTypes); s.WriteString(1, m_paszDiplomacyText);
    }
};
struct TestInfo : CvDiplomacyInfo { void add(CvDiplomacyResponse* p) { m_pResponses.push_back(p); } };
void allow(CvDiplomacyTextInfo::Response& r) {
    r.m_pbOtherCivilizationTypes = new bool[3](); r.m_pbOtherCivilizationTypes[1] = true;
    r.m_pbOtherNotCivilizationTypes = new bool[3](); r.m_pbOtherNotCivilizationTypes[2] = true;
    r.m_pbOtherLeaderHeadTypes = new bool[4](); r.m_pbOtherLeaderHeadTypes[3] = true;
    r.m_pbOtherNotLeaderHeadTypes = new bool[4](); r.m_pbOtherNotLeaderHeadTypes[0] = true;
}
void writeOld(CvDiplomacyTextInfo::Response& r, FDataStreamBase& s) {
    s.Write(uint(0)); s.Write(1); s.Write(r.m_iNumDiplomacyText);
    s.Write(3, r.m_pbCivilizationTypes); s.Write(4, r.m_pbLeaderHeadTypes);
    s.Write(2, r.m_pbAttitudeTypes); s.Write(2, r.m_pbDiplomacyPowerTypes); s.WriteString(1, r.m_paszDiplomacyText);
}
int main() {
    TestResponse empty;
    assert(!empty.getOtherCivilizationTypes(0) && !empty.getOtherLeaderHeadTypes(3));
    assert(!empty.getOtherCivilizationTypes(-1) && !empty.getOtherLeaderHeadTypes(4));
    TestInfo info; TestResponse* response = new TestResponse; response->seed(); response->allow(); info.add(response);
    assert(info.getOtherCivilizationTypes(0, 1) && !info.getOtherCivilizationTypes(0, 0));
    assert(info.getOtherNotCivilizationTypes(0, 2) && info.getOtherLeaderHeadTypes(0, 3));
    assert(info.getOtherNotLeaderHeadTypes(0, 0));
    assert(!info.getOtherLeaderHeadTypes(-1, 0) && !info.getOtherLeaderHeadTypes(1, 0));
    FDataStreamBase stream; response->write(&stream);
    TestResponse restored; restored.read(&stream); assert(stream.pos == stream.bytes.size());
    assert(restored.getOtherCivilizationTypes(1) && restored.getOtherNotCivilizationTypes(2));
    assert(restored.getOtherLeaderHeadTypes(3) && restored.getOtherNotLeaderHeadTypes(0));
    FDataStreamBase old; response->writeOld(old); restored.read(&old);
    assert(old.pos == old.bytes.size() && !restored.getOtherCivilizationTypes(1) && !restored.getOtherLeaderHeadTypes(3));
    empty.seed(); FDataStreamBase absent; empty.write(&absent); restored.read(&absent);
    assert(absent.pos == absent.bytes.size() && !restored.getOtherLeaderHeadTypes(3));
    CvDiplomacyTextInfo legacy; legacy.init(1);
    assert(!legacy.getOtherLeaderHeadTypes(0, 3) && !legacy.getOtherNotCivilizationTypes(0, 2));
    assert(!legacy.getOtherLeaderHeadTypes(-1, 0) && !legacy.getOtherLeaderHeadTypes(0, 4));
    CvDiplomacyTextInfo::Response& lr = const_cast<CvDiplomacyTextInfo::Response&>(legacy.getResponse(0));
    seedOriginal(lr); allow(lr);
    assert(legacy.getOtherLeaderHeadTypes(0, 3) && legacy.getOtherNotLeaderHeadTypes(0, 0));
    FDataStreamBase ls; legacy.write(&ls);
    CvDiplomacyTextInfo copy; copy.read(&ls); assert(ls.pos == ls.bytes.size());
    assert(copy.getOtherCivilizationTypes(0, 1) && copy.getOtherNotCivilizationTypes(0, 2));
    assert(copy.getOtherLeaderHeadTypes(0, 3) && copy.getOtherNotLeaderHeadTypes(0, 0));
    FDataStreamBase lo; writeOld(lr, lo); copy.read(&lo);
    assert(lo.pos == lo.bytes.size() && !copy.getOtherLeaderHeadTypes(0, 3));
    CvDiplomacyTextInfo nullLists; nullLists.init(1);
    seedOriginal(const_cast<CvDiplomacyTextInfo::Response&>(nullLists.getResponse(0)));
    FDataStreamBase ln; nullLists.write(&ln); copy.read(&ln);
    assert(ln.pos == ln.bytes.size() && !copy.getOtherCivilizationTypes(0, 1));
}
'''
with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    (temp / 'PartnerDiplomacyCache.h').write_text((dll / 'PartnerDiplomacyCache.h').read_text())
    cpp, binary = temp / 'partner.cpp', temp / 'partner'
    declarations = '\n'.join([declaration(ch, 'CvDiplomacyResponse'), declaration(ch, 'CvDiplomacyInfo'), declaration(mh, 'CvDiplomacyTextInfo')])
    cpp.write_text(stub + '\n' + declarations + '\n' + '\n'.join(definitions) + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('Actual partner getters/storage/cache methods: C++03 + ASan/UBSan passed (simulated stream)')
