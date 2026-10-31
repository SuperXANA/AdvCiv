#!/usr/bin/env python3
"""Complete header, native size_t and explicitly simulated unsigned-32 arithmetic."""
from pathlib import Path
import ctypes
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
header = (root / 'CvGameCoreDLL/FSimpleDataStorage.h').read_text()
prefix = r'''
#include <cassert>
#include <climits>
#include <cstddef>
#include <new>
#define FAssert(x) assert(x)
#define FAssertMsg(x,m) ((void)0)
#define SAFE_DELETE_ARRAY(p) do { delete[] p; p = NULL; } while (0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do { delete[] (reinterpret_cast<char*>(p) - (n)); p = NULL; } while (0)
struct FDataStreamBase {
    int count, dataReads;
    FDataStreamBase(int n) : count(n), dataReads(0) {}
    void Read(int* p) { *p = count; }
    template<class T> void Read(int, T*) { ++dataReads; }
    template<class T> void Write(T) {}
    template<class T> void Write(int, T const*) {}
};
struct CvXMLLoadUtility {
    template<class T> void SetVariableListTagPair(T**, char const*, int) {}
};
#include "FSimpleDataStorage.h"
'''
body = r'''
void classChecks() {
    FDynamicArray<double> a;
    FDynamic2DArray<double> b;
    a.init(3, 2.5); b.init(2, 3, 1.5);
    assert(a.size() == 3 && a.get(2) == 2.5);
    assert(b.size() == 6 && b.get(5) == 1.5);
    FDynamicArray<double> ac(a);
    FDynamic2DArray<double> bc(b);
    assert(ac.size() == 3 && ac.get(2) == 2.5);
    assert(bc.size() == 6 && bc.get(5) == 1.5);
    double* raw = new double[2]; raw[0] = 7; raw[1] = 9;
    a.load(raw, 2); assert(raw == NULL && a.size() == 2 && a.get(1) == 9);
    double** rows = new double*[1]; rows[0] = new double[2];
    rows[0][0] = 11; rows[0][1] = 13;
    b.load(rows, 1, 2); assert(rows == NULL && b.size() == 2 && b.get(1) == 13);
    // Negative/zero init retain existing API behavior.
    a.init(-1); b.init(-1, -1);
    assert(a.size() == 2 && b.size() == 2);
    a.clear(); b.clear();
#ifdef SIMULATED_32
    assert(sizeof(unsigned int) == 4 && INT_MAX == 2147483647);
    a.init(INT_MAX);
    assert(a.size() == 0);
    b.init(INT_MAX, 1);
    assert(b.size() == 0);
    a.init(2, 17); b.init(2, 1, 19);
    // An existing init is still a no-op, even for an oversized request.
    a.init(INT_MAX); b.init(INT_MAX, 1);
    assert(a.size() == 2 && a.get(0) == 17);
    assert(b.size() == 2 && b.get(0) == 19);
    a.reset(INT_MAX);
    assert(a.size() == 0);
    b.reset(INT_MAX, 1);
    assert(b.size() == 0);
    raw = new double[1]; raw[0] = 23;
    double* savedRaw = raw;
    a.load(raw, INT_MAX);
    assert(a.size() == 0 && raw == savedRaw && raw[0] == 23);
    delete[] raw;
    rows = new double*[1]; rows[0] = new double[1]; rows[0][0] = 29;
    double** savedRows = rows;
    b.load(rows, INT_MAX, 1);
    assert(b.size() == 0 && rows == savedRows && rows[0][0] == 29);
    delete[] rows[0]; delete[] rows;
    FDataStreamBase stream(INT_MAX);
    a.Read(&stream);
    assert(a.size() == 0 && stream.dataReads == 0);
    b.Read(&stream);
    assert(b.size() == 0 && stream.dataReads == 0);
    a.init(1, 31); b.init(1, 1, 37);
    assert(a.get(0) == 31 && b.get(0) == 37);
#endif
}
'''

def checks(bits):
    maximum = (1 << bits) - 1
    cases = set()
    for element in [0, 1, 2, 4, 8, 16, 255, 65536, maximum // 2, maximum - 8, maximum - 7, maximum]:
        counts = [-1, 0, 1, 2, 3, 2147483647]
        if element:
            boundary = (maximum - 8) // element
            counts += [boundary - 1, boundary, boundary + 1]
        for count in counts:
            if -2147483648 <= count <= 2147483647:
                cases.add((count, element))
    lines = ['int main() {']
    for count, element in sorted(cases):
        value = 8 + count * element
        valid = count >= 0 and element > 0 and value <= maximum
        call = 'FStorageAllocationSize(%d, static_cast<ByteSize>(0x%xUL))' % (count, element)
        if valid:
            lines.append('assert(%s == static_cast<ByteSize>(0x%xUL));' % (call, value))
        else:
            lines.append('assert(%s == 0);' % call)
    lines += ['classChecks();', '}']
    return '\n'.join(lines), len(cases)

with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    for simulated, bits in [(False, ctypes.sizeof(ctypes.c_size_t) * 8), (True, 32)]:
        # Same function/body and class callers; only the helper's size type changes.
        # This is an arithmetic stand-in, not a 32-bit compiler/ABI validation.
        h = header.replace('std::size_t', 'unsigned int') if simulated else header
        (tmp / 'FSimpleDataStorage.h').write_text(h)
        main, count = checks(bits)
        alias = 'typedef %s ByteSize;\n' % ('unsigned int' if simulated else 'std::size_t')
        (tmp / 'check.cpp').write_text(prefix + alias + body + main)
        command = ['g++', '-std=c++03', '-fno-exceptions', '-Wall', '-Wextra', '-Werror', '-pedantic',
                   '-fsanitize=address,undefined', '-g', str(tmp / 'check.cpp'), '-o', str(tmp / 'check')]
        if simulated:
            command.insert(1, '-DSIMULATED_32')
        subprocess.run(command, check=True)
        subprocess.run([str(tmp / 'check')], check=True,
                       env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
        print('PASS: %d %s boundary cases and class caller checks; C++03/ASan/UBSan.' %
              (count, 'simulated-32-bit' if simulated else 'native-size_t'))
