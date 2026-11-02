#!/usr/bin/env python3
"""Compile the actual hybrid-building valuation block with distinct enum stubs."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvCityAI.cpp').read_text()
start = source.index('// XANA: 11-02-2026 Hybrid building valuation native scope fixes (ChatGPT)')
start = source.index('{', start)
end = source.index('// K-Mod end (corp)', start)
block = source[start:end]
prefix = r'''
#include <cassert>
#include <iostream>
enum HybridOrganizationTypes {NO_HYBRID_ORGANIZATION=-1,HYBRID};
enum ReligionTypes {NO_RELIGION=-1,RELIGION};
enum CorporationTypes {NO_CORPORATION=-1,CORP_A,CORP_B};
enum CommerceTypes {COMMERCE};
#define FOR_EACH_ENUM(Name) for (Name##Types eLoop##Name=static_cast<Name##Types>(0); \
    eLoop##Name<static_cast<Name##Types>(Name##Count); \
    eLoop##Name=static_cast<Name##Types>(eLoop##Name+1))
int const CorporationCount=2,CommerceCount=1;
struct CvHybridOrganizationInfo {
    ReligionTypes religion;
    CorporationTypes corporation;
    ReligionTypes getTriggerReligion()const{return religion;}
    CorporationTypes getTriggerCorporation()const{return corporation;}
} hybrid;
struct CorporationInfo {int getHeadquarterCommerce(CommerceTypes)const{return 2;}} corporation;
struct Game {
    int levels,calls;
    int countCorporationLevels(CorporationTypes id) {assert(id>=CORP_A&&id<=CORP_B);++calls;return levels;}
    bool isCompetingCorporation(CorporationTypes a,CorporationTypes b)const{return a!=b;}
} game;
struct Globals {
    CvHybridOrganizationInfo const& getInfo(HybridOrganizationTypes id)const {assert(id==HYBRID);return hybrid;}
    CorporationInfo const& getInfo(CorporationTypes id)const {assert(id>=CORP_A&&id<=CORP_B);return corporation;}
    Game& getGame()const{return game;}
} GC;
struct Building {HybridOrganizationTypes id;HybridOrganizationTypes getFoundsHybridOrganization()const{return id;}} building;
struct Player {
    bool disabled,competitor;
    int competitorValue,calls;
    bool AI_atVictoryStage4()const{return false;}
    bool isNoCorporations()const{return disabled;}
    int AI_corporationValue(CorporationTypes id,void const* =NULL){assert(id>=CORP_A&&id<=CORP_B);++calls;return id==CORP_A?100:competitorValue;}
    bool hasHeadquarters(CorporationTypes id)const{return competitor&&id==CORP_B;}
    int AI_commerceWeight(CommerceTypes,void const*)const{return 100;}
} player;
struct City {
    int getTotalCommerceRateModifier(CommerceTypes)const{return 100;}
    int findCommerceRateRank(CommerceTypes)const{return 1;}
    int getNumNationalWonders()const{return 0;}
    int value(){
        Building const& kBuilding=building;Player& kOwner=player;Game& kGame=game;
        int const iNumCities=4;bool const bWarPlan=false;int iValue=0;
'''
suffix = r'''
        return iValue;
    }
};
int main(){City city;building.id=HYBRID;hybrid.religion=RELIGION;hybrid.corporation=CORP_A;
    player.disabled=false;player.competitor=false;game.levels=0;game.calls=0;player.calls=0;
    assert(city.value()==30);assert(game.calls==1&&player.calls==1);
    player.competitor=true;player.competitorValue=200;assert(city.value()==0);
    game.levels=1;assert(city.value()==11);
    game.levels=0;player.competitorValue=50;assert(city.value()==15);
    player.disabled=true;assert(city.value()==0);
    player.disabled=false;hybrid.corporation=NO_CORPORATION;game.calls=0;player.calls=0;
    assert(city.value()==0);assert(game.calls==0&&player.calls==0);
    hybrid.corporation=CORP_A;hybrid.religion=NO_RELIGION;assert(city.value()==0);
    building.id=NO_HYBRID_ORGANIZATION;assert(city.value()==0);
    std::cout<<"8 hybrid-building valuation/sentinel cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p = Path(directory)
    (p / 'check.cpp').write_text(prefix + block + suffix)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-g', str(p / 'check.cpp'),
                    '-o', str(p / 'check')], check=True)
    subprocess.run([str(p / 'check')], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
