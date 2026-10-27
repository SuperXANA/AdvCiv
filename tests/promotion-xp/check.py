#!/usr/bin/env python3
"""Check the actual XP modifier methods in a focused C++03 fixture."""
import pathlib
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[2]
source = (root / "CvGameCoreDLL/CvUnit.cpp").read_text()
header = (root / "CvGameCoreDLL/CvUnit.h").read_text()

def method(name):
    match = re.search(r"(?:int|void) CvUnit::" + name + r"\([^)]*\)(?: const)?\s*\{", source)
    assert match, name
    start, pos, depth = match.start(), match.end(), 1
    while depth:
        depth += (source[pos] == "{") - (source[pos] == "}")
        pos += 1
    return source[start:pos]

names = ["getXPValueAttackModifier", "changeXPValueAttackModifier",
         "getXPValueDefenseModifier", "changeXPValueDefenseModifier",
         "updateXPValueModifiers", "attackXPValue", "defenseXPValue"]
declarations = []
for name in names:
    declarations.append(next(line.split("//")[0].strip() for line in header.splitlines()
                             if re.search(r"\b" + name + r"\(", line)
                             and line.split("//")[0].strip().endswith(";")))
read = source[source.index("void CvUnit::read("):source.index("void CvUnit::write(")]
assert read.index("m_abHasPromotion.read") < read.index("updateXPValueModifiers();")
assert read.count("updateXPValueModifiers();") == 1
fixture = r'''
#include <cassert>
struct PromotionInfo {
    int attack, defense;
    int getXPValueAttackChange() const { return attack; }
    int getXPValueDefenseChange() const { return defense; }
};
struct Globals {
    PromotionInfo entries[2];
    PromotionInfo const& getInfo(int index) const { return entries[index]; }
} GC = {{{3,2},{-1,4}}};
#define FOR_EACH_ENUM(Dummy) for (int eLoopPromotion=0; eLoopPromotion<2; ++eLoopPromotion)
struct UnitInfo {
    int getXPValueAttack() const { return 4; }
    int getXPValueDefense() const { return 2; }
};
struct CvUnit {
    int m_iXPValueAttackModifier, m_iXPValueDefenseModifier;
    bool promotions[2], barbarian, animal;
    UnitInfo info;
    UnitInfo* m_pUnitInfo;
    CvUnit() : m_iXPValueAttackModifier(0), m_iXPValueDefenseModifier(0),
        barbarian(false), animal(false), m_pUnitInfo(&info) {
        promotions[0] = promotions[1] = false;
    }
    bool isHasPromotion(int promotion) const { return promotions[promotion]; }
    bool isBarbarian() const { return barbarian; }
    bool isAnimal() const { return animal; }
    @DECLARATIONS@
};
@METHODS@
int main() {
    CvUnit unit;
    assert(unit.attackXPValue()==4 && unit.defenseXPValue()==2);
    unit.promotions[0]=true;
    unit.updateXPValueModifiers();
    assert(unit.attackXPValue()==7 && unit.defenseXPValue()==4);
    unit.updateXPValueModifiers();
    assert(unit.getXPValueAttackModifier()==3 && unit.getXPValueDefenseModifier()==2);
    unit.barbarian=true;
    assert(unit.attackXPValue()==6);
    unit.animal=true;
    assert(unit.attackXPValue()==7);
    unit.barbarian=unit.animal=false;
    unit.promotions[1]=true;
    unit.updateXPValueModifiers();
    assert(unit.attackXPValue()==6 && unit.defenseXPValue()==8);
    unit.promotions[0]=false;
    unit.updateXPValueModifiers();
    assert(unit.attackXPValue()==3 && unit.defenseXPValue()==6);
    unit.promotions[1]=false;
    unit.updateXPValueModifiers();
    assert(unit.attackXPValue()==4 && unit.defenseXPValue()==2);
    unit.changeXPValueAttackModifier(3);
    unit.changeXPValueDefenseModifier(2);
    assert(unit.attackXPValue()==7 && unit.defenseXPValue()==4);
    unit.changeXPValueAttackModifier(-3);
    unit.changeXPValueDefenseModifier(-2);
    assert(unit.attackXPValue()==4 && unit.defenseXPValue()==2);
}
'''.replace("@DECLARATIONS@", "\n".join(declarations)).replace(
    "@METHODS@", "\n\n".join(method(name) for name in names))
with tempfile.TemporaryDirectory() as temp:
    cpp = pathlib.Path(temp) / "xp.cpp"
    binary = pathlib.Path(temp) / "xp"
    cpp.write_text(fixture)
    subprocess.run(["g++", "-std=c++03", "-pedantic-errors", "-Wall", "-Wextra",
                    str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)

promotions = ET.parse(root / "Assets/XML/Units/CIV4PromotionInfos.xml").getroot()
ns = {"c": "x-schema:CIV4UnitSchema.xml"}
records = promotions.findall("c:PromotionInfos/c:PromotionInfo", ns)
combat = next(p for p in records if p.findtext("c:Type", namespaces=ns) == "PROMOTION_COMBAT1")
assert combat.findtext("c:iXPValueAttackChange", namespaces=ns) == "3"
assert combat.findtext("c:iXPValueDefenseChange", namespaces=ns) == "2"
info_source = (root / "CvGameCoreDLL/CvInfo_Unit.cpp").read_text()
for tag in ("iXPValueAttackChange", "iXPValueDefenseChange"):
    assert re.search(r'GetChildXmlValByName\([^\n]*"' + tag + r'", 0\);', info_source)
schema = (root / "Assets/XML/Units/CIV4UnitSchema.xml").read_text()
for tag in ("iXPValueAttackChange", "iXPValueDefenseChange"):
    assert '<element type="' + tag + '" minOccurs="0"/>' in schema
text = (root / "Assets/XML/Text/CIV4GameText_gamemods_mlp.xml").read_text()
ET.fromstring(text)
assert "%d1_XPChange" in text and "%s2_TextInfo" in text and "%%" not in text
print("XP reconstruction, stacking/removal, declarations, XML defaults and text checks passed.")
