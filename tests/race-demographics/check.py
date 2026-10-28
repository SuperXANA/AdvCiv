#!/usr/bin/env python3
"""Actual sampler/accessor/selection methods, plus a structural initialization-scope check.

This is a strict C++03 fixture with engine dependencies stubbed, not a DLL build.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile
root = Path(__file__).resolve().parents[2]
dll = root / 'CvGameCoreDLL'

def function(text, name):
    start = text.index(name)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

player = (dll / 'CvPlayer.cpp').read_text()
plot = (dll / 'CvPlot.cpp').read_text()
unit = (dll / 'CvUnit.cpp').read_text()
info = (dll / 'CvInfo_Civilization.h').read_text()
assert '#include "RaceWeightedRandom.h"' in player and '#include "RaceWeightedRandom.h"' in plot
finalize = function(unit, 'void CvUnit::finalizeInit()')
lexed = re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"', '', finalize, flags=re.S)
call = lexed.index('initRaceType();')
assert lexed.count('initRaceType();') == 1
assert lexed[:call].count('{') - lexed[:call].count('}') == 1, 'Race init is conditional'
world = function(lexed, 'if (m_pUnitInfo->isWorldUnit())')
assert lexed.index(world) + len(world) < call < lexed.index('CvEventReporter::')
race_class = info[info.index('class CvRaceInfo : public CvXMLInfo'):]
enum_start = race_class.index('enum BoolElementTypes')
enum_end = race_class.index('};', enum_start) + 2
typed = race_class[enum_start:enum_end] + '\n' + function(race_class, 'bool get(')
methods = '\n'.join([
    function(player, 'RaceTypes CvPlayer::buildRaceInformationCache('),
    function(plot, 'RaceTypes CvPlot::getDemographicRace('),
    function(unit, 'void CvUnit::initRaceType()'),
])
stub = r'''
#include <cassert>
#include <climits>
#include <stddef.h>
#include <deque>
#include <vector>
#include "RaceWeightedRandom.h"
enum RaceTypes { NO_RACE = -1, RACE_A, RACE_B, RACE_C, NUM_RACES };
typedef int PlayerTypes;
const int NO_PLAYER = -1, CIV_ALIVE = 1, MAX_INT = INT_MAX;
int errors = 0;
#define FErrorMsg(text) (++errors)
struct CvXMLInfo {
    enum IntElementTypes { NUM_INT_ELEMENT_TYPES };
    enum BoolElementTypes { NUM_BOOL_ELEMENT_TYPES };
    bool locked;
    CvXMLInfo() : locked(false) {}
    bool get(BoolElementTypes) const { return locked; }
};
struct CvRaceInfo : CvXMLInfo {
    typedef CvXMLInfo base_t;
ACTUAL_ACCESSOR
};
struct FakeGame {
    std::deque<int> draws;
    std::vector<int> bounds;
    int getSorenRandNum(int bound, char const*) {
        assert(bound > 0 && bound <= 65535 && !draws.empty());
        int result = draws.front(); draws.pop_front();
        assert(result >= 0 && result < bound); bounds.push_back(bound); return result;
    }
    void clear() { draws.clear(); bounds.clear(); }
    void large(unsigned int value) {
        draws.push_back(value / 65536U); draws.push_back((value % 65536U) / 2U);
        draws.push_back(value % 2U);
    }
} game;
struct CvCivilization {
    int weights[NUM_RACES];
    CvCivilization() { for (int i = 0; i < NUM_RACES; ++i) weights[i] = 0; }
    int getRacePriority(int i) const { return weights[i]; }
};
struct CvPlayer {
    CvCivilization civilization;
    int id;
    bool alive;
    RaceTypes visible, ordinary;
    CvPlayer() : id(0), alive(true), visible(RACE_B), ordinary(RACE_A) {}
    CvCivilization const& getCivilization() const { return civilization; }
    RaceTypes buildRaceInformationCache(bool bCultureRoll = false) const;
    int getID() const { return id; }
    RaceTypes getDefaultRace(bool culture = false) const { return culture ? visible : ordinary; }
} players[3];
struct Globals {
    CvRaceInfo races[NUM_RACES];
    FakeGame& getGame() { return game; }
    CvRaceInfo const& getInfo(RaceTypes r) { return races[r]; }
} GC;
#define FOR_EACH_ENUM(Type) for (RaceTypes eLoopRace = RACE_A; eLoopRace < NUM_RACES; eLoopRace = static_cast<RaceTypes>(eLoopRace + 1))
#define GET_PLAYER(id) (players[id])
template<int> struct PlayerIter {
    int index;
    PlayerIter() : index(0) { skip(); }
    void skip() { while (index < 3 && !players[index].alive) ++index; }
    bool hasNext() const { return index < 3; }
    void operator++(int) { ++index; skip(); }
    CvPlayer& operator*() { return players[index]; }
};
struct CvPlot {
    int cultures[3];
    CvPlot() { for (int i = 0; i < 3; ++i) cultures[i] = 0; }
    int countTotalCulture() const { return cultures[0] + cultures[1] + cultures[2]; }
    int getCulture(int i) const { return cultures[i]; }
    RaceTypes getDemographicRace(PlayerTypes eSkipPlayer = NO_PLAYER) const;
};
struct UnitInfo {
    RaceTypes race;
    UnitInfo() : race(NO_RACE) {}
    RaceTypes getDefaultRace() const { return race; }
};
struct CvUnit {
    UnitInfo info;
    UnitInfo* m_pUnitInfo;
    CvPlot at;
    RaceTypes m_eRaceCreationType;
    CvUnit() : m_pUnitInfo(&info), m_eRaceCreationType(NO_RACE) {}
    PlayerTypes getOwner() const { return 0; }
    CvPlot& getPlot() { return at; }
    void initRaceType();
};
'''
checks = r'''
void reset() {
    game.clear(); errors = 0;
    for (int i = 0; i < 3; ++i) { players[i] = CvPlayer(); players[i].id = i; GC.races[i].locked = false; }
}
int main() {
    assert(UINT_MAX == 0xffffffffU && INT_MAX == 2147483647);
    reset(); assert(xanaRace::drawWeightedIndex(game, 0) == -1);
    assert(xanaRace::drawWeightedIndex(game, -1) == -1 && game.bounds.empty());
    int pools[] = { 1, 2, 3, 100, 65535 };
    for (int i = 0; i < 5; ++i) {
        game.clear(); game.draws.push_back(pools[i] - 1);
        assert(xanaRace::drawWeightedIndex(game, pools[i]) == pools[i] - 1);
        assert(game.bounds.size() == 1 && game.bounds[0] == pools[i]);
    }
    int largePools[] = { 65536, 65537, 100000, INT_MAX };
    for (int i = 0; i < 4; ++i) {
        game.clear(); game.large(largePools[i] - 1);
        assert(xanaRace::drawWeightedIndex(game, largePools[i]) == largePools[i] - 1);
        assert(game.bounds.size() == 3 && game.bounds[0] == 32768 && game.bounds[1] == 32768 && game.bounds[2] == 2);
    }
    game.clear(); game.large(0x7fffffffU); game.large(42);
    assert(xanaRace::drawWeightedIndex(game, 65537) == 42 && game.bounds.size() == 6);
    game.clear(); game.large(0x7fffffffU); game.large(INT_MAX - 1);
    assert(xanaRace::drawWeightedIndex(game, INT_MAX) == INT_MAX - 1 && game.bounds.size() == 6);
    game.clear(); game.large(0x7fffffffU); game.large(1073741824U);
    assert(xanaRace::drawWeightedIndex(game, 1073741825) == 1073741824 && game.bounds.size() == 6);
    reset(); CvPlayer& p = players[0];
    p.civilization.weights[0] = 2; p.civilization.weights[1] = 3; p.civilization.weights[2] = 1;
    int counts[3] = { 0, 0, 0 };
    for (int roll = 0; roll < 6; ++roll) { game.draws.push_back(roll); ++counts[p.buildRaceInformationCache()]; }
    assert(counts[0] == 2 && counts[1] == 3 && counts[2] == 1);
    GC.races[1].locked = true; game.draws.push_back(2);
    assert(p.buildRaceInformationCache(true) == RACE_C && game.bounds.back() == 3);
    game.draws.push_back(2); assert(p.buildRaceInformationCache() == RACE_B);
    p.civilization.weights[0] = 50000; p.civilization.weights[1] = 50000; p.civilization.weights[2] = 0;
    game.large(90000); assert(p.buildRaceInformationCache() == RACE_B);
    game.clear(); p.civilization.weights[0] = INT_MAX; p.civilization.weights[1] = 1;
    assert(p.buildRaceInformationCache() == NO_RACE && errors == 1 && game.bounds.empty());
    p.civilization.weights[0] = 0; p.civilization.weights[1] = -1;
    assert(p.buildRaceInformationCache() == NO_RACE && game.bounds.empty());
    reset(); CvPlot at; at.cultures[0] = 60; at.cultures[1] = 30; at.cultures[2] = 10;
    players[2].visible = RACE_C;
    game.draws.push_back(29); assert(at.getDemographicRace(0) == RACE_B);
    game.draws.push_back(30); assert(at.getDemographicRace(0) == RACE_C);
    game.draws.push_back(40); assert(at.getDemographicRace(0) == NO_RACE);
    at.cultures[0] = at.cultures[1] = 70000; at.cultures[2] = 0;
    game.large(69999); assert(at.getDemographicRace(0) == RACE_B);
    game.large(70000); assert(at.getDemographicRace(0) == NO_RACE);
    reset(); CvUnit unit; unit.info.race = RACE_C; unit.initRaceType();
    assert(unit.m_eRaceCreationType == RACE_C && game.bounds.empty());
    unit.info.race = NO_RACE; unit.at.cultures[1] = 1; game.draws.push_back(0); unit.initRaceType();
    assert(unit.m_eRaceCreationType == RACE_B);
    unit.at.cultures[1] = 0; unit.initRaceType(); assert(unit.m_eRaceCreationType == RACE_A);
    assert(game.draws.empty());
}
'''
with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    (temp / 'RaceWeightedRandom.h').write_text((dll / 'RaceWeightedRandom.h').read_text())
    cpp, binary = temp / 'race.cpp', temp / 'race'
    cpp.write_text(stub.replace('ACTUAL_ACCESSOR', typed) + '\n' + methods + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('C++03 + ASan/UBSan passed; actual weighted methods/accessor; unconditional finalizeInit scope checked')
