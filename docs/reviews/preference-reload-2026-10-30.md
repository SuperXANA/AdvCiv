# Preference list/map repeated-load consistency — 2026-10-30

PREFERENCE-20261030-06. Original source LeaderCivilizationDecisionPreferences `aac03388283a5ac316f6a19f6e3754a7435b6511`; reused PreferenceFrameworkDraft-ChatGPT parent `8d6dc5585b79af44cdffc7ae4a3c22317d4e9361`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no changed original heads against the latest global ledger at 65aa3745ce458b6d2b6764cd2eddb8bd17b05f09. Prior cleanup/cursor reports and actual constructors, destructors, index getters, record getters and three enclosing read methods were read first.

[Correction and regression fixture 09367de35a207e4faa45fd9ab1e4099e23192a0e](https://github.com/SuperXANA/AdvCiv/commit/09367de35a207e4faa45fd9ab1e4099e23192a0e).

## Defect and correction

The five list readers clear their record vector after locating an XML list and passing SkipToNextVal. They delete the previous index map only inside the later positive-child-count/SetToChild guard. Re-reading an explicitly present empty list therefore clears all records while leaving a previous nonnegative index in the map. get*PreferenceIndex can return that stale index; a consumer's get*Preference then asserts or accesses a cleared vector.

Move each existing SAFE_DELETE_ARRAY call alongside its vector.clear(), before the child-count guard. No map allocation is needed for an empty list: all five existing index getters return -1 when the map is NULL. The baseline CvMemoryManager.h macro deletes and nulls the pointer. Baseline CvXMLLoadUtility::SkipToNextVal only skips comment nodes and returns true at a non-comment node; it does not require a nonempty child list.

| Actual reader | Corrected cleanup line |
| --- | ---: |
| CvTechPreferenceInfo::read, CvInfo_Civilization.cpp | 1614 |
| CvEventPreferenceInfo::read, CvInfo_RandomEvent.cpp | 2149 |
| CvUnitPreferenceInfo::read, UnitCombatPreferences, CvInfo_Unit.cpp | 2633 |
| CvUnitPreferenceInfo::read, UnitClassPreferences, CvInfo_Unit.cpp | 2667 |
| CvUnitPreferenceInfo::read, UnitPreferences, CvInfo_Unit.cpp | 2701 |

Omitted-list, failed-base-read and failed-SkipToNextVal paths keep existing data as before. Valid populated loads still allocate initialized maps and preserve record order, NONE skipping and last-duplicate indexing. Original XANA boundaries and earlier fixes remain; moved lines carry a dated ChatGPT annotation. This only synchronizes structures on the already-existing vector-clear path and does not invent new default inheritance rules or XML content.

## Verification

Run `python tests/preference-reload/check.py` from the branch checkout. It extracts the actual complete three class declarations and implementations from constructor through read, including actual destructors and all getters. A reduced CvInfoBase, globals/enums, XML tree/cursor and record readers stand in for the rest of the engine. Earlier tests of actual record readers remain separate and unchanged.

960 sequences passed C++03/ASan/UBSan: five info counts, six list lengths and all 32 combinations of five explicitly emptied lists. Each sequence checks populated maps/records, omitted lists, base-read failure, skip failure, selected empty lists and refill. Every stage checks vector cardinality, all valid ID lookups, returned record IDs and root cursor restoration. Populated data includes duplicate IDs and NONE records. All three unit lists are checked independently, including when sibling lists are omitted.

Five negative controls independently restore the old cleanup placement for one list; each fails the lookup-index consistency assertion after its list is emptied. No unsafe access is required to demonstrate the stale index.

Compiler flags: `-std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`, with ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Limits and next coverage

No real Firaxis parser/XML installation, arbitrary invalid positive ID, full translation-unit/MSVC7.1/DLL, cache, copying of owning metadata, player initialization or gameplay validation. Allocation exceptions and pointer-copy semantics remain unverified. Record readers in this fixture are deliberately stubs because the tested scope is the enclosing list/map lifecycle. A full native overlay remains pending broader integration review. Partial scoped work uses [skip ci]; no DLL build triggered or claimed.
