#!/usr/bin/env python3
"""Actual organization header and religion-weight methods, distinct enum interface stubs."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
organization=(root/'CvGameCoreDLL/CvInfo_Organization.h').read_text()
leader=(root/'CvGameCoreDLL/CvInfo_Civilization.h').read_text()
implementation=(root/'CvGameCoreDLL/CvInfo_Civilization.cpp').read_text()
declarations='\n'.join(line for line in leader.splitlines() if any(name in line for name in
    ['getReligionWeightModifier(', 'changeReligionWeightModifier(', 'setReligionWeightModifier(']))
def method(signature):
    a=implementation.index(signature);b=implementation.index('{',a)+1;depth=1
    while depth:
        depth+=(implementation[b]=='{')-(implementation[b]=='}');b+=1
    return implementation[a:b]
methods='\n'.join(method(s) for s in ['int CvLeaderHeadInfo::getReligionWeightModifier(',
    'void CvLeaderHeadInfo::changeReligionWeightModifier(', 'void CvLeaderHeadInfo::setReligionWeightModifier('])
prefix=r'''
#include <cassert>
#include <cstddef>
#include <string>
#include <vector>
#include <iostream>
typedef wchar_t wchar;
typedef char TCHAR;
typedef std::string CvString;
typedef std::wstring CvWString;
enum CivilizationTypes {NO_CIVILIZATION=-1,CIV0,CIV1};
enum LeaderHeadTypes {NO_LEADER=-1,LEADER0,LEADER1};
enum HybridOrganizationTypes {NO_HYBRID_ORGANIZATION=-1,HYBRID0,HYBRID1};
enum ReligionTypes {NO_RELIGION=-1,RELIGION0,RELIGION1};
enum CorporationTypes {NO_CORPORATION=-1,CORPORATION0,CORPORATION1};
enum TechTypes {NO_TECH=-1,TECH0};
enum UnitClassTypes {NO_UNITCLASS=-1,UNITCLASS0};
enum MissionTypes {NO_MISSION=-1,MISSION0};
enum BonusTypes {NO_BONUS=-1,BONUS0};
struct CvHotkeyInfo {};
class CvXMLLoadUtility;
#define FAssertBounds(a,b,i) assert((i)>=(a)&&(i)<(b))
#include "CvInfo_Organization.h"
// Constructors/destructors are stand-ins; the complete actual header/getters are tested.
CvOrganizationInfo::CvOrganizationInfo():m_iPrereqCivilization(-1),m_iPrereqLeader(-1),m_bMinorOrganization(false){}
CvReligionInfo::CvReligionInfo():m_iHybridOrganization(-1),m_paiGlobalReligionCommerce(NULL),m_paiHolyCityCommerce(NULL),m_paiStateReligionCommerce(NULL){}
CvReligionInfo::~CvReligionInfo(){}
CvCorporationInfo::CvCorporationInfo():m_iHybridOrganization(-1),m_paiHeadquarterCommerce(NULL),m_paiCommerceProduced(NULL),m_paiYieldProduced(NULL){}
CvCorporationInfo::~CvCorporationInfo(){}
struct OrganizationProbe:CvOrganizationInfo {void set(int civ,int leader){m_iPrereqCivilization=civ;m_iPrereqLeader=leader;}};
struct ReligionProbe:CvReligionInfo {void set(int id){m_iHybridOrganization=id;}};
struct CorporationProbe:CvCorporationInfo {void set(int id){m_iHybridOrganization=id;}};
struct Globals {int getNumReligionInfos()const{return 2;}} GC;
struct CvLeaderHeadInfo {
    int* m_piReligionWeightModifier;
'''
code=prefix+declarations+'\n};\n'+methods+r'''
int main(){int getterCases=0,weightCases=0;
    // Member-pointer assignments require the actual distinct return types.
    CivilizationTypes(CvOrganizationInfo::*civGetter)()const=&CvOrganizationInfo::getPrereqCivilization;
    LeaderHeadTypes(CvOrganizationInfo::*leaderGetter)()const=&CvOrganizationInfo::getPrereqLeader;
    HybridOrganizationTypes(CvReligionInfo::*religionGetter)()const=&CvReligionInfo::getHybridOrganizationType;
    HybridOrganizationTypes(CvCorporationInfo::*corporationGetter)()const=&CvCorporationInfo::getHybridOrganizationType;
    for(int civ=-1;civ<=1;++civ)for(int leader=-1;leader<=1;++leader){
        OrganizationProbe p;p.set(civ,leader);
        assert(static_cast<int>((p.*civGetter)())==civ);
        assert(static_cast<int>((p.*leaderGetter)())==leader);++getterCases;
    }
    for(int id=-1;id<=1;++id){ReligionProbe r;CorporationProbe c;r.set(id);c.set(id);
        assert(static_cast<int>((r.*religionGetter)())==id);
        assert(static_cast<int>((c.*corporationGetter)())==id);getterCases+=2;
    }
    int const initial[]={-50,0,50},changes[]={-2,0,2};
    for(int id=0;id<2;++id)for(int v=0;v<3;++v)for(int d=0;d<3;++d){
        int values[2]={11,13};CvLeaderHeadInfo leader;leader.m_piReligionWeightModifier=values;
        ReligionTypes eReligion=static_cast<ReligionTypes>(id);
        leader.setReligionWeightModifier(eReligion,initial[v]);
        assert(leader.getReligionWeightModifier(eReligion)==initial[v]);
        leader.changeReligionWeightModifier(eReligion,changes[d]);
        assert(leader.getReligionWeightModifier(eReligion)==initial[v]+changes[d]);
        assert(values[1-id]==(id==0?13:11));++weightCases;
    }
    CvLeaderHeadInfo empty;empty.m_piReligionWeightModifier=NULL;
    assert(empty.getReligionWeightModifier(RELIGION0)==0);
    assert(empty.getReligionWeightModifier(RELIGION1)==0);weightCases+=2;
    assert(getterCases==15&&weightCases==20);
    std::cout<<getterCases<<" organization getter cases and "<<weightCases<<" religion weight cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'CvInfo_Organization.h').write_text(organization);(p/'check.cpp').write_text(code)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,
                   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
