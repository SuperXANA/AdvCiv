#!/usr/bin/env python3
"""Run the unchanged Python filter with fake game objects; check bindings/schema."""
from pathlib import Path
from types import SimpleNamespace
import re
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parents[2]
source = (root / 'Assets/Python/CvDiplomacy.py').read_text()
methods = []
for name in ['setLastResponseID', 'getLastResponseID', 'isUsed', 'filterUserResponse']:
    start = source.index('\tdef ' + name + '(')
    end = source.find('\n\tdef ', start + 1)
    methods.append(source[start:end if end != -1 else len(source)])
class Player:
    def __init__(self, civ, leader):
        self.civ, self.leader = civ, leader
    def getCivilizationType(self): return self.civ
    def getLeaderType(self): return self.leader
    def AI_getAttitude(self, player): return 1
    def getPower(self): return 100
class Random:
    def __init__(self): self.calls = []
    def get(self, n, label):
        assert n > 0
        self.calls.append((n, label))
        return 0
class Globals:
    def __init__(self):
        self.ours, self.theirs = Player(1, 3), Player(2, 0)
        self.random = Random()
    def getPlayer(self, player): return self.theirs
    def getActivePlayer(self): return self.ours
    def getNumCivilizationInfos(self): return 3
    def getNumLeaderHeadInfos(self): return 4
    def getASyncRand(self): return self.random
gc = Globals()
env = dict(gc=gc, true=True, false=False,
           AttitudeTypes=SimpleNamespace(NUM_ATTITUDE_TYPES=3),
           DiplomacyPowerTypes=SimpleNamespace(NUM_DIPLOMACYPOWER_TYPES=3,
               DIPLOMACYPOWER_STRONGER=0, DIPLOMACYPOWER_WEAKER=1, DIPLOMACYPOWER_EQUAL=2),
           CyGame=lambda: SimpleNamespace(getActivePlayer=lambda: 0))
exec('class Filter:\n' + '\n'.join(methods), env)
f = env['Filter']()
f.diploScreen = SimpleNamespace(getWhoTradingWith=lambda: 1)
class Info:
    def __init__(self, rows): self.rows = rows
    def getNumResponses(self): return len(self.rows)
    def getNumDiplomacyText(self, row): return 1
    def getDiplomacyText(self, row, item): return self.rows[row]['text']
    def __getattr__(self, name):
        if name.startswith('get'):
            return lambda row, value: value in self.rows[row].get(name[3:], ())
        raise AttributeError(name)
def pick(**conditions):
    return f.filterUserResponse(Info([dict(text='match', **conditions)]))
assert pick() == 'match'
for field, yes, no in [('CivilizationTypes', 2, 1), ('LeaderHeadTypes', 0, 3),
                      ('OtherCivilizationTypes', 1, 2), ('OtherLeaderHeadTypes', 3, 0)]:
    assert pick(**{field: [yes]}) == 'match'
    assert pick(**{field: [no]}) == ''
for field, banned, allowed in [('OtherNotCivilizationTypes', 1, 2), ('OtherNotLeaderHeadTypes', 3, 0)]:
    assert pick(**{field: [banned]}) == ''
    assert pick(**{field: [allowed]}) == 'match'
assert pick(CivilizationTypes=[2], LeaderHeadTypes=[0], OtherCivilizationTypes=[1], OtherLeaderHeadTypes=[3]) == 'match'
assert pick(OtherLeaderHeadTypes=[3], OtherNotLeaderHeadTypes=[3]) == ''
assert pick(OtherCivilizationTypes=[1], OtherNotCivilizationTypes=[1]) == ''
assert pick(AttitudeTypes=[1], DiplomacyPowerTypes=[2], OtherLeaderHeadTypes=[3]) == 'match'
assert pick(AttitudeTypes=[0], OtherLeaderHeadTypes=[3]) == ''
assert pick(DiplomacyPowerTypes=[0], OtherLeaderHeadTypes=[3]) == ''
rows = [dict(text='wrong', OtherLeaderHeadTypes=[0]), dict(text='right', OtherLeaderHeadTypes=[3])]
assert f.filterUserResponse(Info(rows)) == 'right'
before = len(gc.random.calls)
assert pick(OtherLeaderHeadTypes=[0]) == '' and len(gc.random.calls) == before
f.diploScreen = SimpleNamespace(getWhoTradingWith=lambda: -1)
assert pick() == '' and len(gc.random.calls) == before
bindings = (root / 'CvGameCoreDLL/CyInfoInterface3.cpp').read_text()
fields = ['OtherCivilizationTypes', 'OtherNotCivilizationTypes', 'OtherLeaderHeadTypes', 'OtherNotLeaderHeadTypes']
for cls in ['CvDiplomacyTextInfo', 'CvDiplomacyInfo']:
    for field in fields:
        expected = '.def("get%s", &%s::get%s,' % (field, cls, field)
        assert bindings.count(expected) == 1
assert '&CvEventTriggerInfo::getReligionRequired' in bindings
assert '&CvEventTriggerInfo::isPickOtherPlayerCity' in bindings
assert '&CvEventInfo::getNumUnits' in bindings
schema = ET.parse(root / 'Assets/XML/GameInfo/CIV4GameInfoSchema.xml')
types = {e.attrib['name']: e for e in schema.getroot() if e.tag.rsplit('}', 1)[-1] == 'ElementType'}
new_tags = ['OtherCivilizations', 'OtherNotCivilizations', 'OtherLeaders', 'OtherNotLeaders']
response = types['Response']
refs = {e.attrib.get('type'): e.attrib for e in response}
for tag in new_tags:
    assert tag in types and refs[tag].get('minOccurs') == '0'
example = ET.parse(Path(__file__).with_name('source-response.xml')).getroot()
assert example.find('Leaders/Leader/LeaderType').text == 'LEADER_CELESTIA'
assert example.find('OtherLeaders/Leader/LeaderType').text == 'LEADER_SOMBRA'
print('Actual Python response filter, eight bindings, optional schema fields and inactive source example passed')
