# Summon civilization selector — 2026-10-28

Code cb83bcd5425b49185855653b0470633ad66dcbbe; reused SummonCatchupDraft-ChatGPT.
Original source d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc unchanged.
No original feature head changed during inventory. CI intentionally skipped.

## SUMMON-20261028-05

CvPlayer.cpp selectCompatibleCivForSummonLeader begins at line 15461.
The previous helper enumerated getNumLeaders()/getLeader(j) to test civilization
compatibility. Actual pinned 1.14 CvInfo_Civilization.h declares getNumLeaders()
and isLeaders(int), but no getLeader(int). The enumeration could not compile
against that interface.

The helper now checks kCiv.isLeaders(eLeader), matching the baseline mask.
The leader ID is validated against getNumLeaderHeadInfos before lookup;
each candidate civ is validated against getNumCivilizationInfos before metadata
or event-weight access. The candidate vector is const. LEAD_ANY_CIV still
bypasses compatibility only, not ID validation or supplied-pool membership.
Positive event weights and existing selection behavior are retained.

## Checks and limits

python tests/summon-civ/check.py extracts the actual helper.
Passed strict C++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan and
UBSAN_OPTIONS=halt_on_error=1; ASAN_OPTIONS=detect_leaks=0.
Metadata/RNG are stubs. Cases include ordinary compatibility, lead-any,
supplied pool restriction, zero-weight exclusion, 2:3 weighted draw boundaries,
absent weight array, empty pool and invalid leader/civilization IDs.
The baseline interface was read directly; this is not inferred from stubs.
An old-helper control fails compilation against the minimal fixture, including
its getLeader reference; unrelated fixture omissions are not native errors.

No full DLL workflow was added or triggered. Commit uses [skip ci].
Large weight totals/overflow, RNG use inside event eligibility queries, remaining
resolver syntax/slot creation and transfer integration remain unresolved.
No standalone fixture is presented as MSVC 7.1/DLL or gameplay validation.
Original XANA markers, source branch and read-only 1.14 remain unchanged.
