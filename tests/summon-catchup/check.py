#!/usr/bin/env python3
"""Actual catch-up and era-median helpers with game/team/RNG dependencies stubbed."""
from pathlib import Path
import os
import subprocess
import tempfile
root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvPlayer.cpp').read_text()

def function(signature):
    start = source.index(signature)
    opening, depth = source.index('{', start), 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

methods = '\n'.join(function(s) for s in [
    'void doWorldTechDiffusionForSummonedPlayer(',
    'EraTypes calculateMedianEraOfMajorCivs('])
stub = r'''
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <deque>
#include <utility>
#include <vector>
typedef int PlayerTypes;
typedef int TeamTypes;
const int NO_PLAYER = -1, ALIVE = 0, MAJOR_CIV = 1, TECH_COUNT = 8;
enum TechTypes { NO_TECH = -1, TECH_0, TECH_1, TECH_2, TECH_3, TECH_4, TECH_5, TECH_6, TECH_7 };
enum EraTypes { NO_ERA = -1, ERA_0, ERA_1, ERA_2, ERA_3, ERA_4, ERA_5, ERA_6, ERA_7, ERA_8, ERA_9 };
template<class T> struct enum_traits;
template<> struct enum_traits<EraTypes> { static EraTypes const first = ERA_0; };
struct CvTechInfo {
    std::vector<int> ands, ors;
    int getNumAndTechPrereqs() const { return ands.size(); }
    int getNumOrTechPrereqs() const { return ors.size(); }
    int getPrereqAndTechs(int i) const { return ands[i]; }
    int getPrereqOrTechs(int i) const { return ors[i]; }
};
struct CvTeam {
    bool known[TECH_COUNT];
    std::vector<std::pair<int, int> > grants;
    CvTeam() { for (int i = 0; i < TECH_COUNT; ++i) known[i] = false; }
    bool isHasTech(TechTypes t) const { assert(t >= 0 && t < TECH_COUNT); return known[t]; }
    void setHasTech(TechTypes t, bool value, PlayerTypes p, bool first, bool announce, bool end = false) {
        assert(value && !first && !announce && !end && t >= 0 && t < TECH_COUNT);
        assert(!known[t]); known[t] = true; grants.push_back(std::make_pair(int(t), p));
    }
} teams[20];
#define GET_TEAM(t) teams[t]
struct CvPlayer {
    int id, team;
    bool alive, major;
    EraTypes era;
    CvPlayer(int p, int t, EraTypes e = ERA_0) : id(p), team(t), alive(true), major(true), era(e) {}
    int getID() const { return id; }
    int getTeam() const { return team; }
    bool isAlive() const { return alive; }
    EraTypes getCurrentEra() const { return era; }
};
std::vector<CvPlayer> players;
template<int Kind> struct PlayerIter {
    size_t index;
    PlayerIter() : index(0) { skip(); }
    void skip() {
        while (index < players.size() && (!players[index].alive || (Kind == MAJOR_CIV && !players[index].major))) ++index;
    }
    bool hasNext() const { return index < players.size(); }
    void operator++() { ++index; skip(); }
    CvPlayer const* operator->() const { return &players[index]; }
};
struct Game {
    std::deque<int> rolls;
    int calls;
    Game() : calls(0) {}
    int getSorenRandNum(int n, char const*) {
        assert(n == 100 && !rolls.empty());
        int r = rolls.front(); rolls.pop_front(); ++calls; assert(r >= 0 && r < n); return r;
    }
} game;
struct Globals {
    CvTechInfo tech[TECH_COUNT];
    int getNumTechInfos() const { return TECH_COUNT; }
    CvTechInfo const& getInfo(TechTypes t) const { assert(t >= 0 && t < TECH_COUNT); return tech[t]; }
    Game& getGame() const { return game; }
} GC;
#define SyncRandNum(n) GC.getGame().getSorenRandNum(n, "fixture")
'''
checks = r'''
void reset() {
    players.clear(); players.push_back(CvPlayer(0, 2)); players.push_back(CvPlayer(1, 4));
    for (int i = 0; i < 20; ++i) teams[i] = CvTeam();
    for (int i = 0; i < TECH_COUNT; ++i) GC.tech[i] = CvTechInfo();
    game = Game();
}
void chance(int roll, bool expected, int ownerCount = 1, int summoner = NO_PLAYER) {
    reset(); teams[4].known[TECH_0] = true;
    for (int i = 1; i < ownerCount; ++i) players.push_back(CvPlayer(i + 1, 4));
    game.rolls.push_back(roll); doWorldTechDiffusionForSummonedPlayer(players[0], summoner);
    assert(teams[2].known[TECH_0] == expected && game.calls == 1 && game.rolls.empty());
    assert(teams[4].known[TECH_0]);
    if (expected) assert(teams[2].grants[0].second == players[0].getID());
}
int main() {
    chance(4, true); chance(5, false);
    chance(9, true, 1, 1); chance(10, false, 1, 1);
    chance(12, true, 2); chance(13, false, 2);
    chance(74, true, 12, 1); chance(75, false, 12, 1);
    reset(); teams[4].known[TECH_2] = true; GC.tech[2].ors.push_back(TECH_0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(!teams[2].known[TECH_2] && game.calls == 0);
    teams[2].known[TECH_1] = true; GC.tech[2].ors.push_back(TECH_1); game.rolls.push_back(0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(teams[2].known[TECH_2] && game.calls == 1);
    reset(); teams[4].known[TECH_3] = true;
    GC.tech[3].ands.push_back(TECH_0); GC.tech[3].ands.push_back(TECH_1);
    teams[2].known[TECH_0] = true;
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(!teams[2].known[TECH_3] && game.calls == 0);
    teams[2].known[TECH_1] = true; game.rolls.push_back(0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(teams[2].known[TECH_3] && game.calls == 1);
    reset(); teams[4].known[TECH_0] = teams[4].known[TECH_1] = true;
    game.rolls.push_back(99); game.rolls.push_back(0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(!teams[2].known[TECH_0] && teams[2].known[TECH_1] && game.calls == 2);
    reset(); teams[4].known[TECH_0] = teams[4].known[TECH_1] = true;
    GC.tech[0].ands.push_back(TECH_1); game.rolls.push_back(0); game.rolls.push_back(0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER);
    assert(game.calls == 2 && teams[2].grants.size() == 2);
    assert(teams[2].grants[0].first == TECH_1 && teams[2].grants[1].first == TECH_0);
    reset(); teams[2].known[TECH_0] = true;
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER); assert(game.calls == 0);
    reset(); teams[4].known[TECH_0] = true; GC.tech[0].ands.push_back(-1);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER); assert(game.calls == 0);
    GC.tech[0].ands.clear(); GC.tech[0].ors.push_back(TECH_COUNT);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER); assert(game.calls == 0);
    reset(); teams[4].known[TECH_0] = teams[4].known[TECH_1] = true;
    GC.tech[0].ands.push_back(TECH_1); GC.tech[1].ands.push_back(TECH_0);
    doWorldTechDiffusionForSummonedPlayer(players[0], NO_PLAYER); assert(game.calls == 0);
    reset(); teams[4].known[TECH_0] = true; players[1].alive = false;
    doWorldTechDiffusionForSummonedPlayer(players[0], 1); assert(game.calls == 0);
    players.clear(); assert(calculateMedianEraOfMajorCivs() == ERA_0);
    players.push_back(CvPlayer(0, 0, ERA_7)); assert(calculateMedianEraOfMajorCivs() == ERA_7);
    players.push_back(CvPlayer(1, 1, ERA_1)); assert(calculateMedianEraOfMajorCivs() == ERA_1);
    players.push_back(CvPlayer(2, 2, ERA_9)); assert(calculateMedianEraOfMajorCivs() == ERA_7);
    players.clear(); int eras[] = {9, 1, 5, 0, 3, 7};
    for (int i = 0; i < 6; ++i) players.push_back(CvPlayer(i, i, static_cast<EraTypes>(eras[i])));
    assert(calculateMedianEraOfMajorCivs() == ERA_3);
    players[0].alive = false; players[1].major = false;
    assert(calculateMedianEraOfMajorCivs() == ERA_3);
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp, binary = Path(directory) / 'catchup.cpp', Path(directory) / 'catchup'
    cpp.write_text(stub + '\n' + methods + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('Actual summon catch-up helpers: strict C++03 + ASan/UBSan passed (engine/RNG stubs)')
