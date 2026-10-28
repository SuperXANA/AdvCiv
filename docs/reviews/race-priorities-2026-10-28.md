# Civilization race-priority member follow-up — 2026-10-28

Source FFHRaceTypes: a50b62ccd1ec72672c3b8b4814ad03230088ea18.
Previous draft c51f157812cfe248f07fcccf1eed7a5fa0a760a9; new code https://github.com/SuperXANA/AdvCiv/commit/73dc2faf9e7efb807d20bcd7dc23c97f4f68b0c1.
Read-only baseline remains 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## RACE-20261028-04 — complete the pending owned-member declaration and accessor

The earlier race-demographics review explicitly recorded m_piRacePriorities as unresolved integration scope. This pass implements that pending repair rather than presenting it as a newly discovered defect.

[CvCivilizationInfo declaration, header line 111](https://github.com/SuperXANA/AdvCiv/blob/73dc2faf9e7efb807d20bcd7dc23c97f4f68b0c1/CvGameCoreDLL/CvInfo_Civilization.h#L111) now declares int* m_piRacePriorities within XANA 06-21-2025 markers. Its constructor already initializes this name to NULL, its XML reader passes its address to SetVariableListTagPair, and its destructor already deletes it. Without the member declaration those definitions cannot compile. The pointer is placed after m_paszCityNames to match its position in the existing constructor initializer sequence.

[getRacePriority, implementation line 205](https://github.com/SuperXANA/AdvCiv/blob/73dc2faf9e7efb807d20bcd7dc23c97f4f68b0c1/CvGameCoreDLL/CvInfo_Civilization.cpp#L205) previously indexed any non-null array without checking i. The repair rejects negative and metadata-out-of-range indices before access, returning the same zero fallback used for absent arrays. Valid values, including nonpositive priorities, remain unchanged. It assumes any populated array has the XML reader's current getNumRaceInfos length; this does not protect a stale array allocated against a different metadata count.

No XML reader, stream/cache layout, reset semantics, copy behavior or race-selection policy changes in this pass. Adding this member completes one declaration requirement, not the full race feature's integration.

## Verification

python tests/race-priorities/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -Wno-reorder -pedantic -fsanitize=address,undefined. LeakSanitizer disabled, UBSan halt_on_error enabled. Reorder diagnostics are disabled for the preexisting unrelated constructor initializer ordering; this is not a zero-warning native compilation claim.

The fixture compiles the actual complete CvCivilizationInfo class declaration (excluding the rest of the header), actual constructor/destructor and actual getRacePriority method. Engine/base/string/types are stubbed. A derived fixture installs a three-entry array and an instrumented SAFE_DELETE_ARRAY verifies one owned allocation is deleted; all other constructor-owned arrays stay null. Checks cover null fallback, positive/zero/negative values, -1, the first out-of-range index and a large invalid index.

The fixture does not execute XML loading, cache-enabled methods, real metadata initialization, unrelated class fields, stream reads/writes, copy/reset, MSVC 7.1, engine ABI, DLL or gameplay. No workflow or DLL build was triggered. Earlier race RNG/initialization/accessor findings RACE-20261027-01..03 remain in the original report with their existing limits.

Only CvInfo_Civilization.h/.cpp change in production this pass; original feature branches, existing XANA markers and 1.14 are preserved. No new branch was created. Reuse RaceDemographicsDraft-ChatGPT for remaining info loader/cache consistency, metadata readiness, lifecycle and versioned persistence before a coherent complete pinned-base DLL build.

## Coverage

Fresh inventory showed no changed source heads. CivicScrollDraft's different head is already-delivered religion-row documentation. UnitStatusEffects remains deferred; the ceiling alert remains closed. Partial reviews and failed/unverified native states remain, so the stop gate is false.
