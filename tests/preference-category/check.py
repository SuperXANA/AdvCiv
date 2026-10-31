#!/usr/bin/env python3
"""Actual preference record declarations/readers, with category-aware GC/XML stubs."""
from pathlib import Path
import os
import re
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
header=(root/'CvGameCoreDLL/CvXMLStructs.h').read_text().replace('#pragma once','')
source=(root/'CvGameCoreDLL/CvXMLStructs.cpp').read_text()
source=re.sub(r'^#include[^\n]*\n','',source,flags=re.M)
prefix=r'''
#include <cassert>
#include <climits>
#include <cstring>
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <iostream>
static int assertions=0;
#define FAssertMsg(x,m) do{if(!(x))++assertions;}while(0)
typedef std::string CvString;
enum TechTypes{NO_TECH=-1};enum EventTypes{NO_EVENT=-1};
enum UnitCombatTypes{NO_UNITCOMBAT=-1};enum UnitClassTypes{NO_UNITCLASS=-1};enum UnitTypes{NO_UNIT=-1};
template<class E>struct Category;
template<>struct Category<TechTypes>{enum{value=0};};
template<>struct Category<EventTypes>{enum{value=1};};
template<>struct Category<UnitCombatTypes>{enum{value=2};};
template<>struct Category<UnitClassTypes>{enum{value=3};};
template<>struct Category<UnitTypes>{enum{value=4};};
struct Info {
    std::string type;bool nullType;
    explicit Info(std::string const& s=""):type(s),nullType(false){}
    char const* getType()const{return nullType?NULL:type.c_str();}
};
char const* const prefixes[]={"TECH_","EVENT_","UNITCOMBAT_","UNITCLASS_","UNIT_"};
std::string key(int c,int n){std::ostringstream out;out<<prefixes[c]<<n;return out.str();}
struct Globals {
    std::vector<Info> tables[5];std::map<std::string,int> registry;int lookups;
    void setup(int rotation){registry.clear();lookups=0;
        for(int c=0;c<5;++c){tables[c].clear();for(int n=0;n<(c+rotation)%6;++n){tables[c].push_back(Info(key(c,n)));registry[key(c,n)]=n;}}
    }
    int getInfoTypeForString(char const* s)const{std::map<std::string,int>::const_iterator i=registry.find(s);return i==registry.end()?-1:i->second;}
    template<class E> Info const& getInfo(E id){int c=Category<E>::value;assert(id>=0&&static_cast<size_t>(id)<tables[c].size());++lookups;return tables[c][id];}
    int getNumTechInfos()const{return tables[0].size();}int getNumEventInfos()const{return tables[1].size();}
    int getNumUnitCombatInfos()const{return tables[2].size();}int getNumUnitClassInfos()const{return tables[3].size();}
    int getNumUnitInfos()const{return tables[4].size();}
}GC;
struct CvXMLLoadUtility {
    std::string type;bool present;int scalarReads;void* cursor;
    CvXMLLoadUtility():present(true),scalarReads(0),cursor(this){}
    bool GetChildXmlValByName(CvString& out,char const*){out=present?type:"";return present;}
    void GetChildXmlValByName(int* out,char const*){++scalarReads;*out=37;}
    void GetChildXmlValByName(bool* out,char const* tag){++scalarReads;*out=std::strcmp(tag,"bPreferredChoice")==0;}
    void SetInfoIDFromChildXmlVal(int& out,char const*){out=present?GC.getInfoTypeForString(type.c_str()):-1;}
};
'''
suffix=r'''
int id(TechPreferenceData const& r){return r.getTechType();}int id(EventPreferenceData const& r){return r.getEventType();}
int id(UnitCombatPreferenceData const& r){return r.getUnitCombatType();}int id(UnitClassPreferenceData const& r){return r.getUnitClassType();}
int id(UnitPreferenceData const& r){return r.getUnitType();}
int percent(TechPreferenceData const& r){return r.getTechValueModifierPercent();}int percent(EventPreferenceData const& r){return r.getEventValueModifierPercent();}
int percent(UnitCombatPreferenceData const& r){return r.getUnitValueModifierPercent();}int percent(UnitClassPreferenceData const& r){return r.getUnitValueModifierPercent();}
int percent(UnitPreferenceData const& r){return r.getUnitValueModifierPercent();}
template<class R> int check(int category){int cases=0;
    for(int rotation=0;rotation<6;++rotation){GC.setup(rotation);
        for(int foreign=0;foreign<5;++foreign)for(int n=0;n<6;++n){
            CvXMLLoadUtility xml;xml.type=key(foreign,n);R row;void* cursor=xml.cursor;
            bool expected=foreign==category&&n<static_cast<int>(GC.tables[category].size());
            bool ok=row.read(&xml);assert(ok==expected);assert(xml.cursor==cursor);
            assert(id(row)==(expected?n:-1));assert(xml.scalarReads==(expected?3:0));
            if(expected){assert(percent(row)==37&&row.isPreferredChoice()&&!row.isNotPreferredChoice());
                // Reuse a populated record; failed reads must invalidate the old key.
                xml.type="NONE";assert(!row.read(&xml)&&id(row)==-1);
            }
            ++cases;
        }
        char const* const invalid[]={"NONE","","UNKNOWN","tech_0","BAD_LOW","BAD_NEGATIVE","BAD_HIGH","BAD_MAX"};
        GC.registry["BAD_LOW"]=INT_MIN;GC.registry["BAD_NEGATIVE"]=-2;
        GC.registry["BAD_HIGH"]=static_cast<int>(GC.tables[category].size());GC.registry["BAD_MAX"]=INT_MAX;
        for(int n=0;n<8;++n){CvXMLLoadUtility xml;xml.type=invalid[n];R row;int before=GC.lookups;
            assert(!row.read(&xml)&&id(row)==-1&&xml.scalarReads==0);
            if(n>=4)assert(GC.lookups==before);
            ++cases;
        }
        {CvXMLLoadUtility xml;xml.present=false;R row;assert(!row.read(&xml)&&id(row)==-1&&xml.scalarReads==0);++cases;}
        if(!GC.tables[category].empty()){
            GC.tables[category][0].nullType=true;CvXMLLoadUtility xml;xml.type=key(category,0);R row;
            assert(!row.read(&xml)&&id(row)==-1&&xml.scalarReads==0);GC.tables[category][0].nullType=false;++cases;
        }
    }
    return cases;
}
template<class R> void collisionOnly(int category){int count=0;
    for(int rotation=0;rotation<6;++rotation){GC.setup(rotation);
        for(int foreign=0;foreign<5;++foreign)if(foreign!=category)
        for(int n=0;n<static_cast<int>(GC.tables[foreign].size())&&n<static_cast<int>(GC.tables[category].size());++n){
            CvXMLLoadUtility xml;xml.type=key(foreign,n);R row;
            assert(!row.read(&xml)&&id(row)==-1);++count;
        }
    }
    assert(count>0);
}
int main(){int cases=check<TechPreferenceData>(0)+check<EventPreferenceData>(1)+check<UnitCombatPreferenceData>(2)+check<UnitClassPreferenceData>(3)+check<UnitPreferenceData>(4);
    assert(assertions>0);std::cout<<cases<<" preference-category record cases passed\n";
}
'''
specs=[('TechTypes','iTech','TechType','Tech'),('EventTypes','iEvent','Event','Event'),
       ('UnitCombatTypes','iUnitCombat','UnitCombatType','UnitCombat'),('UnitClassTypes','iUnitClass','UnitClassType','UnitClass'),('UnitTypes','iUnit','UnitType','Unit')]
