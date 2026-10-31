# Preference lookup-map ID bounds — 2026-10-31

PREFERENCE-20261031-07. Read-only source LeaderCivilizationDecisionPreferences `aac03388283a5ac316f6a19f6e3754a7435b6511`; reused PreferenceFrameworkDraft-ChatGPT parent `afb7f7ce941698df0c904a233c1120dacb177970`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no original-head changes against global ledger c23d090f23e88ccf600d58cb89f76a5062030622. Prior preference cursor and list/map lifecycle work was read and preserved.

[Correction and fixture dcd135136f8b3fabdc87bbe39a89f0cac6d8d7f9](https://github.com/SuperXANA/AdvCiv/commit/dcd135136f8b3fabdc87bbe39a89f0cac6d8d7f9).

## Defect

The five enclosing loaders allocate lookup maps to their corresponding GC info counts, but accept every record ID other than NO_* before indexing those maps. The record declarations in CvXMLStructs.h store IDs as int, and their read methods pass those ints to SetInfoIDFromChildXmlVal. The pinned baseline utility's InfoIDFromChild<T,false> path delegates to global info lookup without the enum-bound assertion of its enum specialization. A successful global lookup from another category can therefore yield a nonnegative ID beyond this map's size. The enclosing static_cast to a category enum did not validate that size.

Zero-capacity tables plus ID zero, or a positive ID equal to the table count, can write outside the allocation. Non-sentinel negative values are likewise unchecked, although ordinary unknown-name lookup normally supplies -1.

## Completed correction

Keep each record ID as int until validation, require 0<=ID<the corresponding GC count, then append the accepted record and write the map using that checked int. No enum conversion is needed for the raw map index. Records outside range are skipped, extending the existing NO_* skip behavior; return/error/default policy is not otherwise changed.

| Reader/list | File | Guard line |
| --- | --- | ---: |
| CvTechPreferenceInfo::read | CvInfo_Civilization.cpp | 1628 |
| CvEventPreferenceInfo::read | CvInfo_RandomEvent.cpp | 2163 |
| CvUnitPreferenceInfo::read, UnitCombat | CvInfo_Unit.cpp | 2647 |
| CvUnitPreferenceInfo::read, UnitClass | CvInfo_Unit.cpp | 2681 |
| CvUnitPreferenceInfo::read, Unit | CvInfo_Unit.cpp | 2715 |

Valid record order, last-duplicate indexing, NONE behavior, omitted lists, existing cleanup and XML cursor movement remain unchanged. Earlier XANA boundaries and edits remain; each new guard has a dated annotation.

## Verification

Run `python tests/preference-bounds/check.py`. It extracts actual full enclosing class declarations and implementations from constructors through read, including destructors and lookup/record getters. The globals, XML tree/cursor and record readers are stand-ins. Earlier actual-record-reader fixtures remain separate evidence; this test injects raw IDs at that interface.

15,552 strict C++03/ASan/UBSan configurations passed: six rotations of category capacities 0–5, all pairs of nine input IDs (INT_MIN,-2,-1,0,1,5,6,99,INT_MAX), and all 32 masks of present/omitted replacement lists. Each case first populates valid initial state, then loads a mix of boundary IDs, checks accepted vector cardinality/order, every valid lookup and record ID, last-duplicate behavior, independent category counts and cursor restoration.

Five negative controls restore an ID!=-1 guard for one list at a time while restricting inputs to nonnegative IDs. Every control reproduces ASan heap-buffer-overflow at a lookup-map write. An initial broad negative probe reached an ASan write SEGV for INT_MIN; the focused nonnegative controls establish the ordinary upper-bound defect independently of extreme negative values.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Limits / remaining scope

Range checks cannot prove category correctness for a wrong-category global ID whose numeric value happens to be within range. No new keyed schema, type registry or authoring contract was invented. Full category validation, real parser/XML installation, owning-info copying/default inheritance/cache, player initialization and complete engine/native integration remain open.

No full MSVC7.1/DLL/game result. Partial scoped code uses [skip ci]; no DLL run triggered. This is not a validation of the real global-ID lookup or enum ABI, which are stubbed in the fixture. Original branches and baseline remain untouched.
