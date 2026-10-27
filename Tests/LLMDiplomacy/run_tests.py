#!/usr/bin/env python3
"""Compile the actual diplomacy sources against small, instrumented Linux stubs."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def extract_block(path):
    marker = '// XANA: 05-23-2026 LLM Text Diplomacy Generation'
    text = path.read_text()
    start = text.index(marker)
    end = text.index(marker, start + len(marker)) + len(marker)
    return text[start:end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='enable ASan/UBSan; leak detection is disabled for ptrace hosts')
    args = parser.parse_args()
    tests = Path(__file__).resolve().parent
    repo = tests.parents[1]
    source = repo / 'CvGameCoreDLL'
    with tempfile.TemporaryDirectory(prefix='llm-diplo-tests-') as folder:
        work = Path(folder)
        for path in (tests / 'stubs').iterdir():
            shutil.copy2(path, work / path.name)
        for filename in ['CvDynamicDiploManager.h', 'CvDynamicDiploManager.cpp', 'CvCriticalSectionMutex.h']:
            shutil.copy2(source / filename, work / filename)
        (work / 'CvStructs.h').write_text('#ifndef TEST_STRUCTS_H\n#define TEST_STRUCTS_H\n#include "CvGameCoreDLL.h"\n' + extract_block(source / 'CvStructs.h') + '#endif\n')
        (work / 'CvStructs.cpp').write_text('#include "CvGameCoreDLL.h"\n#include "CvStructs.h"\n' + extract_block(source / 'CvStructs.cpp'))
        compiler = os.environ.get('CXX', 'g++')
        flags = ['-std=c++03', '-pedantic-errors', '-Wall', '-Wextra', '-pthread', '-I.', '-g']
        env = dict(os.environ)
        if args.sanitize:
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
            env['ASAN_OPTIONS'] = 'detect_leaks=0'
            print('ASan/UBSan enabled; LeakSanitizer is excluded on ptrace hosts.', flush=True)
        for name, sources in [('struct_test', ['CvStructs.cpp']), ('manager_test', ['CvStructs.cpp', 'CvDynamicDiploManager.cpp'])]:
            shutil.copy2(tests / (name + '.cpp'), work / (name + '.cpp'))
            subprocess.run([compiler] + flags + sources + [name + '.cpp', '-o', name], cwd=work, check=True)
            subprocess.run([str(work / name)], cwd=work, env=env, check=True)
        subprocess.run([sys.executable, str(tests / 'test_python.py'), str(repo)], check=True)
    print('All local regression tests passed. This does not validate the Civ4 DLL or multiplayer lockstep.', flush=True)


if __name__ == '__main__':
    main()
