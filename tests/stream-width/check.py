#!/usr/bin/env python3
"""Compile the actual wrapper with overload-sensitive stream and Civ type stand-ins."""
import os,pathlib,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[2]
header=(root/'CvGameCoreDLL/FDataStreamExtended.h').read_text()
base=r'''
#pragma once
#include <cassert>
#include <string>
#include <vector>
#include <cstring>
#include <cwchar>
#include <cstdio>
typedef wchar_t wchar;
#ifdef TEST_WIDE_TCHAR
typedef wchar_t TCHAR;
#else
typedef char TCHAR;
#endif
extern int fixtureAssertions;
#define FAssert(c) do { if(!(c)) ++fixtureAssertions; } while(false)
class FDataStreamBase {
public:
 enum Kind { INTEGER, BOOLEAN, NARROW, WIDE };
 struct Record { Kind kind; int i; std::string s; std::wstring w; explicit Record(Kind k):kind(k),i(0){} };
 std::vector<Record> records; unsigned int cursor;
 FDataStreamBase():cursor(0){}
 void Write(int v){Record r(INTEGER);r.i=v;records.push_back(r);}
 void Write(bool v){Record r(BOOLEAN);r.i=v?1:0;records.push_back(r);}
 void WriteString(char const* v){Record r(NARROW);r.s=v;records.push_back(r);}
 void WriteString(wchar const* v){Record r(WIDE);r.w=v;records.push_back(r);}
 void WriteString(std::string const& v){WriteString(v.c_str());}
 void WriteString(std::wstring const& v){WriteString(v.c_str());}
 Record const& take(Kind k){assert(cursor<records.size());Record const& r=records[cursor++];assert(r.kind==k);return r;}
 void Read(int* v){*v=take(INTEGER).i;}
 void Read(bool* v){*v=take(BOOLEAN).i!=0;}
 void ReadString(char* v){std::strcpy(v,take(NARROW).s.c_str());}
 void ReadString(wchar* v){std::wcscpy(v,take(WIDE).w.c_str());}
 void ReadString(std::string& v){v=take(NARROW).s;}
 void ReadString(std::wstring& v){v=take(WIDE).w;}
};
'''
main=r'''
#include "FDataStreamExtended.h"
int fixtureAssertions=0;
int main(){
 int cases=0;
 for(int n=0;n<=64;++n){
  std::string text(n,'a');std::wstring wide(n,L'z');
  FDataStreamBase raw;CvDataStream stream(&raw);
  stream.Write(text.c_str());stream.Write(wide.c_str());stream.Write(100+n);stream.Write(n%2==0);
  assert(raw.records.size()==4 && raw.records[0].kind==FDataStreamBase::NARROW && raw.records[1].kind==FDataStreamBase::WIDE);
  char small[128];wchar large[128];int tail=0;bool flag=false;
  stream.Read(small);stream.Read(large);stream.Read(&tail);stream.Read(&flag);
  assert(text==small && wide==large && tail==100+n && flag==(n%2==0));assert(raw.cursor==raw.records.size());++cases;
  FDataStreamBase owned;CvDataStream owner(&owned);
  owner.WriteString(text);owner.WriteString(wide);owner.Write(-100-n);
  std::string a;std::wstring b;tail=0;owner.ReadString(a);owner.ReadString(b);owner.Read(&tail);
  assert(a==text && b==wide && tail==-100-n && owned.cursor==owned.records.size());++cases;
 }
 {
  FDataStreamBase raw;CvDataStream stream(&raw);char a[]="mutable";wchar b[]=L"buffer";
  stream.Write(a);stream.Write(b);a[0]='X';b[0]=L'X';std::string n;std::wstring w;
  stream.ReadString(n);stream.ReadString(w);assert(n=="mutable" && w==L"buffer");++cases;
 }
 {
  FDataStreamBase raw;CvDataStream stream(&raw);
  TestEnum input=static_cast<TestEnum>(-1);stream.WriteEnum(input);stream.WriteEnum(static_cast<TestEnum>(5));stream.Write(17);
  TestEnum a=static_cast<TestEnum>(0),b=static_cast<TestEnum>(0);int tail=0;
  stream.ReadEnum(a);stream.ReadEnum(b);stream.Read(&tail);assert(static_cast<int>(a)==-1 && static_cast<int>(b)==5 && tail==17);++cases;
 }
 {
  CvDataStream absent(NULL);char n[]="held";wchar w[]=L"held";int i=77;bool b=true;TestEnum e=static_cast<TestEnum>(5);std::string s="kept";std::wstring t=L"kept";
  absent.Write(n);absent.Write(w);absent.Write(5);absent.Write(false);absent.WriteString(s);absent.WriteString(t);absent.WriteEnum(e);
  absent.Read(n);absent.Read(w);absent.Read(&i);absent.Read(&b);absent.ReadEnum(e);absent.ReadString(s);absent.ReadString(t);
  assert(std::string(n)=="held" && std::wstring(w)==L"held" && i==77 && b && static_cast<int>(e)==5 && s=="kept" && t==L"kept" && fixtureAssertions==1);++cases;
 }
 std::printf("%d raw/owning/enum/null-stream cases passed\n",cases);
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=pathlib.Path(tmp)
 (p/'FDataStreamExtended.h').write_text(header)
 (p/'FDataStreamBase.h').write_text(base)
 (p/'EnumTraits.h').write_text('enum TestEnum { TEST_NONE=-1, TEST_VALUE=0, TEST_POSITIVE=5 }; template<class T> struct enum_traits { enum { is_enum=0 }; }; template<> struct enum_traits<TestEnum> { enum { is_enum=1 }; };\n')
 (p/'BoostPythonPCH.h').write_text('#define BOOST_STATIC_ASSERT(c) ((void)sizeof(char[(c)?1:-1]))\n')
 (p/'main.cpp').write_text(main)
 for wide in (False,True):
  binary=p/('wide' if wide else 'narrow')
  cmd=['g++','-std=c++03','-fno-exceptions','-pedantic','-Wall','-Wextra','-Werror','-I',str(p),str(p/'main.cpp'),'-o',str(binary)]
  if os.environ.get('STREAM_WIDTH_SANITIZE'):cmd[1:1]=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  if wide:cmd.insert(1,'-DTEST_WIDE_TCHAR')
  subprocess.run(cmd,check=True);subprocess.run([str(binary)],check=True)
print('Both widths dispatch to string codecs in both TCHAR configurations.')
