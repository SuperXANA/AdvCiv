#!/usr/bin/env python3
"""Test actual discovery code with a simulated Win32 reader; this is not a DLL test."""
from pathlib import Path
import os
import subprocess
import tempfile
root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/SelfMod.cpp').read_text()
header = (root / 'CvGameCoreDLL/SelfMod.h').read_text()
locator = source[source.index('class SidSaysLocator'):]
locator = locator[:locator.index('// XANA:')]
entry = source[source.index('void Civ4BeyondSwordPatches::patchSidSays()'):]
stub = r'''
#include <algorithm>
#include <cassert>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <stdint.h>
typedef unsigned char byte;
typedef uint32_t DWORD;
typedef int32_t LONG;
typedef size_t SIZE_T;
struct IMAGE_DOS_HEADER { uint16_t e_magic; byte unused[58]; LONG e_lfanew; };
struct IMAGE_FILE_HEADER {
    uint16_t Machine, NumberOfSections;
    DWORD TimeDateStamp, PointerToSymbolTable, NumberOfSymbols;
    uint16_t SizeOfOptionalHeader, Characteristics;
};
struct IMAGE_OPTIONAL_HEADER32 {
    uint16_t Magic; byte unused[54];
    DWORD SizeOfImage, SizeOfHeaders, CheckSum; byte tail[156];
};
struct IMAGE_NT_HEADERS32 {
    DWORD Signature; IMAGE_FILE_HEADER FileHeader; IMAGE_OPTIONAL_HEADER32 OptionalHeader;
};
struct IMAGE_SECTION_HEADER {
    byte Name[8]; union { DWORD PhysicalAddress, VirtualSize; } Misc;
    DWORD VirtualAddress, SizeOfRawData, PointerToRawData, PointerToRelocations, PointerToLinenumbers;
    uint16_t NumberOfRelocations, NumberOfLinenumbers; DWORD Characteristics;
};
const uint16_t IMAGE_DOS_SIGNATURE = 0x5A4D, IMAGE_FILE_MACHINE_I386 = 0x14C,
    IMAGE_NT_OPTIONAL_HDR32_MAGIC = 0x10B;
const DWORD IMAGE_NT_SIGNATURE = 0x4550, IMAGE_SCN_CNT_INITIALIZED_DATA = 0x40,
    IMAGE_SCN_MEM_READ = 0x40000000, IMAGE_SCN_MEM_WRITE = 0x80000000,
    IMAGE_SCN_MEM_EXECUTE = 0x20000000, IMAGE_SCN_MEM_DISCARDABLE = 0x02000000;
struct CvString : std::string {
    void Format(char const* fmt, ...) {
        char buffer[2048]; va_list args; va_start(args, fmt);
        vsnprintf(buffer, sizeof(buffer), fmt, args); va_end(args); assign(buffer);
    }
};
typedef std::string CvWString;
struct FakeDLL {
    std::vector<std::string> logs;
    void logMsg(char const*, char const* text, bool, bool) { logs.push_back(text); }
} fakeDLL;
FakeDLL* gDLL = &fakeDLL;
struct FakeGC { bool disabled; bool getDefineBOOL(char const*) { return disabled; } } GC;
std::vector<byte> image;
size_t reads = 0, deniedStart = 0, deniedEnd = 0;
bool noModule = false;
void* GetModuleHandle(void*) { return noModule ? NULL : &image[0]; }
void* GetCurrentProcess() { return NULL; }
int ReadProcessMemory(void*, void const* address, void* out, size_t bytes, SIZE_T* copied) {
    ++reads;
    size_t base = reinterpret_cast<size_t>(&image[0]), pos = reinterpret_cast<size_t>(address);
    *copied = 0;
    if (pos < base || pos - base > image.size() || bytes > image.size() - (pos - base)) return 0;
    size_t offset = pos - base;
    if (deniedEnd && offset < deniedEnd && offset + bytes > deniedStart) return 0;
    memcpy(out, &image[offset], bytes); *copied = bytes; return 1;
}
'''
checks = r'''
std::vector<std::string> playerErrors;
void Civ4BeyondSwordPatches::showErrorMsgToPlayer(CvWString msg) { playerErrors.push_back(msg); }
void put(size_t offset, void const* data, size_t size) {
    assert(offset + size <= image.size()); memcpy(&image[offset], data, size);
}
void label(size_t offset, char const* text, bool wide = false) {
    for (size_t i = 0; i <= strlen(text); ++i) {
        image[offset + (wide ? 2 * i : i)] = text[i];
        if (wide) image[offset + 2 * i + 1] = 0;
    }
}
void setup() {
    image.assign(0x8000, 0xCC); fakeDLL.logs.clear(); playerErrors.clear();
    reads = deniedStart = deniedEnd = 0; noModule = false; GC.disabled = false;
    IMAGE_DOS_HEADER dos = {}; dos.e_magic = IMAGE_DOS_SIGNATURE; dos.e_lfanew = 0x80;
    put(0, &dos, sizeof(dos));
    IMAGE_NT_HEADERS32 nt = {}; nt.Signature = IMAGE_NT_SIGNATURE;
    nt.FileHeader.Machine = IMAGE_FILE_MACHINE_I386; nt.FileHeader.NumberOfSections = 4;
    nt.FileHeader.SizeOfOptionalHeader = sizeof(IMAGE_OPTIONAL_HEADER32);
    nt.OptionalHeader.Magic = IMAGE_NT_OPTIONAL_HDR32_MAGIC; nt.OptionalHeader.SizeOfImage = 0x7000;
    put(0x80, &nt, sizeof(nt));
    for (unsigned int i = 0; i < 4; ++i) {
        IMAGE_SECTION_HEADER s = {};
        s.VirtualAddress = i == 0 ? 0x1000 : 0x3000 + i * 0x1000;
        s.Misc.VirtualSize = i == 0 ? 9000 : 256;
        s.Characteristics = IMAGE_SCN_CNT_INITIALIZED_DATA | IMAGE_SCN_MEM_READ;
        if (i == 1) s.Characteristics |= IMAGE_SCN_MEM_WRITE;
        if (i == 2) s.Characteristics |= IMAGE_SCN_MEM_EXECUTE;
        if (i == 3) s.Characteristics |= IMAGE_SCN_MEM_DISCARDABLE;
        put(0x80 + sizeof(nt) + i * sizeof(s), &s, sizeof(s));
    }
    label(0x1000 + 20, "Sid Says:");
    label(0x1000 + 4088, "Sid's Tips", true);
    label(0x1000 + 8200, "Sid's Tips");
    label(0x1000 + 200, "Sid Says:extended");
    label(0x4000, "Sid Says:"); label(0x5000, "Sid Says:");
    label(0x6000, "Sid Says:"); label(0x7100, "Sid Says:");
}
size_t count(char const* text) {
    size_t n = 0;
    for (size_t i = 0; i < fakeDLL.logs.size(); ++i)
        if (fakeDLL.logs[i].find(text) != std::string::npos) ++n;
    return n;
}
int main() {
    assert(sizeof(IMAGE_DOS_HEADER) == 64 && sizeof(IMAGE_FILE_HEADER) == 20);
    assert(sizeof(IMAGE_NT_HEADERS32) == 248 && sizeof(IMAGE_SECTION_HEADER) == 40);
    setup(); std::vector<byte> before = image;
    SidSaysLocator locator; assert(locator.inspect()); assert(image == before);
    assert(count("Candidate RVA=") == 3 && count("RVA=00001FF8") == 1);
    assert(count("encoding=UTF-16LE") == 1 && count("candidates=3 unreadableBlocks=0") == 1);
    fakeDLL.logs.clear(); assert(locator.inspect()); assert(count("Candidate RVA=") == 3);
    setup(); deniedStart = 0x2000; deniedEnd = 0x2100; before = image;
    assert(!SidSaysLocator().inspect()); assert(image == before && count("unreadableBlocks=2") == 1);
    setup(); image[0] = 0; assert(!SidSaysLocator().inspect()); assert(count("Candidate RVA=") == 0);
    setup(); noModule = true; assert(!SidSaysLocator().inspect()); assert(reads == 0);
    setup(); DWORD huge = 0x7fffffff; put(60, &huge, sizeof(huge));
    assert(!SidSaysLocator().inspect()); assert(reads == 1);
    setup(); IMAGE_SECTION_HEADER bad = {}; bad.VirtualAddress = 0x6fff; bad.Misc.VirtualSize = 256;
    bad.Characteristics = IMAGE_SCN_CNT_INITIALIZED_DATA | IMAGE_SCN_MEM_READ;
    put(0x80 + sizeof(IMAGE_NT_HEADERS32), &bad, sizeof(bad));
    assert(!SidSaysLocator().inspect());
    setup();
    for (size_t i = 0; i < 200; ++i) label(0x1000 + 20 * i, "Sid Says:");
    assert(SidSaysLocator().inspect()); assert(count("Candidate RVA=") == 128);
    setup(); Civ4BeyondSwordPatches patches; GC.disabled = true;
    patches.patchSidSays(); assert(!patches.isSidSaysPatched() && reads == 0 && fakeDLL.logs.empty());
    GC.disabled = false; before = image; patches.patchSidSays();
    assert(!patches.isSidSaysPatched() && image == before && playerErrors.size() == 1);
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp, binary = Path(directory) / 'discovery.cpp', Path(directory) / 'discovery'
    cpp.write_text(stub + '\n' + header.replace('#pragma once', '') + '\n' + locator + '\n' + entry + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('Actual locator and entry: C++03 + ASan/UBSan passed; image bytes unchanged')
