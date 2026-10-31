#!/usr/bin/env python3
"""Check actual UWAI installation paths, XDR declarations and registration order.

This is source/XML structural validation, not execution of Civ4's XML parser.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
loader = (root / 'CvGameCoreDLL/CvXMLLoadUtilitySet.cpp').read_text()
pattern = r'LoadGlobalClassInfo\(GC\.m_paWarUtilityAspectAIInfo,\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"'
calls = list(re.finditer(pattern, loader))
assert len(calls) == 1
call = calls[0]
file_root, directory, xpath = call.groups()
leader = loader.index('LoadGlobalClassInfo(GC.m_paLeaderHeadInfo,')
assert call.start() < leader, 'Aspect type IDs/count must exist before leader XML/cache reads'
path = root / 'Assets/XML' / directory / (file_root + '.xml')
assert path.is_file(), 'Aspect XML must exist at the actual loader path'
document = ET.parse(path).getroot()
namespace = document.tag.split('}')[0][1:]
assert namespace.startswith('x-schema:')
schema_path = path.parent / namespace[len('x-schema:'):]
schema = ET.parse(schema_path).getroot()
xdr = {'x': 'urn:schemas-microsoft-com:xml-data'}
declarations = {e.attrib['name']: e for e in schema.findall('x:ElementType', xdr)}
parts = xpath.split('/')
assert document.tag.split('}')[-1] == parts[0]
for parent, child in zip(parts, parts[1:]):
    declaration = declarations[parent]
    assert child in [e.attrib['type'] for e in declaration.findall('x:element', xdr)]
for key in ['Type', 'Description', 'iAIWeight']:
    assert key in declarations
    assert key in [e.attrib['type'] for e in declarations[parts[-1]].findall('x:element', xdr)]
rows = document.findall('.//{%s}%s' % (namespace, parts[-1]))
types = [row.find('{%s}Type' % namespace).text for row in rows]
assert len(types) == 29 and len(set(types)) == 29
for row in rows:
    assert int(row.find('{%s}iAIWeight' % namespace).text) == 100
    assert row.find('{%s}Description' % namespace).text
aspect = (root / 'CvGameCoreDLL/WarUtilityAspect.h').read_text()
keys = re.findall(r'getInfoTypeForString\("(WARUTILITYASPECTAI_[^"]+)"\)', aspect)
assert len(keys) == 29 and set(keys) == set(types)
assert not (root / 'Assets/XML/GameInfos/CIV4WarUtilityAspectAIInfos.xml').exists()
print('PASS: actual loader path/order, colocated XDR schema and all 29 aspect keys/defaults')
