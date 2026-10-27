"""Focused tests of actual XANA methods; requires Python 3 and g++.

Run --sanitize for ASan/UBSan. Stubs do not establish engine text rendering.
"""
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
MARK="// XANA: 05-11-2025 City Bonus Diplomacy Modifier"
def method(text,signature):
    start=text.index(signature); cursor=text.index("{",start)+1; level=1
    while level:
        level+=(text[cursor]=="{")-(text[cursor]=="}");cursor+=1
    return text[start:cursor]
def declaration(path):
    text=(ROOT/path).read_text(); start=text.index(MARK)
    return text[start:text.index(MARK,start+len(MARK))]

info=(ROOT/"CvGameCoreDLL/CvInfo_Civilization.cpp").read_text()
ai=(ROOT/"CvGameCoreDLL/CvPlayerAI.cpp").read_text()
text=(ROOT/"CvGameCoreDLL/CvGameTextMgr.cpp").read_text()
getter=method(info,"int CvLeaderHeadInfo::getCityBonusDiplomacyModifier(")
query=method(ai,"int CvPlayerAI::AI_getBonusPreferenceAttitude(")
formatting=method(text,"void CvGameTextMgr::appendToAttitudeBreakdownWithExtraDescription(")
code=r"""
#include <cassert>
#include <cwchar>
#include <string>
#include <vector>
#define FAssertBounds(a,b,c) assert((c)>=(a)&&(c)<(b))
#define SETCOLR L""
#define ENDCOLR L""
#define TEXT_COLOR(c) L"color"
#define NEWLINE L"\n"
typedef wchar_t wchar;
enum BonusTypes { NO_BONUS=-1,B0,B1,B2,STUB_BONUS_MAX=32767 };
enum PlayerTypes { P0,P1 };
enum LeaderHeadTypes { L0 };
class CvLeaderHeadInfo {
public:
    int* m_piCityBonusDiplomacyModifier;
    CvLeaderHeadInfo():m_piCityBonusDiplomacyModifier(NULL) {}
    __GETDECL__
};
struct Globals {
    CvLeaderHeadInfo info;
    int getNumBonusInfos() const { return 3; }
    const CvLeaderHeadInfo& getInfo(LeaderHeadTypes) const { return info; }
} GC;
__GETTER__
static int cityChecks=0;
class CvCity {
public:
    bool bonuses[3];
    CvCity() { for(int i=0;i<3;++i) bonuses[i]=false; }
    bool hasBonus(BonusTypes b) const { ++cityChecks; return bonuses[b]; }
};
class CvPlayer {
public:
    std::vector<CvCity> cities;
    bool hasBonus(BonusTypes) const;
};
#define FOR_EACH_CITY(p,player) \
    for(size_t cityIndex=0;cityIndex<(player).cities.size();++cityIndex) \
    for(const CvCity* p=&(player).cities[cityIndex];p!=NULL;p=NULL)
__BASE_HAS_BONUS__
CvPlayer players[2];
#define GET_PLAYER(p) players[p]
class CvPlayerAI {
public:
    LeaderHeadTypes getPersonalityType() const { return L0; }
    __QUERYDECL__
};
__QUERY__
struct CvWString {
    std::wstring value;
    CvWString() {}
    explicit CvWString(const std::wstring& v):value(v) {}
    const wchar* GetCString() const { return value.c_str(); }
    void Format(const wchar*,const wchar*,const wchar* body) { value=body; }
};
struct CvWStringBuffer {
    std::wstring value;
    void append(const wchar* x) { value+=x; }
    void append(const CvWString& x) { value+=x.value; }
};
struct DLL {
    std::string key; std::wstring description; int amount,calls;
    DLL():amount(0),calls(0) {}
    CvWString getText(const char* k,int n,const wchar* resource) {
        assert(resource!=NULL); ++calls;key=k;amount=n;description=resource;
        return CvWString(description);
    }
} dll;
DLL* gDLL=&dll;
class CvGameTextMgr {
public:
    __FORMATDECL__
};
__FORMATTING__
int main() {
    CvPlayerAI ai;
    players[P1].cities.resize(3);
    int mods[3]={0,0,0};
    // Null XML storage and explicitly configured zero values both skip scans.
    assert(ai.AI_getBonusPreferenceAttitude(P1,B0)==0 && cityChecks==0);
    GC.info.m_piCityBonusDiplomacyModifier=mods;
    for(int i=0;i<3;++i)
        assert(ai.AI_getBonusPreferenceAttitude(P1,static_cast<BonusTypes>(i))==0);
    assert(cityChecks==0);
    mods[B0]=4; mods[B1]=-3;
    players[P1].cities[2].bonuses[B0]=true;
    assert(ai.AI_getBonusPreferenceAttitude(P1,B0)==4 && cityChecks==3);
    cityChecks=0;
    // Copies or more cities do not multiply the attitude.
    players[P1].cities[0].bonuses[B0]=true;
    assert(ai.AI_getBonusPreferenceAttitude(P1,B0)==4 && cityChecks==1);
    cityChecks=0;
    assert(ai.AI_getBonusPreferenceAttitude(P1,B1)==0 && cityChecks==3);
    players[P1].cities[0].bonuses[B1]=true;
    assert(ai.AI_getBonusPreferenceAttitude(P1,B1)==-3);
    players[P0].cities.clear();
    assert(ai.AI_getBonusPreferenceAttitude(P0,B0)==0);
    CvGameTextMgr mgr; CvWStringBuffer buffer; int total=0;
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,0,4,total,
        "favored","disfavored",L"Maïs");
    assert(total==4&&dll.key=="favored"&&dll.description==L"Maïs"&&dll.amount==4);
    int calls=dll.calls;
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,1,4,total,
        "favored","disfavored",L"Maïs");
    assert(total==4&&dll.calls==calls);
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,1,-3,total,
        "favored","disfavored",L"Épices");
    assert(total==1&&dll.key=="disfavored"&&dll.description==L"Épices");
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,1,-2,total,"fallback");
    assert(total==-1&&dll.key=="fallback"&&dll.description.empty());
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,0,1,total,"favored",NULL,NULL);
    assert(total==0&&dll.description.empty());
    calls=dll.calls;
    mgr.appendToAttitudeBreakdownWithExtraDescription(buffer,0,0,total,"unused");
    assert(dll.calls==calls&&total==0);
}
"""
code=(code.replace("__GETDECL__",declaration("CvGameCoreDLL/CvInfo_Civilization.h"))
      .replace("__QUERYDECL__",declaration("CvGameCoreDLL/CvPlayerAI.h"))
      .replace("__FORMATDECL__",declaration("CvGameCoreDLL/CvGameTextMgr.h"))
      .replace("__GETTER__",getter).replace("__QUERY__",query)
      .replace("__FORMATTING__",formatting)
      .replace("__BASE_HAS_BONUS__",(ROOT/"tests/city-bonus/baseline-has-bonus.txt").read_text()))
with tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/"check.cpp";binary=Path(tmp)/"check";source.write_text(code)
    flags=(["-fsanitize=address,undefined","-fno-omit-frame-pointer"]
           if "--sanitize" in sys.argv else [])
    subprocess.run(["g++","-std=c++03","-Wall","-Wextra","-Werror","-pedantic"]
                   +flags+[str(source),"-o",str(binary)],check=True)
    env=os.environ.copy()
    if "--sanitize" in sys.argv: env["UBSAN_OPTIONS"]="halt_on_error=1"
    subprocess.run([str(binary)],check=True,env=env)

# Structural XDR checks. Civ4's Microsoft XML validator is not available here.
ns="{urn:schemas-microsoft-com:xml-data}"
schema=ET.parse(ROOT/"Assets/XML/Civilizations/CIV4CivilizationsSchema.xml").getroot()
defs={x.attrib["name"]:x for x in schema.findall(ns+"ElementType")}
assert len(defs)==len(schema.findall(ns+"ElementType")),"Duplicate XDR definition"
leader=defs["LeaderHeadInfo"]; children=leader.findall(ns+"element")
entry=next(x for x in children if x.attrib["type"]=="BonusAttitudeChanges")
assert entry.attrib["minOccurs"]=="0" and children[-1] is entry
assert [x.attrib["type"] for x in defs["BonusAttitudeChange"].findall(ns+"element")]==["BonusType","iAttitudeChange"]
assert defs["iAttitudeChange"].attrib["{urn:schemas-microsoft-com:datatypes}type"]=="int"
leaders=ET.parse(ROOT/"Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml").getroot().findall(".//{*}LeaderHeadInfo")
positions={x.attrib["type"]:i for i,x in enumerate(children)}
for leader in leaders:
    order=[positions[x.tag.split("}")[-1]] for x in leader]
    assert order==sorted(order),leader.find("{*}Type").text
    assert leader.find("{*}BonusAttitudeChanges") is None
textroot=ET.parse(ROOT/"Assets/XML/Text/CIV4GameText_XANA_CityBonusDiplomacy.xml").getroot()
texts={x.find("{*}Tag").text:x.find("{*}English").text for x in textroot}
assert set(texts)=={"TXT_KEY_MISC_ATTITUDE_FAVORED_BONUS","TXT_KEY_MISC_ATTITUDE_DISFAVORED_BONUS"}
for line in texts.values(): assert "%D1" in line and "%s2" in line
print("C++03 city-bonus query, wide-description and XML structure checks passed;",
      len(leaders),"unchanged baseline leaders checked")
