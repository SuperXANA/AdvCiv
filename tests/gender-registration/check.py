from pathlib import Path
import tempfile
import subprocess
import os

root = Path(__file__).resolve().parents[2]
header = (root / 'CvGameCoreDLL/CvEnumMacros.h').read_text()
code = r'''
#include <vector>
#include <cassert>
#include "CvEnumMacros.h"
enum GenderTypes { NO_GENDER = -1 };
#define DECLARE_CLASS(Name, Dummy) class Cv##Name##Info;
DO_FOR_EACH_INFO_TYPE(DECLARE_CLASS)
class CvInfoBase {
public:
 static int alive;
 CvInfoBase() { ++alive; }
 virtual ~CvInfoBase() { --alive; }
};
int CvInfoBase::alive = 0;
#define FAssertBounds(lo, hi, value) assert((value) >= (lo) && (value) < (hi))
struct Globals {
#define DECLARE_VECTOR(Name, Dummy) std::vector<Cv##Name##Info*> m_pa##Name##Info;
 DO_FOR_EACH_INFO_TYPE(DECLARE_VECTOR)
 MAKE_INFO_ACCESSORS_DYN(Gender, GENDER)
} GC;
template<class T> void LoadGlobalClassInfo(std::vector<T*>& infos,
 const char*, const char*, const char*, bool) {
 infos.push_back(new T());
 infos.push_back(new T());
}
int main() {
 LoadGlobalClassInfo(GC.m_paGenderInfo, "CIV4GenderInfos", "BasicInfos",
  "Civ4GenderInfos/GenderInfos/GenderInfo", false);
 assert(GC.getNumGenderInfos()==2 && CvInfoBase::alive==2);
 for(int i=0;i<2;++i) {
  CvInfoBase& info=GC.getGenderInfo(i);
  assert(&info==GC.m_paGenderInfo[i]);
  assert(&GC.getInfo(static_cast<GenderTypes>(i))==&info);
  delete &info;
 }
 GC.m_paGenderInfo.clear();
 assert(CvInfoBase::alive==0);
}
'''
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp)
    (p / 'CvEnumMacros.h').write_text(header)
    (p / 'check.cpp').write_text(code)
    for sanitized in (False, True):
        exe = p / ('sanitized' if sanitized else 'normal')
        cmd = ['g++', '-std=c++03', '-fno-exceptions', '-Wall', '-Wextra', '-Werror', '-pedantic', '-I'+str(p), str(p/'check.cpp'), '-o', str(exe)]
        if sanitized:
            cmd += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(cmd, check=True)
        subprocess.run([str(exe)], check=True, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
        print(('ASan/UBSan' if sanitized else 'normal') + ': gender registration lifecycle passed')
    marker = '// XANA: 11-01-2026 Gender basic-info class alias (ChatGPT)'
    before, addition, after = header.split(marker)
    assert '#define CvGenderInfo CvInfoBase' in addition
    (p / 'CvEnumMacros.h').write_text(before + after.lstrip('\n'))
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0 and 'incomplete type' in result.stderr
    print('Original header: incomplete-type compile failure reproduced')
