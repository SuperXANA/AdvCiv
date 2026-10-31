#!/usr/bin/env python3
"""Actual base/hybrid declarations, constructors and readers; XML/base interfaces stubbed."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
directory = Path(os.environ.get('ORGANIZATION_SOURCE_DIR', str(root / 'CvGameCoreDLL')))
header = (directory / 'CvInfo_Organization.h').read_text()
source = (directory / 'CvInfo_Organization.cpp').read_text()

def declaration(name):
    start = header.index('class ' + name + ' :')
    return header[start:header.index('\n};', start) + 4]

def method(signature):
    start = source.index(signature)
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

prefix = r'''
#include <cassert>
#include <climits>
#include <cstddef>
#include <cstring>
#include <new>
#include <string>
#include <vector>
#include <iostream>
typedef wchar_t wchar;
typedef char TCHAR;
typedef std::string CvString;
// Category IDs are aliases in this interface fixture; enum conversions are not validated.
typedef int TechTypes;
typedef int UnitClassTypes;
typedef int MissionTypes;
typedef int CivilizationTypes;
typedef int LeaderHeadTypes;
typedef int ReligionTypes;
typedef int CorporationTypes;
enum { NO_TECH=-1, NO_UNITCLASS=-1, NO_MISSION=-1, NO_CIVILIZATION=-1,
       NO_LEADER=-1, NO_RELIGION=-1, NO_CORPORATION=-1 };
class CvXMLLoadUtility;
struct CvHotkeyInfo {
    std::vector<CvString> m_aszExtraXMLforPass3;
    bool read(CvXMLLoadUtility*);
};
'''
xml = r'''
char const* const tags[] = { "iSpreadFactor", "bMinorOrganization", "TriggerReligion",
    "TriggerCorporation", "iMinUnhappinessRequired", "iBaseSpreadChancePercentage",
    "iWithdrawalUnhappinessTurns", "PrereqCivilization", "PrereqLeader" };
class CvXMLLoadUtility {
public:
    int mask, value, calls;
    bool baseOK;
    CvXMLLoadUtility(int m, int v, bool b) : mask(m), value(v), calls(0), baseOK(b) {}
    bool present(char const* tag) const {
        for (int i=0; i<9; ++i) if (tag == std::string(tags[i])) return (mask & (1<<i)) != 0;
        return false;
    }
    void SetInfoIDFromChildXmlVal(int& out, char const* tag) {
        ++calls; out=present(tag) ? value : -1;
    }
    void GetChildXmlValByName(int* out, char const* tag) {
        ++calls; *out=present(tag) ? value : 0;
    }
    void GetChildXmlValByName(bool* out, char const* tag) {
        ++calls; *out=present(tag) ? (value != 0) : false;
    }
    void GetChildXmlValByName(CvString& out, char const* tag) {
        ++calls; out=present(tag) ? tag : "";
    }
    void GetChildXmlValByName(std::wstring& out, char const*) { ++calls; out=L""; }
    void* GetXML() { return NULL; }
    void InitList(int** out, int count) { *out=new int[count]; for(int i=0;i<count;++i)(*out)[i]=0; }
    void SetCommerceArray(int** out) { InitList(out,3); }
};
bool CvHotkeyInfo::read(CvXMLLoadUtility* p) { return p->baseOK; }
struct XmlIface { bool SetToChildByTagName(void*,char const*) { return false; } };
struct DLL { XmlIface iface; XmlIface* getXMLIFace() { return &iface; } } dll;
DLL* gDLL=&dll;
enum { NUM_COMMERCE_TYPES=3 };
// Reduced shell for the additional complete religion read body; constructor/arrays are stand-ins.
class CvReligionInfo : public CvOrganizationInfo {
public:
    int m_iNumFreeUnits;
    int *m_paiGlobalReligionCommerce, *m_paiHolyCityCommerce, *m_paiStateReligionCommerce;
    CvString m_szTechButton, m_szGenericTechButton;
    std::wstring m_szAdjectiveKey;
    CvReligionInfo() : m_iNumFreeUnits(0), m_paiGlobalReligionCommerce(NULL),
        m_paiHolyCityCommerce(NULL), m_paiStateReligionCommerce(NULL) {}
    ~CvReligionInfo() { delete[]m_paiGlobalReligionCommerce; delete[]m_paiHolyCityCommerce; delete[]m_paiStateReligionCommerce; }
    bool read(CvXMLLoadUtility*);
};
'''
checks = r'''
void defaults(CvHybridOrganizationInfo const& info) {
    assert(!info.isMinorOrganization());
    assert(info.getChar()==0 && info.getTechPrereq()==NO_TECH);
    assert(info.getFreeUnitClass()==NO_UNITCLASS && info.getMissionType()==NO_MISSION);
    assert(info.getSpreadFactor()==0);
    assert(info.getPrereqCivilization()==NO_CIVILIZATION && info.getPrereqLeader()==NO_LEADER);
    assert(info.getTriggerReligion()==NO_RELIGION && info.getTriggerCorporation()==NO_CORPORATION);
    assert(info.getMinUnhappinessRequired()==0);
    assert(info.getBaseSpreadChancePercentage()==0 && info.getWithdrawalUnhappinessTurns()==0);
    assert(info.m_aszExtraXMLforPass3.empty());
}
int main() {
    int const values[] = {-5,0,17,100,INT_MAX};
    int const patterns[] = {0,0x7f,0xff};
    int cases=0;
    for (int pattern=0; pattern<3; ++pattern)
    for (int mask=0; mask<512; ++mask)
    for (int v=0; v<5; ++v)
    for (int baseOK=0; baseOK<2; ++baseOK) {
        union Storage { long double alignment; char bytes[sizeof(CvHybridOrganizationInfo)]; } storage;
        std::memset(storage.bytes,patterns[pattern],sizeof(storage.bytes));
        CvHybridOrganizationInfo* info=new (storage.bytes) CvHybridOrganizationInfo;
        defaults(*info);
        CvXMLLoadUtility xml(mask,values[v],baseOK != 0);
        bool success=info->read(&xml);
        assert(success == (baseOK != 0));
        if (!baseOK) {
            defaults(*info); assert(xml.calls==0);
        } else {
            assert(info->isMinorOrganization() == ((mask & 2) && values[v] != 0));
            assert(info->getSpreadFactor() == ((mask & 1) ? values[v] : 0));
            assert(info->getTriggerReligion() == ((mask & 4) ? values[v] : -1));
            assert(info->getTriggerCorporation() == ((mask & 8) ? values[v] : -1));
            assert(info->getMinUnhappinessRequired() == ((mask & 16) ? values[v] : 0));
            assert(info->getBaseSpreadChancePercentage() == ((mask & 32) ? values[v] : 0));
            assert(info->getWithdrawalUnhappinessTurns() == ((mask & 64) ? values[v] : 0));
            // Existing base staging/order and unresolved prereq fields are preserved.
            assert(info->m_aszExtraXMLforPass3.size()==2);
            assert(info->m_aszExtraXMLforPass3[0] == ((mask & 128) ? "PrereqCivilization" : ""));
            assert(info->m_aszExtraXMLforPass3[1] == ((mask & 256) ? "PrereqLeader" : ""));
            assert(info->getPrereqCivilization()==NO_CIVILIZATION && info->getPrereqLeader()==NO_LEADER);
            assert(xml.calls==14);
        }
        info->~CvHybridOrganizationInfo();
        ++cases;
    }
    assert(cases==15360);
    for(int baseOK=0;baseOK<2;++baseOK) {
        CvReligionInfo religion;
        CvXMLLoadUtility xml(0,0,baseOK!=0);
        assert(religion.read(&xml)==(baseOK!=0));
        assert(religion.m_aszExtraXMLforPass3.size()==(baseOK ? 3U : 0U));
        if(baseOK) {
            assert(religion.m_aszExtraXMLforPass3[2].empty());
            assert(religion.m_paiGlobalReligionCommerce && religion.m_paiHolyCityCommerce && religion.m_paiStateReligionCommerce);
        } else assert(xml.calls==0);
    }
    std::cout << cases << " base/hybrid constructor and read configurations passed\n";
    std::cout << "2 religion read success/failure cases passed (reduced shell)\n";
}
'''
methods = [method(signature) for signature in [
    'CvOrganizationInfo::CvOrganizationInfo(', 'wchar CvOrganizationInfo::getChar(', 'bool CvOrganizationInfo::read(',
    'CvHybridOrganizationInfo::CvHybridOrganizationInfo(', 'CvHybridOrganizationInfo::~CvHybridOrganizationInfo(',
    'bool CvHybridOrganizationInfo::read(', 'bool CvReligionInfo::read(']]
code = prefix + declaration('CvOrganizationInfo') + declaration('CvHybridOrganizationInfo') + xml + '\n'.join(methods) + checks
with tempfile.TemporaryDirectory() as directory_name:
    p=Path(directory_name)
    (p/'check.cpp').write_text(code)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,
                   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
