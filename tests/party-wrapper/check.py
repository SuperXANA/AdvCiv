#!/usr/bin/env python3
"""Compile the actual CyPartyGroup declaration/body against instrumented API stubs.

This checks the wrapper boundary only, not a DLL, Boost.Python, or party engine.
Run from any directory; requires a C++03-capable g++ on PATH.
"""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
header = (root / 'CvGameCoreDLL/CySelectionGroup.h').read_text()
source = (root / 'CvGameCoreDLL/CySelectionGroup.cpp').read_text()
declaration = header[header.index('class CyPartyGroup\n'):]
declaration = declaration[:declaration.index('};') + 2]
begin = source.index('CyPartyGroup::CyPartyGroup()')
body = source[begin:source.index('// XANA:', begin)]

stub = r'''
#include <cassert>
#include <cstddef>
enum MissionTypes { MISSION_MOVE_TO, MISSION_OTHER };
enum MovementFlags { NO_MOVEMENT_FLAGS };
enum MissionAITypes { NO_MISSIONAI };
enum UnitAITypes { UNITAI_TEST };
enum TeamTypes { TEAM_TEST };
struct MissionData {};
struct CvPlot {};
struct CvUnit {};
struct CyPlot {
    CvPlot* p;
    explicit CyPlot(CvPlot* v) : p(v) {}
    CvPlot* getPlot() { return p; }
};
struct CyUnit {
    CvUnit* p;
    explicit CyUnit(CvUnit* v) : p(v) {}
    CvUnit* getUnit() { return p; }
};
struct CvPartyGroup {
    int pushes, pops, clears, queries, x, y;
    CvPlot plot;
    CvUnit unit;
    MissionData mission;
    CvPlot const* lastPlot;
    CvUnit const* lastUnit;
    CvPartyGroup() : pushes(0), pops(0), clears(0), queries(0), x(0), y(0),
        lastPlot(NULL), lastUnit(NULL) {}
    void pushMission(MissionTypes, int a, int b,
        MovementFlags = NO_MOVEMENT_FLAGS, bool = false, bool = false,
        MissionAITypes = NO_MISSIONAI, CvPlot const* p = NULL,
        CvUnit const* u = NULL) {
        ++pushes; x = a; y = b; lastPlot = p; lastUnit = u;
    }
    void popMission() { ++pops; }
    CvPlot* lastMissionPlot() { return &plot; }
    bool canStartMission(MissionTypes, int, int, CvPlot const* p, bool) {
        ++queries; lastPlot = p; return true;
    }
    bool isHuman() { return true; }
    bool isWaiting() { return true; }
    bool isFull() { return true; }
    bool hasCargo() { return true; }
    bool canFight() { return true; }
    bool canDefend() { return true; }
    int countNumUnitAIType(UnitAITypes) { return 2; }
    int getID() { return 7; }
    int getOwner() { return 3; }
    TeamTypes getTeam() { return TEAM_TEST; }
    int getNumUnits() { return 1; }
    void clearMissionQueue() { ++clears; }
    int getLengthMissionQueue() { return 1; }
    MissionData* getMissionFromQueue(int) { return &mission; }
    CvUnit* getHeadUnit() { return &unit; }
    CvUnit* getUnitAt(int) { return &unit; }
    int getMissionType(int) { return MISSION_OTHER; }
    int getMissionData1(int) { return 13; }
    int getMissionData2(int) { return 17; }
};
'''
checks = r'''
int main() {
    CvPartyGroup first, second;
    CyPartyGroup a(&first), b(second), empty;
    CyPartyGroup copied(a);
    assert(copied.getPartyGroup() == &first);
    assert(a.getPartyGroup() == &first && b.getPartyGroup() == &second);
    a.pushMoveToMission(4, 9);
    assert(first.pushes == 1 && first.x == 4 && first.y == 9);
    assert(second.pushes == 0);
    b.popMission();
    assert(second.pops == 1 && first.pops == 0);
    CyPlot* last = a.lastMissionPlot();
    assert(last && last->getPlot() == &first.plot); delete last;
    CyPlot p(&second.plot); CyUnit u(&second.unit);
    a.pushMission(MISSION_OTHER, 1, 2, 0, false, false, NO_MISSIONAI, &p, &u);
    assert(first.lastPlot == &second.plot && first.lastUnit == &second.unit);
    a.pushMission(MISSION_OTHER, 1, 2, 0, false, false, NO_MISSIONAI, NULL, NULL);
    assert(first.lastPlot == NULL && first.lastUnit == NULL);
    CyPlot noPlot(NULL); CyUnit noUnit(NULL);
    a.pushMission(MISSION_OTHER, 1, 2, 0, false, false, NO_MISSIONAI, &noPlot, &noUnit);
    assert(first.lastPlot == NULL && first.lastUnit == NULL);
    assert(a.canStartMission(0, 0, 0, &p, false));
    assert(first.lastPlot == &second.plot);
    assert(a.canStartMission(0, 0, 0, NULL, false));
    assert(first.lastPlot == NULL && first.queries == 2);
    assert(a.getUnitAt(-1) == NULL && a.getUnitAt(1) == NULL);
    CyUnit* member = a.getUnitAt(0); assert(member->getUnit() == &first.unit); delete member;
    empty.pushMoveToMission(1, 2); empty.popMission();
    empty.pushMission(MISSION_OTHER, 0, 0, 0, false, false, NO_MISSIONAI, NULL, NULL);
    assert(empty.isNone() && empty.lastMissionPlot() == NULL);
    assert(!empty.canStartMission(0, 0, 0, NULL, false));
    assert(empty.getUnitAt(0) == NULL && empty.getID() == -1);
    assert(first.pushes == 4 && second.pushes == 0);
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / 'wrapper.cpp'
    binary = Path(directory) / 'wrapper'
    cpp.write_text(stub + '\n' + declaration + '\n' + body + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1')
    subprocess.run([str(binary)], check=True, env=env)
print('Actual CyPartyGroup wrapper: strict C++03 + ASan/UBSan passed')
