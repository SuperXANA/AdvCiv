#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,os
root=Path(__file__).resolve().parents[2]
h=(root/'CvGameCoreDLL/CvInfo_Civilization.h').read_text()
a=h.index('class CvCivilizationInfo :');b=h.index('\n};',a)+3;declaration=h[a:b]
s=(root/'CvGameCoreDLL/CvInfo_Civilization.cpp').read_text()
def method(signature):
 a=s.index(signature);b=s.index('{',a)+1;depth=1
 while depth:
  depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]
stub=r'''
#include <string>
#include <vector>
#include <cassert>
#include <cstddef>
typedef unsigned int uint;
typedef wchar_t wchar;
typedef char TCHAR;
typedef std::string CvString;
typedef std::wstring CvWString;
typedef int ArtStyleTypes;
typedef int BuildingTypes;
typedef int UnitTypes;
typedef int RaceTypes;
const int NO_PLAYERCOLOR=-1,NO_ARTSTYLE=-1,NO_UNIT_ARTSTYLE=-1,NO_CIVILIZATION=-1;
struct CvInfoBase{};
class CvXMLLoadUtility;class FDataStreamBase;class CvArtInfoCivilization;
#define DllExport
#define ENABLE_XML_FILE_CACHE 0
int deletions=0;
template<class T> void release(T*&p){if(p){++deletions;delete[]p;p=NULL;}}
#define SAFE_DELETE_ARRAY(p) release(p)
struct Globals{int getNumRaceInfos()const{return 3;}}GC;
'''
code=stub+declaration+'\n'+'\n'.join(method(sig) for sig in ['CvCivilizationInfo::CvCivilizationInfo()', 'CvCivilizationInfo::~CvCivilizationInfo()', 'int CvCivilizationInfo::getRacePriority('])
code+=r'''
struct Fixture: CvCivilizationInfo {
 void install(){assert(m_piRacePriorities==NULL);m_piRacePriorities=new int[3];m_piRacePriorities[0]=5;m_piRacePriorities[1]=0;m_piRacePriorities[2]=-2;}
};
int main(){
 {Fixture f;assert(f.getRacePriority(0)==0&&f.getRacePriority(-1)==0&&f.getRacePriority(3)==0);}
 assert(deletions==0);
 {Fixture f;f.install();assert(f.getRacePriority(0)==5&&f.getRacePriority(1)==0&&f.getRacePriority(2)==-2);assert(f.getRacePriority(-1)==0&&f.getRacePriority(3)==0&&f.getRacePriority(999)==0);}
 assert(deletions==1);
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-Wno-reorder','-pedantic','-fsanitize=address,undefined',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual civilization class, constructor/destructor/accessor; empty/owned arrays, value and index boundaries. C++03/ASan/UBSan; metadata/cache/engine stubbed.')
