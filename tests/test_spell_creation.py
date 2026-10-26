#!/usr/bin/env python3
"""Compile the production spell-creation structs in isolation as C++03.

Run: python3 tests/test_spell_creation.py
Optional: SPELL_TEST_SANITIZE=1 python3 tests/test_spell_creation.py
This uses XML/engine stubs: it does NOT validate XML traversal or build the DLL.
"""
# XANA: 10-26-2026 Focused spell creation ownership regression test (ChatGPT)
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKER = "// XANA: 03-28-2026 Magical Spell System for Advanced Civ"
header = (ROOT / "CvGameCoreDLL/CvStructs.h").read_text().split(MARKER)[1]
implementation = (ROOT / "CvGameCoreDLL/CvStructs.cpp").read_text().split(MARKER)[1]
STUBS = r'''
#include <cassert>
#include <cstddef>
#include <cstring>
#include <set>
enum UnitClassTypes { NO_UNITCLASS = -1, TEST_UNITCLASS = 3 };
enum UnitTypes { NO_UNIT = -1, TEST_UNIT = 7 };
typedef char TCHAR;
static std::set<bool*> allocations;
static void releaseArray(bool*& p)
{
    if (p != NULL) { assert(allocations.erase(p) == 1); delete[] p; p = NULL; }
}
#define SAFE_DELETE_ARRAY(p) releaseArray(p)
struct XMLInterface {
    int parents;
    XMLInterface() : parents(0) {}
    void SetToParent(void*) { ++parents; }
};
struct DLL {
    XMLInterface xml;
    XMLInterface* getXMLIFace() { return &xml; }
} dll;
static DLL* gDLL = &dll;
struct Globals { int getNumPromotionInfos() const { return 3; } } GC;
class CvXMLLoadUtility {
public:
    void* GetXML() { return NULL; }
    void SetVariableListTagPair(bool** pp, TCHAR const* tag, int size) {
        // Synthetic nonempty lists; only allocation reuse models the base loader.
        if (*pp == NULL) { *pp = new bool[size]; allocations.insert(*pp); }
        for (int i = 0; i < size; ++i)
            (*pp)[i] = (i == (std::strcmp(tag, "AddPromotions") == 0 ? 1 : 2));
    }
};
'''
TEST = r'''
template<class Creation> void checkData(Creation& data)
{
    SpellUnitCreationSubData& kSubStruct = data.getCreationData();
    Creation const& constData = data;
    assert(&constData.getCreationData() == &kSubStruct);
    assert(kSubStruct.getCreationNumber() == 0);
    assert(kSubStruct.getAddPromotionsArray() == NULL);
    assert(kSubStruct.getRemovePromotionsArray() == NULL);
    kSubStruct.setCreationNumber(4);
    assert(constData.getCreationData().getCreationNumber() == 4);
    CvXMLLoadUtility xml;
    CvXMLLoadUtility* pXML = &xml;
    // These are the production loader's pointer-to-pointer expressions.
    kSubStruct.readPromotions(pXML, "AddPromotions", &kSubStruct.getAddPromotionsArray());
    kSubStruct.readPromotions(pXML, "RemovePromotions", &kSubStruct.getRemovePromotionsArray());
    assert(constData.getCreationData().getAddPromotionsArray()[1]);
    assert(!constData.getCreationData().getAddPromotionsArray()[2]);
    assert(constData.getCreationData().getRemovePromotionsArray()[2]);
    bool const* original = constData.getCreationData().getAddPromotionsArray();
    kSubStruct.readPromotions(pXML, "AddPromotions", &kSubStruct.getAddPromotionsArray());
    assert(original == constData.getCreationData().getAddPromotionsArray());
}
int main()
{
    { SpellUnitCreationSubData empty; }
    assert(allocations.empty());
    {
        UnitCreationData* partial = new UnitCreationData;
        CvXMLLoadUtility xml;
        SpellUnitCreationSubData& data = partial->getCreationData();
        data.readPromotions(&xml, "AddPromotions", &data.getAddPromotionsArray());
        assert(data.getRemovePromotionsArray() == NULL);
        assert(allocations.size() == 1);
        delete partial;
    }
    assert(allocations.empty());
    for (int i = 0; i < 2; ++i) {
        {
            UnitClassCreationData byClass;
            UnitCreationData byUnit;
            assert(byClass.getClassType() == NO_UNITCLASS);
            assert(byUnit.getUnitType() == NO_UNIT);
            byClass.setClassType(TEST_UNITCLASS);
            byUnit.setUnitType(TEST_UNIT);
            assert(byClass.getClassType() == TEST_UNITCLASS);
            assert(byUnit.getUnitType() == TEST_UNIT);
            checkData(byClass);
            checkData(byUnit);
            assert(allocations.size() == 4);
        }
        assert(allocations.empty());
    }
    assert(dll.xml.parents == 13);
}
'''
compiler = shlex.split(os.environ.get("CXX", "g++"))
flags = ["-std=c++03", "-Wall", "-Wextra", "-Werror", "-pedantic-errors"]
if os.environ.get("SPELL_TEST_SANITIZE") == "1":
    flags += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
source = STUBS + header + implementation
with tempfile.TemporaryDirectory(prefix="spell-creation-") as temporary:
    path = Path(temporary)
    cpp, binary = path / "test.cpp", path / "test"
    cpp.write_text(source + TEST)
    subprocess.run(compiler + flags + [str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
    # Reject shallow copies of both owning subdata and its containing records.
    checks = []
    for name in ("SpellUnitCreationSubData", "UnitClassCreationData", "UnitCreationData"):
        checks += [name + " a; " + name + " b(a);", name + " a, b; b = a;"]
    checks += ["const UnitCreationData a; a.getCreationData().setCreationNumber(1);",
               "const UnitClassCreationData a; a.getCreationData().getAddPromotionsArray()[0] = true;"]
    for code in checks:
        cpp.write_text(source + "\nint main() { " + code + " }\n")
        result = subprocess.run(compiler + ["-std=c++03", "-pedantic-errors", "-fsyntax-only", str(cpp)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            raise AssertionError("Unsafe operation compiled: " + code)
print("PASS: C++03 initialization, type/count persistence, owned-pointer loading/reuse, cleanup;")
print("      8 compile-negative copy/const-correctness checks. XML traversal/DLL not tested.")
