#!/usr/bin/env python3
"""Compile the actual equipment trade rule functions against small stubs and
check their behaviour.

Covers CvPlayer::changeEquipmentCount, changeEquipmentInUseCount,
canTradeEquipmentTo, giveEquipmentTo and CvPlayerAI::AI_equipmentTradeVal,
AI_equipmentTrade. Everything around them (info loading, the deal object, the
trade screen, AI negotiation) is simulated or absent; this is not a DLL test.
"""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]

def method(source, signature):
    start = source.index(signature)
    brace, depth = source.index('{', start), 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

player = (root / 'CvGameCoreDLL/CvPlayer.cpp').read_text(encoding='latin-1')
ai = (root / 'CvGameCoreDLL/CvPlayerAI.cpp').read_text(encoding='latin-1')
methods = '\n'.join(
    [method(player, s) for s in [
        'void CvPlayer::changeEquipmentCount(EquipmentTypes',
        'void CvPlayer::changeEquipmentInUseCount(EquipmentTypes',
        'bool CvPlayer::canTradeEquipmentTo(PlayerTypes',
        'bool CvPlayer::giveEquipmentTo(PlayerTypes']] +
    [method(ai, s) for s in [
        'int CvPlayerAI::AI_equipmentTradeVal(EquipmentTypes',
        'DenialTypes CvPlayerAI::AI_equipmentTrade(EquipmentTypes']])

stub = r'''
#include <cassert>
#include <algorithm>
enum EquipmentTypes { NO_EQUIPMENT = -1, EQ_A, EQ_B, EQ_C, NUM_EQ };
enum PlayerTypes { NO_PLAYER = -1, P0, P1, P2, NUM_P };
enum TeamTypes { NO_TEAM = -1, T0, T1, T2 };
enum AttitudeTypes { ATT_FURIOUS, ATT_ANNOYED, ATT_CAUTIOUS, ATT_PLEASED, ATT_FRIENDLY };
enum DenialTypes { NO_DENIAL = -1, DENIAL_UNKNOWN, DENIAL_ATTITUDE, DENIAL_NO_GAIN, DENIAL_WORST_ENEMY };
#define FAssert(x) assert(x)
int g_errors = 0;
#define FErrorMsg(x) (++g_errors)
struct CvEquipmentInfo {
    bool trade, personal; int value;
    CvEquipmentInfo() : trade(true), personal(false), value(100) {}
    bool isTrade() const { return trade; }
    bool isPersonalWeapon() const { return personal; }
    int getAITradeValue() const { return value; }
};
struct Leader { int threshold; int getStrategicBonusRefuseAttitudeThreshold() const { return threshold; } };
struct Globals {
    CvEquipmentInfo eq[NUM_EQ]; Leader leader;
    int getNumEquipmentInfos() const { return NUM_EQ; }
    CvEquipmentInfo const& getInfo(EquipmentTypes e) const { assert(e >= 0 && e < NUM_EQ); return eq[e]; }
    Leader const& getInfo(int) const { return leader; }
} GC;
struct Map { int v[NUM_EQ]; Map() { for (int i = 0; i < NUM_EQ; ++i) v[i] = 0; }
    int get(EquipmentTypes e) const { assert(e >= 0 && e < NUM_EQ); return v[e]; }
    void add(EquipmentTypes e, int c) { assert(e >= 0 && e < NUM_EQ); v[e] += c; } };
struct CvTeamAI {
    TeamTypes id, worst; bool vassalOf[3], war[3];
    CvTeamAI() : id(NO_TEAM), worst(NO_TEAM) { for (int i = 0; i < 3; ++i) vassalOf[i] = war[i] = false; }
    bool isVassal(TeamTypes t) const { return vassalOf[t]; }
    bool isAtWar(TeamTypes t) const { return war[t]; }
    TeamTypes AI_getWorstEnemy() const { return worst; }
    int AI_roundTradeVal(int v) const { return v; }
};
CvTeamAI g_teams[3];
struct CvPlayer {
    PlayerTypes id; TeamTypes team; bool human; AttitudeTypes att[NUM_P];
    Map m_aiEquipmentCount, m_aiEquipmentInUseCount;
    CvPlayer() : id(NO_PLAYER), team(NO_TEAM), human(false) { for (int i = 0; i < NUM_P; ++i) att[i] = ATT_PLEASED; }
    PlayerTypes getID() const { return id; }
    TeamTypes getTeam() const { return team; }
    bool isHuman() const { return human; }
    int getPersonalityType() const { return 0; }
    AttitudeTypes AI_getAttitude(PlayerTypes p) const { return att[p]; }
    int AI_goldTradeValuePercent() const { return 200; }
    int getEquipmentCount(EquipmentTypes e) const { return m_aiEquipmentCount.get(e); }
    int getEquipmentInUseCount(EquipmentTypes e) const { return m_aiEquipmentInUseCount.get(e); }
    int getNumTradeableEquipment(EquipmentTypes e) const { return std::max(0, getEquipmentCount(e) - getEquipmentInUseCount(e)); }
    void changeEquipmentCount(EquipmentTypes, int);
    void changeEquipmentInUseCount(EquipmentTypes, int);
    bool canTradeEquipmentTo(PlayerTypes, EquipmentTypes) const;
    bool giveEquipmentTo(PlayerTypes, EquipmentTypes);
    int AI_equipmentTradeVal(EquipmentTypes) const;
    DenialTypes AI_equipmentTrade(EquipmentTypes, PlayerTypes) const;
};
typedef CvPlayer CvPlayerAI;
CvPlayer g_players[NUM_P];
CvPlayer& GET_PLAYER(PlayerTypes p) { assert(p >= 0 && p < NUM_P); return g_players[p]; }
CvTeamAI& GET_TEAM(TeamTypes t) { return g_teams[t]; }
TeamTypes TEAMID(PlayerTypes p) { return g_players[p].team; }
'''

