#!/usr/bin/env python3
"""Compile the actual XANA enum proxy against a small C++03 globals fixture."""
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
header = (root / "CvGameCoreDLL/CvGlobals.h").read_text()
macros = root / "CvGameCoreDLL/CvEnumMacros.h"
start = header.index("class CvEnumType\n{")
end = header.index("// XANA: 03-21-2026 Easy Enum Lookup", start)
proxy = header[start:end]
declaration = next(line.strip() for line in header.splitlines()
                   if "CvEnumType getEnumForString(" in line)
fixture = r'''
#include <cassert>
#include <cstring>
#include <string>
#include "CvEnumMacros.h"
typedef std::string CvString;
#define DECLARE_ENUM(Name, Prefix) enum Name##Types { Name##TestValue = 0 };
DO_FOR_EACH_DYN_INFO_TYPE(DECLARE_ENUM)
DO_FOR_EACH_STATIC_INFO_TYPE(DECLARE_ENUM)
#undef DECLARE_ENUM
int assertionCount = 0;
bool hideAssertSeen = false;
#define FAssertMsg(condition, message) do { if (!(condition)) ++assertionCount; } while (false)
class CvEnumType;
class CvGlobals {
public:
    static CvGlobals const& getConstInstance() { static CvGlobals globals; return globals; }
    int getInfoTypeForString(char const* name, bool hideAssert) const {
        hideAssertSeen = hideAssert;
        if (std::strcmp(name, "UNIT_WARRIOR") == 0) return 17;
        if (std::strcmp(name, "CIVIC_POLICE_STATE") == 0) return 23;
        return -1;
    }
    @DECLARATION@
};
@PROXY@
#define GC CvGlobals::getConstInstance()
int main() {
    UnitTypes copy = GET_ENUM("UNIT_WARRIOR");
    CivicTypes direct(GET_ENUM("CIVIC_POLICE_STATE"));
    assert(static_cast<int>(copy) == 17 && static_cast<int>(direct) == 23);
    CvEnumType temporary = GET_ENUM(std::string("UNIT_WARRIOR").c_str());
    std::string churn(1000, 'x');
    UnitTypes delayed = temporary;
    assert(static_cast<int>(delayed) == 17);
    std::string name("UNIT_WARRIOR");
    CvEnumType saved = GET_ENUM(name.c_str());
    name.assign("CIVIC_POLICE_STATE");
    UnitTypes preserved = saved;
    assert(static_cast<int>(preserved) == 17);
    UnitTypes missing = GET_ENUM_HIDE_ASSERT("UNIT_MISSING");
    assert(static_cast<int>(missing) == -1 && hideAssertSeen);
    UnitTypes mismatch = GET_ENUM("CIVIC_POLICE_STATE");
    (void)mismatch;
#ifdef FASSERT_ENABLE
    assert(assertionCount == 1);
#else
    assert(assertionCount == 0);
#endif
    return 0;
}
'''.replace("@DECLARATION@", declaration).replace("@PROXY@", proxy)
with tempfile.TemporaryDirectory() as temp:
    source = pathlib.Path(temp) / "enum_lookup.cpp"
    source.write_text(fixture)
    for assertions in (False, True):
        binary = pathlib.Path(temp) / ("assertions" if assertions else "release")
        command = ["g++", "-std=c++03", "-pedantic-errors", "-Wall", "-Wextra",
                   "-I", str(macros.parent), str(source), "-o", str(binary)]
        if assertions:
            command.insert(1, "-DFASSERT_ENABLE")
        subprocess.run(command, check=True)
        subprocess.run([str(binary)], check=True)
print("C++03 enum proxy checks passed with assertions disabled and enabled.")
