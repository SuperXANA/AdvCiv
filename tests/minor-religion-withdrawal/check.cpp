// Placeholders are filled from current production source by check.py.
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

typedef unsigned int uint;
int const MAX_INT = INT_MAX;
#define FAssert(condition) assert(condition)
#define FOR_EACH_ENUM(Name) for (int eLoop##Name = 0; eLoop##Name < 1; ++eLoop##Name)
enum HybridOrganizationTypes { HYBRID_ZERO, HYBRID_ONE, HYBRID_DISABLED };

struct CvHybridOrganizationInfo {
    int duration;
    int getWithdrawalUnhappinessTurns() const { return duration; }
};
struct Info {
    int getHappyBonus() const { return 0; }
    const wchar_t* getTextKeyWide() const { return L"civic"; }
};
struct Globals {
    int magnitude;
    CvHybridOrganizationInfo hybrid[3];
    int getDefineINT(const char* key) const {
        assert(std::string(key) == "TEMP_HAPPY"); return magnitude;
    }
    int getPERCENT_ANGER_DIVISOR() const { return 1000; }
    CvHybridOrganizationInfo const& getInfo(HybridOrganizationTypes id) const { return hybrid[id]; }
    Info getInfo(int) const { return Info(); }
} GC;
struct Player {
    int getGwPercentAnger() const { return 0; }
    int getCivicPercentAnger(int) const { return 0; }
    int getBuildingHappiness() const { return 0; }
    int getExtraHappiness() const { return 0; }
    bool isAnarchy() const { return false; }
} owner;
#define GET_PLAYER(id) owner
struct Area { int getBuildingHappiness(int) const { return 0; } } area;

// Typed sequential int stream; adjacent field and trailing sentinel expose a
// missing/versionless/misordered timer read. Not the real FDataStreamBase codec.
struct FDataStreamBase {
    std::vector<int> data;
    unsigned int cursor;
    FDataStreamBase() : cursor(0) {}
    void Write(int value) { data.push_back(value); }
    void Write(uint value) { data.push_back(static_cast<int>(value)); }
    void Read(int* value) { assert(cursor < data.size()); *value = data[cursor++]; }
    void Read(uint* value) { int i; Read(&i); *value = static_cast<uint>(i); }
};

struct CvCity {
    @DECLARATIONS@
    bool immune;
    int otherAnger;
    int dirtyCalls;
    int pendingReligion;
    int observedAnger;
    CvCity() : immune(false), otherAnger(0), dirtyCalls(0),
               pendingReligion(-1), observedAnger(0) { @INITIALIZATION@ }
    void AI_setAssignWorkDirty(bool dirty) { assert(dirty); ++dirtyCalls; }
    int unhappyLevel(int iExtra = 0) const;
    int happyLevel() const;
    void setCityChangesDueToMinorReligionJoining(HybridOrganizationTypes);
    void setCityChangesDueToMinorReligionLeaving(HybridOrganizationTypes);
    void doProduction(bool) { observedAnger = unhappyLevel(); }
    void doDecay() {}
    void doReligion() {
        if (pendingReligion >= 0) {
            setCityChangesDueToMinorReligionLeaving(static_cast<HybridOrganizationTypes>(pendingReligion));
            pendingReligion = -1;
        }
    }
    void productionThroughReligion() { bool const bForceProduction = true; @TURN@ }
    void readTimers(FDataStreamBase* pStream) { @READ@ }
    void writeTimers(FDataStreamBase* pStream) { @WRITE@ }
    bool isNoUnhappiness() const { return immune; }
    bool isOccupation() const { return false; }
    int getOwner() const { return 0; }
    int getHandicapType() const { return 0; }
    int getPopulation() const { return 1; }
    Area const& getArea() const { return area; }
    int getOvercrowdingPercentAnger(int = 0) const { return 0; }
    int getHurryPercentAnger(int = 0) const { return m_iHurryAngerTimer > 0 ? 1000 : 0; }
    int getConscriptPercentAnger(int = 0) const { return m_iConscriptAngerTimer > 0 ? 1000 : 0; }
    int getDefyResolutionPercentAnger(int = 0) const { return m_iDefyResolutionAngerTimer > 0 ? 1000 : 0; }
    int getHurryAngerTimer() const { return m_iHurryAngerTimer; }
    int getConscriptAngerTimer() const { return m_iConscriptAngerTimer; }
    int getDefyResolutionAngerTimer() const { return m_iDefyResolutionAngerTimer; }
    int getEspionageHappinessCounter() const { return otherAnger; }
#define ZERO_GETTER(name) int name() const { return 0; }
    ZERO_GETTER(getNoMilitaryPercentAnger)
    ZERO_GETTER(getCulturePercentAnger)
    ZERO_GETTER(getReligionPercentAnger)
    ZERO_GETTER(getWarWearinessPercentAnger)
    ZERO_GETTER(getLargestCityHappiness)
    ZERO_GETTER(getMilitaryHappiness)
    ZERO_GETTER(getCurrentStateReligionHappiness)
    ZERO_GETTER(getBuildingGoodHappiness)
    ZERO_GETTER(getBuildingBadHappiness)
    ZERO_GETTER(getExtraBuildingGoodHappiness)
    ZERO_GETTER(getExtraBuildingBadHappiness)
    ZERO_GETTER(getSurroundingGoodHappiness)
    ZERO_GETTER(getSurroundingBadHappiness)
    ZERO_GETTER(getBonusGoodHappiness)
    ZERO_GETTER(getBonusBadHappiness)
    ZERO_GETTER(getReligionGoodHappiness)
    ZERO_GETTER(getReligionBadHappiness)
    ZERO_GETTER(getCommerceHappiness)
    ZERO_GETTER(getExtraHappiness)
    ZERO_GETTER(getVassalUnhappiness)
    ZERO_GETTER(getVassalHappiness)
#undef ZERO_GETTER
};
@METHODS@

