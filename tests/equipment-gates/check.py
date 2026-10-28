#!/usr/bin/env python3
"""Compile actual unit acquisition methods against instrumented metadata/team stubs.

Only the listed method boundary is checked; this is not an equipment engine or DLL.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvUnit.cpp').read_text()

def method(signature):
    start = source.index(signature)
    brace, depth = source.index('{', start), 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

methods = '\n'.join(method(s) for s in [
    'bool CvUnit::canAcquireEquipment(EquipmentTypes',
    'bool CvUnit::isEquipmentValid(EquipmentTypes',
    'bool CvUnit::canAcquireEquipmentAny()'])
tree = ET.parse(root / 'XML/Units/CIV4EquipmentInfos.xml')
item = next(x for x in tree.getroot().iter() if x.tag.rsplit('}', 1)[-1] == 'EquipmentInfo')
values = {x.tag.rsplit('}', 1)[-1]: x.text for x in item}
minimum, maximum = int(values['iEquipmentLowestLevelRequired']), int(values['iEquipmentHighestLevelRequired'])
assert values['Type'] == 'EQUIPMENT_ALICORN_AMULET' and (minimum, maximum) == (1, 9)
stub = r'''
#include <cassert>
#include <cstddef>
enum EquipmentTypes { NO_EQUIPMENT = -1, EQUIP_A, EQUIP_B, EQUIP_C, EQUIP_D, EQUIP_E, EQUIP_F, EQUIP_G, EQUIP_H, NUM_EQUIPMENT };
enum PromotionTypes { NO_PROMOTION = -1, PROMO_A, PROMO_B, PROMO_C, PROMO_D, NUM_PROMOTION };
enum UnitTypes { NO_UNIT = -1, UNIT_A, UNIT_B };
enum EquipmentClassTypes { NO_EQUIPMENT_CLASS = -1, CLASS_A };
enum TechTypes { NO_TECH = -1, TECH_A, TECH_B };
enum MagicTechClassTypes { NO_MAGIC_TECH_CLASS = -1, MAGIC_CLASS_A, MAGIC_CLASS_B };
enum MagicTechTypes { NO_MAGIC_TECH = -1, MAGIC_TECH_A, MAGIC_TECH_B };
struct CvEquipmentInfo {
    int low, high;
    bool legendary, personal;
    UnitTypes unit;
    PromotionTypes enchantment, promotion, orPromotion[3];
    EquipmentTypes equipment, orEquipment[3];
    TechTypes tech;
    MagicTechClassTypes magicClass;
    MagicTechTypes magicTech;
    CvEquipmentInfo() : low(ACTUAL_MIN), high(ACTUAL_MAX), legendary(false), personal(false),
        unit(NO_UNIT), enchantment(NO_PROMOTION), promotion(NO_PROMOTION), equipment(NO_EQUIPMENT),
        tech(NO_TECH), magicClass(NO_MAGIC_TECH_CLASS), magicTech(NO_MAGIC_TECH) {
        for (int i = 0; i < 3; ++i) { orPromotion[i] = NO_PROMOTION; orEquipment[i] = NO_EQUIPMENT; }
    }
    int getEquipmentLowestLevelRequired() const { return low; }
    int getEquipmentHighestLevelRequired() const { return high; }
    bool isLegendaryWeapon() const { return legendary; }
    bool isPersonalWeapon() const { return personal; }
    UnitTypes getPrereqUnitType() const { return unit; }
    PromotionTypes getRequiredEnchantment() const { return enchantment; }
    PromotionTypes getPrereqPromotion() const { return promotion; }
    PromotionTypes getPrereqOrPromotion1() const { return orPromotion[0]; }
    PromotionTypes getPrereqOrPromotion2() const { return orPromotion[1]; }
    PromotionTypes getPrereqOrPromotion3() const { return orPromotion[2]; }
    EquipmentTypes getPrereqEquipment() const { return equipment; }
    EquipmentTypes getPrereqOrEquipment1() const { return orEquipment[0]; }
    EquipmentTypes getPrereqOrEquipment2() const { return orEquipment[1]; }
    EquipmentTypes getPrereqOrEquipment3() const { return orEquipment[2]; }
    TechTypes getTechPrereq() const { return tech; }
    MagicTechClassTypes getMagicTechClassPrereq() const { return magicClass; }
    MagicTechTypes getMagicTechPrereq() const { return magicTech; }
};
struct Globals {
    CvEquipmentInfo equipment[NUM_EQUIPMENT];
    int queries;
    Globals() : queries(0) {}
    int getNumEquipmentInfos() const { return NUM_EQUIPMENT; }
    CvEquipmentInfo const& getInfo(EquipmentTypes e) {
        assert(e >= 0 && e < NUM_EQUIPMENT); ++queries; return equipment[e];
    }
} GC;
struct UnitInfo {
    bool feasible, hero;
    mutable int checks;
    UnitInfo() : feasible(true), hero(false), checks(0) {}
    bool isEquipmentValid(EquipmentTypes, bool leader) const { assert(leader); ++checks; return feasible; }
    bool isHero() const { return hero; }
};
struct Team {
    bool tech[2], magicClass[2], magicTech[2];
    Team() { for (int i = 0; i < 2; ++i) tech[i] = magicClass[i] = magicTech[i] = false; }
    bool isHasTech(TechTypes e) const { assert(e >= 0 && e < 2); return tech[e]; }
    bool isHasMagicTechClass(MagicTechClassTypes e) const { assert(e >= 0 && e < 2); return magicClass[e]; }
    bool isHasMagicTech(MagicTechTypes e) const { assert(e >= 0 && e < 2); return magicTech[e]; }
} team;
#define GET_TEAM(id) team
#define FAssertEnumBounds(e) assert((e) >= 0 && (e) < NUM_EQUIPMENT)
#define FOR_EACH_ENUM(Type) for (EquipmentTypes eLoopEquipment = EQUIP_A; eLoopEquipment < NUM_EQUIPMENT; eLoopEquipment = static_cast<EquipmentTypes>(eLoopEquipment + 1))
struct CvUnit {
    UnitInfo info;
    UnitInfo* m_pUnitInfo;
    bool equipment[NUM_EQUIPMENT], promotions[NUM_PROMOTION];
    int level;
    EquipmentClassTypes equipmentClass;
    mutable int levelReads;
    CvUnit() : m_pUnitInfo(&info), level(1), equipmentClass(CLASS_A), levelReads(0) {
        for (int i = 0; i < NUM_EQUIPMENT; ++i) equipment[i] = false;
        for (int i = 0; i < NUM_PROMOTION; ++i) promotions[i] = false;
    }
    bool isHasEquipment(EquipmentTypes e) const { assert(e >= 0 && e < NUM_EQUIPMENT); return equipment[e]; }
    bool isHasPromotion(PromotionTypes e) const { assert(e >= 0 && e < NUM_PROMOTION); return promotions[e]; }
    EquipmentClassTypes getEquipmentClass() const { return equipmentClass; }
    int getEquipmentLevel() const { assert(equipmentClass != NO_EQUIPMENT_CLASS); ++levelReads; return level; }
    UnitTypes getUnitType() const { return UNIT_A; }
    int getTeam() const { return 0; }
    bool canAcquireEquipment(EquipmentTypes) const;
    bool isEquipmentValid(EquipmentTypes) const;
    bool canAcquireEquipmentAny() const;
};
'''
checks = r'''
void resetMetadata() {
    for (int i = 0; i < NUM_EQUIPMENT; ++i) GC.equipment[i] = CvEquipmentInfo();
    GC.queries = 0; team = Team();
}
int main() {
    resetMetadata(); CvUnit u; CvEquipmentInfo& e = GC.equipment[0];
    for (int level = 0; level <= 10; ++level) {
        u.level = level;
        assert(u.canAcquireEquipment(EQUIP_A) == (level >= 1 && level <= 9));
    }
    u.level = 5; assert(u.isEquipmentValid(EQUIP_A) && u.canAcquireEquipment(EQUIP_A));
    e.low = 0; e.high = 0; u.equipmentClass = NO_EQUIPMENT_CLASS; u.levelReads = 0;
    assert(u.canAcquireEquipment(EQUIP_A) && u.levelReads == 0);
    e.high = 9; assert(!u.canAcquireEquipment(EQUIP_A) && u.levelReads == 0);
    u.equipmentClass = CLASS_A; resetMetadata();
    for (int low = 0; low <= 3; ++low) for (int high = 0; high <= 3; ++high)
        for (int level = 0; level <= 4; ++level) {
            e.low = low; e.high = high; u.level = level;
            assert(u.canAcquireEquipment(EQUIP_A) == ((low == 0 || level >= low) && (high == 0 || level <= high)));
        }
    resetMetadata(); u.level = 5;
    u.info.feasible = false; u.levelReads = 0;
    assert(!u.canAcquireEquipment(EQUIP_A) && u.levelReads == 0); u.info.feasible = true;
    u.equipment[0] = true; assert(!u.canAcquireEquipment(EQUIP_A)); u.equipment[0] = false;
    int priorQueries = GC.queries, priorChecks = u.info.checks;
    assert(!u.canAcquireEquipment(NO_EQUIPMENT));
    assert(!u.canAcquireEquipment(static_cast<EquipmentTypes>(NUM_EQUIPMENT)));
    assert(!u.isEquipmentValid(NO_EQUIPMENT));
    assert(!u.isEquipmentValid(static_cast<EquipmentTypes>(NUM_EQUIPMENT)));
    assert(GC.queries == priorQueries && u.info.checks == priorChecks);
    e.legendary = true; e.enchantment = PROMO_D;
    assert(!u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_D] = true; assert(u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_D] = false; u.info.hero = true; assert(u.canAcquireEquipment(EQUIP_A));
    u.level = 10; assert(!u.canAcquireEquipment(EQUIP_A)); u.level = 5;
    e.personal = true; e.unit = UNIT_B; assert(!u.canAcquireEquipment(EQUIP_A));
    e.unit = UNIT_A; assert(u.canAcquireEquipment(EQUIP_A));
    resetMetadata(); u.info.hero = false;
    e.promotion = PROMO_A; assert(!u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_A] = true; assert(u.canAcquireEquipment(EQUIP_A));
    e.orPromotion[0] = PROMO_B; e.orPromotion[2] = PROMO_C; assert(!u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_C] = true; assert(u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_A] = false; assert(!u.canAcquireEquipment(EQUIP_A));
    u.promotions[PROMO_A] = true;
    e.equipment = EQUIP_B; assert(!u.canAcquireEquipment(EQUIP_A));
    u.equipment[EQUIP_B] = true; assert(u.canAcquireEquipment(EQUIP_A));
    e.orEquipment[0] = EQUIP_C; e.orEquipment[2] = EQUIP_D; assert(!u.canAcquireEquipment(EQUIP_A));
    u.equipment[EQUIP_D] = true; assert(u.canAcquireEquipment(EQUIP_A));
    u.equipment[EQUIP_B] = false; assert(!u.canAcquireEquipment(EQUIP_A)); u.equipment[EQUIP_B] = true;
    e.tech = TECH_A; assert(!u.canAcquireEquipment(EQUIP_A)); team.tech[TECH_A] = true;
    e.magicClass = MAGIC_CLASS_A; assert(!u.canAcquireEquipment(EQUIP_A)); team.magicClass[MAGIC_CLASS_A] = true;
    e.magicTech = MAGIC_TECH_A; assert(!u.canAcquireEquipment(EQUIP_A)); team.magicTech[MAGIC_TECH_A] = true;
    assert(u.canAcquireEquipment(EQUIP_A));
    u.info.hero = true; team.tech[TECH_A] = false; assert(!u.canAcquireEquipment(EQUIP_A));
    team.tech[TECH_A] = true;
    assert(u.promotions[PROMO_A] && u.promotions[PROMO_C] && !u.promotions[PROMO_D]);
    assert(u.equipment[EQUIP_B] && u.equipment[EQUIP_D] && !u.equipment[EQUIP_A] && u.level == 5);
    resetMetadata(); CvUnit any;
    for (int i = 0; i < NUM_EQUIPMENT; ++i) any.equipment[i] = true;
    assert(!any.canAcquireEquipmentAny()); any.equipment[EQUIP_H] = false;
    assert(any.canAcquireEquipmentAny());
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp, binary = Path(directory) / 'equipment.cpp', Path(directory) / 'equipment'
    cpp.write_text(stub.replace('ACTUAL_MIN', str(minimum)).replace('ACTUAL_MAX', str(maximum)) + '\n' + methods + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('Actual equipment gates: strict C++03 + ASan/UBSan passed; XML level range 1..9 checked')
