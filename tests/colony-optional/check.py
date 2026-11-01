from pathlib import Path
import subprocess, tempfile, os
root=Path(__file__).resolve().parents[2]
fixed=(root/'CvGameCoreDLL/CvInfo_Civilization.cpp').read_text()
old='bool CvLeaderHeadInfo::readPass2(CvXMLLoadUtility* pXML)\n{\n pXML->SetInfoIDFromChildXmlVal(m_iDerivativeLeader, \"DerivativeLeader\");\n return true;\n}'
get=(root/'CvGameCoreDLL/CvXMLLoadUtilityGet.cpp').read_text()
def method(text,signature):
    start=text.index(signature)
    end=text.index('\n}',start)+2
    return text[start:end]
reader=method(get,'bool CvXMLLoadUtility::GetChildXmlValByName(std::string&')
global_reader=method(get,'void CvXMLLoadUtility::SetGlobalTypeFromChildXmlVal(')
prefix=r'''
#include <cassert>
#include <cstring>
#include <iostream>
#include <string>
typedef char TCHAR;
enum {NO_LEADER=-1};
int diagnostics=0;
#define FAssertMsg(cond,msg) do {if(!(cond))++diagnostics;}while(0)
#define FErrorMsg(msg) do {++diagnostics;}while(0)
struct CvString:std::string {
 CvString(){}
 CvString(char const* s):std::string(s){}
 bool IsEmpty()const{return empty();}
 operator char const*()const{return c_str();}
};
struct FXml {bool present;std::string text;bool child;};
struct XMLInterface {
 bool SetToChildByTagName(FXml* x,char const* name){assert(std::string(name)=="DerivativeLeader");x->child=x->present;return x->present;}
 void SetToParent(FXml* x){assert(x->child);x->child=false;}
} xmlInterface;
struct DLL {XMLInterface* getXMLIFace(){return &xmlInterface;}} dll;
DLL* gDLL=&dll;
void assignDefault(std::string& r,char const* s){r=s?s:"";}
bool SafeGetLastNodeValue(FXml* x,std::string& r,char const*){assert(x->child);r=x->text;return true;}
int lookup(std::string const& s){
 if(s=="LEADER_ZERO")return 0;
 if(s=="LEADER_THREE")return 3;
 assert(s=="NONE");return -1;
}
struct CvXMLLoadUtility {
 struct Data {bool bAssertMandatory;} data;
 Data* m;FXml* m_pFXml;CvString szAssertMsg;
 CvXMLLoadUtility(FXml& xml,bool mandatory):m(&data),m_pFXml(&xml){data.bAssertMandatory=mandatory;}
 bool SkipToNextVal(){return true;}
 bool GetChildXmlValByName(std::string& r,TCHAR const* name,char const* def);
 void SetGlobalTypeFromChildXmlVal(int& r,TCHAR const* name,bool info);
 static int FindInInfoClass(TCHAR const* s){return lookup(s);}
 static int getGlobalEnumFromString(TCHAR const* s){return lookup(s);}
 template<typename T,bool is_enum=false>struct InfoIDFromChild;
 template<typename T>struct InfoIDFromChild<T,false>{
  static void set(CvXMLLoadUtility& kUtil,T& tValue,TCHAR const* szName){
   kUtil.SetGlobalTypeFromChildXmlVal(static_cast<int&>(tValue),szName,true);
  }
 };
 template<typename T>void SetInfoIDFromChildXmlVal(T& tResult,TCHAR const* szName){
  InfoIDFromChild<T>::set(*this,tResult,szName);
 }
};
struct CvLeaderHeadInfo {int m_iDerivativeLeader;bool readPass2(CvXMLLoadUtility*);};
'''
main=r'''
void apply(CvLeaderHeadInfo& info,int tag,bool mandatory){
 char const* values[]={"","","NONE","LEADER_ZERO","LEADER_THREE"};
 FXml xml;xml.present=tag!=0;xml.text=values[tag];xml.child=false;
 CvXMLLoadUtility util(xml,mandatory);
 assert(info.readPass2(&util));assert(!xml.child);
}
int expected(int old,int tag){if(tag==0 || tag==1)return old;if(tag==2)return -1;if(tag==3)return 0;return 3;}
int main(){
 int const before[]={-1,0,1,3};int cases=0;
 for(int mandatory=0;mandatory<2;++mandatory)
 for(int p=0;p<4;++p)
 for(int first=0;first<5;++first)
 for(int second=0;second<5;++second){
  diagnostics=0;CvLeaderHeadInfo info;info.m_iDerivativeLeader=before[p];
  apply(info,first,mandatory!=0);
  assert(info.m_iDerivativeLeader==expected(before[p],first));
  apply(info,second,mandatory!=0);
  assert(info.m_iDerivativeLeader==expected(expected(before[p],first),second));
  assert(diagnostics==0);++cases;
 }
 assert(cases==200);std::cout<<cases<<" optional two-pass/module sequences passed\n";
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 for negative in (False,True):
  source=prefix+reader+'\n'+global_reader+'\n'+method(old if negative else fixed,'bool CvLeaderHeadInfo::readPass2(')+main
  (p/'check.cpp').write_text(source)
  for sanitize in ([False] if negative else [False,True]):
   flags=['-fsanitize=address,undefined','-g'] if sanitize else []
   subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic']+flags+[str(p/'check.cpp'),'-o',str(p/'check')],check=True)
   r=subprocess.run([str(p/'check')],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
   if negative:
    assert r.returncode!=0 and 'diagnostics==0' in r.stderr,r.stderr
    print('Original reader reproduces optional-tag assertion at stored index zero')
   else:
    assert r.returncode==0,r.stderr
    print(('ASan/UBSan: ' if sanitize else 'C++03: ')+r.stdout.strip())
