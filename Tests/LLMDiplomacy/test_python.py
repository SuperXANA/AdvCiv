"""Parse the Python 2 module and execute its actual display-filter method with stubs."""
import sys
import types
import warnings
from pathlib import Path
warnings.filterwarnings('ignore', category=DeprecationWarning)
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

class Rand:
    def __init__(self): self.calls = 0
    def get(self, n, tag): self.calls += 1; return 0
rand = Rand()
player = types.SimpleNamespace(AI_getAttitude=lambda i: 0, getCivilizationType=lambda: 0, getLeaderType=lambda: 0, getPower=lambda: 10)
gc = types.SimpleNamespace(getPlayer=lambda i: player, getActivePlayer=lambda: player, getASyncRand=lambda: rand, getNumCivilizationInfos=lambda: 1, getNumLeaderHeadInfos=lambda: 1)
cv = types.ModuleType('CvPythonExtensions')
cv.CyGlobalContext = lambda: gc
cv.CyGame = lambda: types.SimpleNamespace(getActivePlayer=lambda: 3)
cv.CyDiplomacy = lambda: None
cv.AttitudeTypes = types.SimpleNamespace(NUM_ATTITUDE_TYPES=1)
cv.DiplomacyPowerTypes = types.SimpleNamespace(NUM_DIPLOMACYPOWER_TYPES=1)
cv.true, cv.false = True, False
sys.modules['CvPythonExtensions'] = cv
sys.modules['CvUtil'] = types.ModuleType('CvUtil')
ph = types.ModuleType('PyHelpers'); ph.PyPlayer = object
sys.modules['PyHelpers'] = ph
source = (Path(sys.argv[1]) / 'Python/CvDiplomacy.py').read_text()
converted = str(RefactoringTool(get_fixers_from_package('lib2to3.fixes')).refactor_string(source, 'CvDiplomacy.py'))
namespace = {}
exec(compile(converted, 'CvDiplomacy.py', 'exec'), namespace)
obj = namespace['CvDiplomacy'].__new__(namespace['CvDiplomacy'])
obj.iLastResponseID = 12
obj.diploScreen = types.SimpleNamespace(getWhoTradingWith=lambda: 7)

class Info:
    def __init__(self, kind, text): self.kind, self.text, self.calls = kind, text, []
    def getType(self): return self.kind
    def getDynamicDiplomacyTextForPlayers(self, *args): self.calls.append(args); return self.text
    def getNumResponses(self): return 1
    def getAttitudeTypes(self, *args): return False
    getCivilizationTypes = getLeaderHeadTypes = getDiplomacyPowerTypes = getAttitudeTypes
    def getNumDiplomacyText(self, i): return 1
    def getDiplomacyText(self, i, j): return 'XML fallback'

ai = Info('AI_DIPLOCOMMENT_FIRST_CONTACT', 'Generated greeting')
assert obj.filterUserResponse(ai) == 'Generated greeting'
assert ai.calls == [(7, 3)] and obj.iLastResponseID == -1 and rand.calls == 0
empty = Info('AI_DIPLOCOMMENT_DECLARE_WAR', '')
assert obj.filterUserResponse(empty) == 'XML fallback'
assert empty.calls == [(7, 3)] and rand.calls == 1
user = Info('USER_DIPLOCOMMENT_WAR', 'Generated button text')
assert obj.filterUserResponse(user) == 'XML fallback'
assert not user.calls and rand.calls == 2
obj.diploScreen = types.SimpleNamespace(getWhoTradingWith=lambda: -1)
assert obj.filterUserResponse(ai) == '' and ai.calls == [(7, 3)]
print('PASS Python 2 grammar, single AI getter with integer IDs, XML fallback, authored user buttons, absent contact')