checks = r'''
void reset() {
    GC = Globals(); GC.leader.threshold = ATT_ANNOYED; g_errors = 0;
    for (int i = 0; i < NUM_P; ++i) { g_players[i] = CvPlayer(); g_players[i].id = (PlayerTypes)i; g_players[i].team = (TeamTypes)i; }
    for (int i = 0; i < 3; ++i) { g_teams[i] = CvTeamAI(); g_teams[i].id = (TeamTypes)i; }
}
int main() {
    reset(); CvPlayer& a = g_players[P0]; CvPlayer& b = g_players[P1];
    // Nothing owned: nothing to trade.
    assert(!a.canTradeEquipmentTo(P1, EQ_A) && !a.giveEquipmentTo(P1, EQ_A));
    a.changeEquipmentCount(EQ_A, 1);
    assert(a.canTradeEquipmentTo(P1, EQ_A));
    // Invalid ids and targets are rejected without touching the info array.
    assert(!a.canTradeEquipmentTo(P1, NO_EQUIPMENT) && !a.canTradeEquipmentTo(P1, (EquipmentTypes)NUM_EQ));
    assert(!a.canTradeEquipmentTo(P0, EQ_A) && !a.canTradeEquipmentTo(NO_PLAYER, EQ_A));
    a.changeEquipmentCount((EquipmentTypes)NUM_EQ, 1); a.changeEquipmentInUseCount(NO_EQUIPMENT, 1);
    assert(g_errors == 2);
    // bTrade flag and personal pieces.
    GC.eq[EQ_A].trade = false; assert(!a.canTradeEquipmentTo(P1, EQ_A)); GC.eq[EQ_A].trade = true;
    GC.eq[EQ_A].personal = true; assert(!a.canTradeEquipmentTo(P1, EQ_A)); GC.eq[EQ_A].personal = false;
    // A piece carried by a unit can't be traded; a second, spare one can.
    a.changeEquipmentInUseCount(EQ_A, 1);
    assert(a.getNumTradeableEquipment(EQ_A) == 0 && !a.canTradeEquipmentTo(P1, EQ_A));
    a.changeEquipmentCount(EQ_A, 1); assert(a.canTradeEquipmentTo(P1, EQ_A));
    // No duplicates for the receiver.
    b.changeEquipmentCount(EQ_A, 1); assert(!a.canTradeEquipmentTo(P1, EQ_A) && !a.giveEquipmentTo(P1, EQ_A));
    assert(a.getEquipmentCount(EQ_A) == 2 && b.getEquipmentCount(EQ_A) == 1);
    b.changeEquipmentCount(EQ_A, -1);
    // The hand-over moves exactly one piece and can't be repeated.
    assert(a.giveEquipmentTo(P1, EQ_A));
    assert(a.getEquipmentCount(EQ_A) == 1 && b.getEquipmentCount(EQ_A) == 1 && a.getEquipmentInUseCount(EQ_A) == 1);
    assert(!a.giveEquipmentTo(P1, EQ_A) && a.getEquipmentCount(EQ_A) == 1);
    // The receiver can't hand it back while the giver still owns one.
    assert(!b.canTradeEquipmentTo(P0, EQ_A));
    // Other types are unaffected.
    assert(a.getEquipmentCount(EQ_B) == 0 && b.getEquipmentCount(EQ_C) == 0);

    // Valuation: gold price times the gold conversion; 0 if unpriced or invalid.
    reset();
    assert(g_players[P0].AI_equipmentTradeVal(EQ_A) == 200 && g_players[P2].AI_equipmentTradeVal(EQ_A) == 200);
    GC.eq[EQ_B].value = 0; assert(g_players[P0].AI_equipmentTradeVal(EQ_B) == 0);
    GC.eq[EQ_B].value = -5; assert(g_players[P0].AI_equipmentTradeVal(EQ_B) == 0);
    assert(g_players[P0].AI_equipmentTradeVal(NO_EQUIPMENT) == 0 && g_players[P0].AI_equipmentTradeVal((EquipmentTypes)NUM_EQ) == 0);

    // Denial.
    reset(); CvPlayer& ai = g_players[P0]; g_players[P1].human = true;
    ai.changeEquipmentCount(EQ_A, 1);
    assert(ai.AI_equipmentTrade(EQ_A, P1) == NO_DENIAL);          // human may ask for the last piece
    assert(ai.AI_equipmentTrade(EQ_A, P2) == DENIAL_NO_GAIN);     // another AI may not
    ai.changeEquipmentCount(EQ_A, 1);
    assert(ai.AI_equipmentTrade(EQ_A, P2) == NO_DENIAL);          // spare piece
    GC.eq[EQ_A].value = 0; assert(ai.AI_equipmentTrade(EQ_A, P1) == DENIAL_UNKNOWN); GC.eq[EQ_A].value = 100;
    assert(ai.AI_equipmentTrade(NO_EQUIPMENT, P1) == DENIAL_UNKNOWN);
    ai.att[P1] = ATT_ANNOYED; assert(ai.AI_equipmentTrade(EQ_A, P1) == DENIAL_ATTITUDE);
    ai.att[P1] = ATT_CAUTIOUS; assert(ai.AI_equipmentTrade(EQ_A, P1) == NO_DENIAL);
    g_teams[T0].worst = T1; assert(ai.AI_equipmentTrade(EQ_A, P1) == DENIAL_WORST_ENEMY);
    g_teams[T0].war[T1] = true; assert(ai.AI_equipmentTrade(EQ_A, P1) == NO_DENIAL);   // peace deals
    g_teams[T0].war[T1] = false; g_teams[T0].vassalOf[T1] = true; assert(ai.AI_equipmentTrade(EQ_A, P1) == NO_DENIAL);
    ai.human = true; GC.eq[EQ_A].value = 0; assert(ai.AI_equipmentTrade(EQ_A, P2) == NO_DENIAL); // humans decide for themselves
    return 0;
}
'''

with tempfile.TemporaryDirectory() as directory:
    cpp, binary = Path(directory) / 'trade.cpp', Path(directory) / 'trade'
    cpp.write_text(stub + '\n' + methods + '\n' + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, env=dict(os.environ,
                   ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
print('Equipment trade rules: strict C++03 + ASan/UBSan passed')