struct CvWStringBuffer {
    void append(std::wstring const&) {}
    void append(wchar_t const*) {}
};
wchar_t const* const NEWLINE = L"\n";
struct TextDLL {
    int withdrawalRows, withdrawalAmount, withdrawalTurns, total;
    TextDLL() { reset(); }
    void reset() { withdrawalRows = withdrawalAmount = withdrawalTurns = total = 0; }
    std::wstring getText(char const* key, int first = 0, int second = 0) {
        if (std::string(key) == "TXT_KEY_ANGER_MINOR_RELIGION_WITHDRAWAL") {
            ++withdrawalRows; withdrawalAmount = first; withdrawalTurns = second;
        }
        if (std::string(key) == "TXT_KEY_ANGER_TOTAL_UNHAPPY") total = first;
        return L"";
    }
    std::wstring getText(char const* key, int first, wchar_t const*) { return getText(key, first); }
} textDLL;
TextDLL* gDLL = &textDLL;
struct CvGameTextMgr { void setAngerHelp(CvWStringBuffer&, CvCity const&); } textMgr;
@ANGER_HELP@

void checkHelp(CvCity const& city, int expectedRows) {
    textDLL.reset(); CvWStringBuffer buffer; textMgr.setAngerHelp(buffer, city);
    assert(textDLL.total == city.unhappyLevel());
    assert(textDLL.withdrawalRows == expectedRows);
    if (expectedRows) {
        assert(textDLL.withdrawalAmount == city.getTemporaryUnhappiness());
        assert(textDLL.withdrawalTurns == city.getUnhappinessTimer());
    }
}