variants=[('positive',source,None)]
records=['TechPreferenceData','EventPreferenceData','UnitCombatPreferenceData','UnitClassPreferenceData','UnitPreferenceData']
for index,(enum,field,tag,category) in enumerate(specs):
    guard='if (!readPreferenceInfoID<%s>(pXML, %s, "%s", GC.getNum%sInfos()))\n\t\treturn false;'%(enum,field,tag,category)
    old='pXML->SetInfoIDFromChildXmlVal(%s, "%s");'%(field,tag)
    assert guard in source
    variants.append((category+'-untyped-key',source.replace(guard,old),index))
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory)
    for name,body,index in variants:
        ending=suffix if index is None else suffix[:suffix.rindex('int main(){')]+'int main(){collisionOnly<%s>(%d);}\n'%(records[index],index)
        (p/'check.cpp').write_text(prefix+header+'\n'+body+'\n'+ending)
        subprocess.run(['g++','-std=c++03','-fno-exceptions','-Wall','-Wextra','-Werror','-pedantic',
                        '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
        r=subprocess.run([str(p/'check')],capture_output=True,text=True,
                         env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
        if name=='positive':
            assert r.returncode==0,r.stderr
            print(r.stdout.strip())
        else:
            assert body!=source and r.returncode!=0,name
            print('Negative control detected: '+name)
