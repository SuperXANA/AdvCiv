#!/usr/bin/env python3
"""Complete header with non-raising elements and deterministic allocation failure."""
from pathlib import Path
import os
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
header = (root / 'CvGameCoreDLL/FSimpleDataStorage.h').read_text()
fixture = Path(__file__).with_suffix('.cpp').read_text()
assert not re.search(r'\b(?:try|catch|throw)\b', header)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1')
mutants = [
    ('invalid-byte-success', header.replace('return 0;', 'return 8;', 1)),
    ('copy-null-write', header.replace('m_pArray != NULL && i < kOther.size()', 'i < kOther.size()')),
    ('lost-raw-owner', header.replace('reset(iSize);\n\t\tif (m_pArray == NULL) return;', 'reset(iSize);')),
    ('lost-local-staging', header.replace('load(tempArray, iSize);\n\t\tSAFE_DELETE_ARRAY(tempArray);', 'load(tempArray, iSize);')),
]
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    (tmp / 'check.cpp').write_text(fixture)
    for name, source in [('positive', header)] + mutants:
        (tmp / 'FSimpleDataStorage.h').write_text(source)
        command = ['g++', '-std=c++03', '-fno-exceptions', '-Wall', '-Wextra', '-Werror', '-pedantic',
                   '-fsanitize=address,undefined', '-g', '-I' + str(tmp), str(tmp / 'check.cpp'),
                   '-Wl,--wrap=_ZnamRKSt9nothrow_t', '-o', str(tmp / 'check')]
        subprocess.run(command, check=True)
        result = subprocess.run([str(tmp / 'check')], env=env, capture_output=True, text=True)
        if name == 'positive':
            assert result.returncode == 0, result.stderr
            print(result.stdout.strip())
        else:
            assert source != header and result.returncode != 0, name
            print('Negative control detected: ' + name)