int main(int argc, char** argv) {
    assert(argc == 2);
    int const magnitude = std::atoi(argv[1]);
    GC.magnitude = magnitude;
    GC.hybrid[HYBRID_ZERO].duration = 1;
    GC.hybrid[HYBRID_ONE].duration = 4;
    GC.hybrid[HYBRID_DISABLED].duration = 0;
    int lifecycleCases = 0, streamCases = 0, boundsCases = 0;
    for (int duration = 1; duration <= 6; ++duration) {
        GC.hybrid[HYBRID_ZERO].duration = duration;
        CvCity city;
        assert(city.getUnhappinessTimer() == 0 && city.unhappyLevel() == 0);
        city.setCityChangesDueToMinorReligionJoining(HYBRID_ONE);
        assert(city.getHappinessTimer() == 4 && city.happyLevel() == magnitude);
        assert(city.getUnhappinessTimer() == 0);
        city.setCityChangesDueToMinorReligionLeaving(HYBRID_DISABLED);
        assert(city.getUnhappinessTimer() == 0);
        GC.hybrid[HYBRID_DISABLED].duration = -3;
        city.setCityChangesDueToMinorReligionLeaving(HYBRID_DISABLED);
        assert(city.getUnhappinessTimer() == 0);
        GC.hybrid[HYBRID_DISABLED].duration = 0;

        // A withdrawal arising inside doReligion retains its entire duration.
        city.pendingReligion = HYBRID_ZERO;
        city.productionThroughReligion();
        assert(city.observedAnger == 0 && city.getUnhappinessTimer() == duration);
        assert(city.happyLevel() == magnitude && city.unhappyLevel() == magnitude);
        checkHelp(city, magnitude > 0 ? 1 : 0);
        city.immune = true;
        assert(city.unhappyLevel() == 0); checkHelp(city, 0);
        city.immune = false;

        // Repeated withdrawal adds time with fixed magnitude; joining and
        // all three pre-existing anger timers remain independent.
        city.setCityChangesDueToMinorReligionLeaving(HYBRID_ONE);
        assert(city.getUnhappinessTimer() == duration + 4);
        assert(city.unhappyLevel() == magnitude && city.getHappinessTimer() == 4);
        city.m_iHurryAngerTimer = 7; city.m_iConscriptAngerTimer = 5;
        city.m_iDefyResolutionAngerTimer = 2; city.otherAnger = 2;
        assert(city.unhappyLevel() == magnitude + 5); checkHelp(city, magnitude > 0 ? 1 : 0);
        int const dirtyBefore = city.dirtyCalls;
        for (int remaining = duration + 4; remaining > 0; --remaining) {
            city.productionThroughReligion();
            assert(city.observedAnger == magnitude + 5);
            assert(city.getUnhappinessTimer() == remaining - 1);
            assert(city.m_iHurryAngerTimer == 7 && city.m_iConscriptAngerTimer == 5);
            assert(city.m_iDefyResolutionAngerTimer == 2 && city.getHappinessTimer() == 4);
        }
        assert(city.dirtyCalls == dirtyBefore + duration + 4);
        assert(city.unhappyLevel() == 5); checkHelp(city, 0);
        city.productionThroughReligion();
        assert(city.observedAnger == 5 && city.dirtyCalls == dirtyBefore + duration + 4);
        ++lifecycleCases;
    }

    // Real writer flag/field sequence and conditional reader slice, with distinct
    // neighboring values, a trailing marker and reuse of a previously angry city.
    GC.magnitude = 2;
    for (int turns = 0; turns <= 9; ++turns) {
        CvCity before; before.changeUnhappinessTimer(turns);
        before.m_iHappinessTimer = 13; before.m_iMilitaryHappinessUnits = 29;
        FDataStreamBase stream; before.writeTimers(&stream); stream.Write(71);
        assert(stream.data.size() == 5 && stream.data[0] == 18);
        CvCity after; after.readTimers(&stream);
        int marker; stream.Read(&marker);
        assert(marker == 71 && stream.cursor == stream.data.size());
        assert(after.getUnhappinessTimer() == turns && after.getHappinessTimer() == 13);
        assert(after.m_iMilitaryHappinessUnits == 29 && after.unhappyLevel() == before.unhappyLevel());
        assert(after.dirtyCalls == 0);
        for (int i = 0; i <= turns; ++i) {
            before.productionThroughReligion(); after.productionThroughReligion();
            assert(after.getUnhappinessTimer() == before.getUnhappinessTimer());
            assert(after.observedAnger == before.observedAnger);
        }
        ++streamCases;
    }
    CvCity reused; reused.changeUnhappinessTimer(8);
    FDataStreamBase legacy; legacy.Write(17u); legacy.Write(13); legacy.Write(29); legacy.Write(71);
    reused.readTimers(&legacy); int marker; legacy.Read(&marker);
    assert(reused.getUnhappinessTimer() == 0 && reused.getHappinessTimer() == 13);
    assert(reused.m_iMilitaryHappinessUnits == 29 && marker == 71 && legacy.cursor == legacy.data.size());
    ++streamCases;

    int const seeds[] = {0, 1, 9, INT_MAX - 1, INT_MAX};
    int const deltas[] = {INT_MIN, -10, -1, 0, 1, 10, INT_MAX};
    for (int s = 0; s < 5; ++s) for (int d = 0; d < 7; ++d) {
        CvCity city; city.changeUnhappinessTimer(seeds[s]); city.dirtyCalls = 0;
        // Expected result uses subtraction/comparison, independently of the
        // production bounded-addition expression (no wider integer extension).
        int expected = seeds[s];
        if (deltas[d] > 0 && deltas[d] > INT_MAX - expected) expected = INT_MAX;
        else if (deltas[d] < 0 && deltas[d] < -expected) expected = 0;
        else expected += deltas[d];
        city.changeUnhappinessTimer(deltas[d]);
        assert(city.getUnhappinessTimer() == expected);
        assert(city.dirtyCalls == (expected != seeds[s] ? 1 : 0));
        ++boundsCases;
    }
    GC.magnitude = -2; reused.changeUnhappinessTimer(3);
    assert(reused.getTemporaryUnhappiness() == 0);
    std::cout << lifecycleCases << " lifecycle/tooltip cases, " << streamCases
              << " stream cases, " << boundsCases << " timer-bound cases passed\n";
}
