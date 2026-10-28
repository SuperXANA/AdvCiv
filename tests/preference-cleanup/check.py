from pathlib import Path
import os,re,subprocess,tempfile
root=Path(__file__).resolve().parents[2]
directory=Path(os.environ.get('PREFERENCE_SOURCE_DIR',str(root/'CvGameCoreDLL')))
classes=[];methods=[]
for file,kind in [('CvInfo_Civilization','Tech'),('CvInfo_RandomEvent','Event'),('CvInfo_Unit','Unit')]:
 name='Cv'+kind+'PreferenceInfo'
 h=(directory/(file+'.h')).read_text();s=(directory/(file+'.cpp')).read_text()
 a=h.index('class '+name+' :');classes.append(h[a:h.index('\n};',a)+4])
 for member in [name,'~'+name]:
  a=s.index(name+'::'+member+'(');b=s.index('{',a);depth=1;i=b+1
  while depth:
   depth+=(s[i]=='{')-(s[i]=='}');i+=1
  methods.append(s[a:i])
prefix=r'''
#include <cassert>
#include <cstddef>
#include <vector>
enum {NO_LEADER=-1,NO_CIVILIZATION=-1};
struct CvInfoBase {};
struct TechPreferenceData{};struct EventPreferenceData{};
struct UnitCombatPreferenceData{};struct UnitClassPreferenceData{};struct UnitPreferenceData{};
class CvXMLLoadUtility;
int deletedArrays=0;
#define SAFE_DELETE_ARRAY(p) do{if(p){delete[]p;p=NULL;++deletedArrays;}}while(0)
'''
suffix=r'''
class CvXMLLoadUtility {
public:
 static void populate(CvTechPreferenceInfo& x){assert(x.m_aiVectorIndexMap==NULL);x.m_aiVectorIndexMap=new int[3];}
 static void populate(CvEventPreferenceInfo& x){assert(x.m_aiVectorIndexMap==NULL);x.m_aiVectorIndexMap=new int[4];}
 static void populate(CvUnitPreferenceInfo& x){
  assert(x.m_aiVectorIndexMapForUnitCombats==NULL);
  assert(x.m_aiVectorIndexMapForUnitClasses==NULL);
  assert(x.m_aiVectorIndexMapForUnits==NULL);
  x.m_aiVectorIndexMapForUnitCombats=new int[2];
  x.m_aiVectorIndexMapForUnitClasses=new int[3];
  x.m_aiVectorIndexMapForUnits=new int[4];
 }
};
int main(){
 {CvTechPreferenceInfo a;CvEventPreferenceInfo b;CvUnitPreferenceInfo c;}
 assert(deletedArrays==0);
 for(int i=0;i<100;++i){
  {CvTechPreferenceInfo a;CvEventPreferenceInfo b;CvUnitPreferenceInfo c;
   CvXMLLoadUtility::populate(a);CvXMLLoadUtility::populate(b);CvXMLLoadUtility::populate(c);}
  assert(deletedArrays==5*(i+1));
 }
}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'check.cpp').write_text(prefix+'\n'.join(classes+methods)+suffix)
 subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
  '-fsanitize=address,undefined',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
 subprocess.run([str(p/'check')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: actual three class declarations/constructors/destructors; 500 array deletions; C++03/ASan/UBSan')
