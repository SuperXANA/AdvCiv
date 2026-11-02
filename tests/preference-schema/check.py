"""Check schema names/cardinality against actual loaders; not an MSXML/XDR execution."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
UNITS = ROOT / 'XML/Units/CIV4UnitSchema.xml'
EVENTS = ROOT / 'XML/Events/CIV4EventSchema.xml'
TECHS = ROOT / 'XML/Civilizations/CIV4CivilizationsSchema.xml'

def models(text):
    tree = ET.fromstring(text)
    declarations = tree.findall('{*}ElementType')
    names = [e.attrib['name'] for e in declarations]
    assert len(names) == len(set(names)), 'duplicate ElementType'
    missing = {e.attrib['type'] for e in tree.findall('.//{*}element')} - set(names)
    assert not missing, 'undefined element types: ' + str(sorted(missing))
    return {e.attrib['name']: e for e in declarations}

def child_names(model):
    return [e.attrib['type'] for e in model.findall('{*}element')]

def validate(unit_text, event_text, tech_text):
    unit, event, tech = [models(t) for t in (unit_text, event_text, tech_text)]
    loader = (ROOT / 'CvGameCoreDLL/CvXMLLoadUtilitySet.cpp').read_text()
    for kind, schema, folder in [('Unit', unit, 'Units'), ('Event', event, 'Events'), ('Tech', tech, 'Civilizations')]:
        match = re.search(r'LoadGlobalClassInfo\(GC\.m_pa' + kind + r'PreferenceInfo, "([^"]+)", "([^"]+)", "([^"]+)"', loader)
        assert match and match.group(2) == folder
        parts = match.group(3).split('/')
        assert parts[0] in schema, 'loader root missing: ' + parts[0]
        for parent, child in zip(parts, parts[1:]):
            assert child in child_names(schema[parent]), (parent, child)
        owner_tags = ('Leader', 'Civilization') if kind == 'Event' else ('LeaderType', 'CivilizationType')
        children = {e.attrib['type']: e for e in schema[kind + 'PreferenceInfo'].findall('{*}element')}
        for tag in owner_tags:
            assert tag in children and children[tag].get('minOccurs') == '0', 'optional owner: ' + tag
    unit_cpp = (ROOT / 'CvGameCoreDLL/CvInfo_Unit.cpp').read_text()
    structs = (ROOT / 'CvGameCoreDLL/CvXMLStructs.cpp').read_text()
    info = unit['UnitPreferenceInfo']
    children = {e.attrib['type']: e for e in info.findall('{*}element')}
    for kind in ('UnitCombat', 'UnitClass', 'Unit'):
        list_name = kind + 'Preferences'
        record = kind + 'Preference'
        assert '"' + list_name + '"' in unit_cpp
        assert list_name in children and children[list_name].get('minOccurs') == '0', 'optional list: ' + list_name
        assert child_names(unit[list_name]) == [record]
    for kind, schema in [('Tech', tech), ('Event', event), ('UnitCombat', unit), ('UnitClass', unit), ('Unit', unit)]:
        record = kind + 'Preference'
        method = re.search(r'bool ' + record + r'Data::read\([^)]*\)\s*\{([\s\S]*?)\n\}', structs).group(1)
        key = re.search(r'readPreferenceInfoID<[^>]+>\([^\n]*?"([^"\n]+)"', method).group(1)
        fields = [key] + re.findall(r'GetChildXmlValByName\([^\n]*?"([^"\n]+)"', method)
        assert child_names(schema[record]) == fields, (record, fields)
    # The actual authored technology sample has one owner field per profile.
    xml = ET.fromstring((ROOT / 'XML/Civilizations/CIV4TechPreferenceInfos.xml').read_text())
    assert xml.tag.rsplit('}', 1)[-1] == 'Civ4TechPreferenceInfos'
    rows = xml.findall('.//{*}TechPreferenceInfo')
    assert len(rows) == 2
    for row in rows:
        present = {e.tag.rsplit('}', 1)[-1] for e in row}
        assert ('LeaderType' in present) != ('CivilizationType' in present)

texts = [p.read_text() for p in (UNITS, EVENTS, TECHS)]
validate(*texts)
controls = []
for index, kind in enumerate(('Unit', 'Event', 'Tech')):
    broken = list(texts)
    broken[index] = broken[index].replace('Civ4' + kind + 'PreferenceInfos', 'Civ4' + kind + 'PerferenceInfos')
    controls.append((kind + ' root spelling', broken))
controls.append(('unit owner spelling', [texts[0].replace('name="LeaderType"', 'name="Leader"').replace('type="LeaderType"', 'type="Leader"')] + texts[1:]))
controls.append(('unit record key', [texts[0].replace('type="UnitType"', 'type="Unit"')] + texts[1:]))
controls.append(('missing unit-class list', [texts[0].replace('<element type="UnitClassPreferences" minOccurs="0"/>', '')] + texts[1:]))
controls.append(('required technology owner', texts[:2] + [texts[2].replace('<element type="LeaderType" minOccurs="0"/>', '<element type="LeaderType"/>')]))
for name, broken in controls:
    try:
        validate(*broken)
    except AssertionError:
        continue
    raise AssertionError('negative control not detected: ' + name)
print('Three schemas, five record contracts and authored technology profiles checked; seven negative controls detected.')
