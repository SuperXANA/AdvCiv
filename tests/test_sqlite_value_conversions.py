#!/usr/bin/env python3
"""Exercise production SQLiteValue integer conversions in C++03.
Reuses the existing Civ stub without executing its database/engine harness.
This does not validate the Civ4 DLL ABI or gameplay.
"""
import ast
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
module = ast.parse((ROOT / "tests/test_sqlite_wrappers.py").read_text())
stub = next(ast.literal_eval(node.value) for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "STUB" for t in node.targets))
test = r'''
#include "SQLiteValue.h"
#include <cassert>
#include <limits>
int main() {
    assert(sizeof(int)==4);
    assert(int(SQLiteValue(12.75))==12);
    assert(int(SQLiteValue(-12.75))==-12);
    assert(int(SQLiteValue(double(INT_MAX)))==INT_MAX);
    assert(int(SQLiteValue(double(INT_MIN)))==INT_MIN);
    assert(int(SQLiteValue(double(INT_MAX)+0.5))==INT_MAX);
    assert(int(SQLiteValue(double(INT_MIN)-0.5))==INT_MIN);
    assert(int(SQLiteValue(double(INT_MAX)+1.0))==0);
    assert(int(SQLiteValue(double(INT_MIN)-1.0))==0);
    assert(int(SQLiteValue(1e100))==0);
    assert(int(SQLiteValue(-1e100))==0);
    assert(int(SQLiteValue(std::numeric_limits<double>::quiet_NaN()))==0);
    assert(int(SQLiteValue(std::numeric_limits<double>::infinity()))==0);
    assert(int(SQLiteValue(-std::numeric_limits<double>::infinity()))==0);
    assert(!bool(SQLiteValue(1e100)));
    assert(int(SQLiteValue(CvString("2147483647")))==INT_MAX);
    assert(int(SQLiteValue(CvString("-2147483648")))==INT_MIN);
    assert(int(SQLiteValue(CvString("2147483648")))==0);
    assert(int(SQLiteValue(CvString("-2147483649")))==0);
    assert(int(SQLiteValue(CvString(std::string(128,'9'))))==0);
    // XANA: 10-30-2026 Keep the comparison inside assert in this test case.
    assert(int(SQLiteValue(CvString(std::string("-")+std::string(128,'9'))))==0);
    // XANA: END integer conversion regression syntax repair.
    assert(int(SQLiteValue(CvString("  -12suffix")))==-12);
    assert(int(SQLiteValue(CvString("+12.75")))==12);
    assert(int(SQLiteValue(CvString("not a number")))==0);
    assert(int(SQLiteValue(CvString("")))==0);
    assert(int(SQLiteValue())==0);
    assert(int(SQLiteValue(73))==73);
}
'''
with tempfile.TemporaryDirectory() as temporary:
    work = pathlib.Path(temporary)
    (work / "CvGameCoreDLL.h").write_text(stub)
    for name in ("SQLiteValue.h", "CvDatabaseSchema.h"):
        (work / name).write_text((ROOT / "CvGameCoreDLL" / name).read_text())
    (work / "test.cpp").write_text(test)
    command = ["g++", "-std=c++03", "-pedantic-errors", "-Wall", "-Wextra",
               str(work / "test.cpp"), "-o", str(work / "test")]
    if os.environ.get("SQLITE_TEST_SANITIZE") == "1":
        command[1:1] = ["-fsanitize=undefined,float-cast-overflow",
                        "-fno-sanitize-recover=all"]
    subprocess.run(command, check=True)
    subprocess.run([str(work / "test")], check=True)
print("SQLiteValue C++03 integer conversion checks passed.")
