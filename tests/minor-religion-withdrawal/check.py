#!/usr/bin/env python3
"""Run production city methods and lifecycle slices in a C++03 engine stand-in.

This is not a DLL or game save test. See the adjacent fixture for the mocked
engine interfaces; initialization/turn/stream slices are extracted, not copied.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
directory = Path(os.environ.get('WITHDRAWAL_SOURCE_DIR', root / 'CvGameCoreDLL'))
city = (directory / 'CvCity.cpp').read_text()
header = (directory / 'CvCity.h').read_text()
text = (directory / 'CvGameTextMgr.cpp').read_text()


def method(source, signature):
    start = source.index(signature)
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def through(source, start, end):
    a = source.index(start)
    b = source.index(end, a) + len(end)
    return source[a:b]


constructor = method(city, 'CvCity::CvCity()')
turn = method(city, 'void CvCity::doTurn()')
reader = method(city, 'void CvCity::read(')
writer = method(city, 'void CvCity::write(')
members = ['m_iHurryAngerTimer', 'm_iConscriptAngerTimer',
           'm_iDefyResolutionAngerTimer', 'm_iHappinessTimer',
           'm_iUnhappinessTimer', 'm_iMilitaryHappinessUnits']
declarations = []
for name in members:
    declarations.append(re.search(r'\bint ' + name + r';', header).group())
for name in ['getHappinessTimer', 'getUnhappinessTimer']:
    declarations.append(re.search(r'\bint ' + name + r'\(\) const \{[^}]+\}', header).group())
for name in ['changeHappinessTimer', 'changeUnhappinessTimer', 'getTemporaryUnhappiness']:
    declarations.append(re.search(r'\b(?:void|int) ' + name + r'\([^;]*;', header).group())

# Keep the actual order through production, timer expiry and the religion update.
# A missing, duplicated or relocated expiry must fail instead of silently testing
# an extracted copy that the live city no longer uses.
turn_slice = through(turn, 'doProduction(!bForceProduction);', 'doReligion();')
assert turn.count('changeUnhappinessTimer(-1)') == 1
assert 'changeUnhappinessTimer(-1)' in turn_slice

methods = '\n'.join(method(city, signature) for signature in [
    'void CvCity::changeHappinessTimer(',
    'void CvCity::changeUnhappinessTimer(',
    'int CvCity::getTemporaryUnhappiness(',
    'int CvCity::unhappyLevel(',
    'int CvCity::happyLevel(',
    'void CvCity::setCityChangesDueToMinorReligionJoining(',
    'void CvCity::setCityChangesDueToMinorReligionLeaving('])
values = {
    'DECLARATIONS': '\n'.join(declarations),
    'INITIALIZATION': '\n'.join(re.search(r'\b' + name + r' = 0;', constructor).group()
                               for name in members),
    'TURN': turn_slice,
    'READ': through(reader, 'uint uiFlag=0;', 'pStream->Read(&uiFlag);') + '\n' +
            through(reader, 'pStream->Read(&m_iHappinessTimer);',
                    'pStream->Read(&m_iMilitaryHappinessUnits);'),
    'WRITE': through(writer, 'uint uiFlag;', 'pStream->Write(uiFlag);') + '\n' +
             through(writer, 'pStream->Write(m_iHappinessTimer);',
                     'pStream->Write(m_iMilitaryHappinessUnits);'),
    'METHODS': methods,
    'ANGER_HELP': method(text, 'void CvGameTextMgr::setAngerHelp('),
}

fixture = Path(__file__).with_name('check.cpp').read_text()
for key, value in values.items():
    fixture = fixture.replace('@' + key + '@', value)
assert not re.search(r'@[A-Z_]+@', fixture)

# The new tooltip must ship with the key and both runtime formatting arguments.
xml = ET.parse(root / 'Assets/XML/Text/CIV4GameText_MinorReligion_mlp.xml')
entry = [e for e in xml.getroot().findall('TEXT')
         if e.findtext('Tag') == 'TXT_KEY_ANGER_MINOR_RELIGION_WITHDRAWAL']
assert len(entry) == 1
assert '%d1' in entry[0].findtext('English') and '%d2' in entry[0].findtext('English')

with tempfile.TemporaryDirectory() as directory:
    p = Path(directory)
    (p / 'check.cpp').write_text(fixture)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-g', str(p / 'check.cpp'),
                    '-o', str(p / 'check')], check=True)
    # happyLevel caches TEMP_HAPPY, so each configured value needs a fresh process.
    for magnitude in range(4):
        subprocess.run([str(p / 'check'), str(magnitude)], check=True, env=dict(os.environ,
                       ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
