# LeaderFamilyRelations review and scoped refinement

Reviewed source: `ba88a0e713fb21fccff9ae2469164af78544bc2b`.
Read-only AdvCiv 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Workflow source: dll-build at `058e4d0e1760f76195071823d3e2dc85c81b7285`.
All original branch heads remain untouched.

## Findings and proposed code

**FAMILY-20261027-01 — first-impression bounds use incompatible storage.**
The new CvRelationInfo registers MIN_INT and MAX_INT defaults through CvXMLInfo.
Baseline CvInfo_Base.h:240,249 stores these fields in a vector of short and
safeIntCast<short> reports overflow without clamping; CvInfo_Base.cpp:428–446
uses that setter while reading. On the 16-bit-short/32-bit-int target, MAX_INT
narrows to -1, while MIN_INT narrows to 0. Thus an omitted positive maximum can
produce bounds [0,-1]: baseline range asserts in Debug, and in Release changes
a positive first impression such as +5 to -1. The source's negative default
also reverses the intended lower/upper limits before narrowing.

Refinement: CvRelationInfo now owns four full-width int bounds and reads the
same i-prefixed XML names explicitly. Defaults are [MIN_INT,0] for negative
values and [0,MAX_INT] for positive values. Missing fields preserve ordinary
first impressions, including full int endpoints. Read rejects reversed ranges.
Preserved source semantics: zero input stays zero, an explicit [0,0] pair opts
out for that sign, and configured ranges may intentionally cross zero. No
assumption that family relationships must always be favorable was introduced.

**FAMILY-20261027-02 — stale identity-specific relationship.**
CvPlayer::setPersonalityType assigns a new personality without rebuilding
m_eRelationship. Even when initLeaderRelationship is explicitly invoked, a
failed search or NO_LEADER leaves the previous relationship intact. Thus a
leader change can apply the old personality's relationship rules.
Refinement: rebuild after assigning the personality, before AI_updatePersonality.
Initialization first clears the old relationship and then selects the first
matching record. Existing reset, initialization and end-of-read reconstruction
hooks remain. Nothing new is serialized; the mapping remains derived from XML
and the restored personality. Duplicate owner records still select the first.
The public personality setter retains the baseline's valid-leader precondition:
AI_updatePersonality requires a non-NO_LEADER identity. The absent-identity test
exercises reconstruction directly after reset/load-style assignment.
The baseline's general attitude-cache refresh schedule is unchanged; this fix
corrects which relationship the next first-impression computation reads.

**FAMILY-20261027-03 — owning array and index validation.**
The original read allocates a new raw array without releasing the previous
allocation. Its implicit copy also shares that owning pointer. Lookup bounds
are assertions only, and the temporary legacy string-list loader can index
outside the leader array for a wrong key.
Refinement: use vector-owned values, clearing/replacing them on every read.
The baseline's already instantiated XMLTagPairIterator<RelationTypes> supplies
resolved pairs; both indices are checked before writing. Invalid pairs fail the
read and clear the partial mapping. Out-of-range lookups return NO_RELATION.
Copies own independent values.

**FAMILY-20261027-04 — declarations cannot compile.**
Both new classes lack their closing braces/semicolons; CvRelationInfo's
constructor has a dangling initializer colon; the const method declaration
does not match its definition. Corrected these and removed the meaningless
top-level const on the scalar relationship getter's return type.

Source links:
[classes and defaults](https://github.com/SuperXANA/AdvCiv/blob/ba88a0e713fb21fccff9ae2469164af78544bc2b/CvGameCoreDLL/CvInfo_Civilization.h#L509),
[bounds and mapping read](https://github.com/SuperXANA/AdvCiv/blob/ba88a0e713fb21fccff9ae2469164af78544bc2b/CvGameCoreDLL/CvInfo_Civilization.cpp#L1565),
[cache initialization](https://github.com/SuperXANA/AdvCiv/blob/ba88a0e713fb21fccff9ae2469164af78544bc2b/CvGameCoreDLL/CvPlayer.cpp#L6368),
[personality setter](https://github.com/SuperXANA/AdvCiv/blob/ba88a0e713fb21fccff9ae2469164af78544bc2b/CvGameCoreDLL/CvPlayer.cpp#L9307).

## Scope and verification limits

The selected source branch has no CIV4RelationInfos.xml or
CIV4RelationshipInfos.xml, nor their schemas. Its loader explicitly requests
both. This refinement adds no invented leader/family data or live XML fixtures;
it is a **compiled source foundation, not an install-ready gameplay package**.
Game startup/XML loading, live relationship effects, saves, personality-change
cache interactions and multiplayer behavior remain untested. The full-width
bounds read uses the same tag names the original generic loader would prefix
with i. Unknown enum names are diagnosed by the baseline iterator; index checks
cannot distinguish the wrong enum family when its numeric value happens to fit.
Future schemas and actual authored records must constrain those names.

The complete baseline is retained and only XANA additions are overlaid.
Unmarked differences in the old feature file copies are reconciled to pinned
1.14, retaining its newer upstream fixes. Original XANA 03-28-2026 boundaries
remain with dated refinement markers. The copied workflow retains the already
verified source-manifest, compiler-probe and build-cleanup adaptations used by
FreePromotionLoaderBuild-ChatGPT; no other feature code is imported.

`python3 tests/family-relations/check.py` compiles the actual new classes,
methods and setter against small game/XML stubs with C++03 and warnings as
errors. Tests cover integer extrema, positive/negative ranges, explicit zero
opt-outs, values above short range, reversed bounds, reload defaults, mapping
copy/reread, invalid indices, mapped/unmapped/absent personality changes, and
reconstruction. It also checks that reset/read hooks remain present.

The original-default diagnostic models the actual baseline's short narrowing
and runs the bundled baseline range helper; it is not a build of the original
broken branch. Stub enums permit dynamic runtime IDs beyond the small test
tables. ASan/UBSan passed with halt-on-error enabled and
`ASAN_OPTIONS=detect_leaks=0`; LeakSanitizer is blocked by this host's ptrace
environment. These fixtures are not Civ4's real XML parser or a DLL.

Native build commit: `5b41bb1d9598a514c99f8fe8e59333a884f56c0b`.
[Run 40564726051](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051)
uses this exact commit, the complete pinned baseline overlay and a sequential
Release/Debug matrix. The run and both jobs completed successfully. Both
configurations verified MSVC 7.1 (`_MSC_VER == 1310`), rebuilt with **zero
warnings and zero errors**, uploaded the requested exact DLL file and
completed build-output cleanup.

| Configuration | Job | Artifact |
|---|---|---|
| Release | 122402825430 | [DLL 12762701765](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051/artifacts/12762701765) |
| Debug | 122402825996 | [DLL/PDB 12763151213](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051/artifacts/12763151213) |

GitHub's artifact metadata names the exact code SHA above and reports both
archives unexpired. Validation covers compiler/linker logs, manifest checks
and exact-file artifact uploads. No downloaded PE inspection or game launch
was performed. All 872 baseline files are present; seven source files differ.

This final results update changes only this review and the test stub's
valid-personality precondition check. No DLL source changes occurred after the
successful native build; the workflow's path filter avoids another unchanged
build. The updated normal and sanitizer fixture runs both passed.

## Coverage checkpoint

All XANA blocks in LeaderFamilyRelations' nine DLL files were inspected at the
reviewed SHA; the unmarked text-manager files were not attributed to the mod.
Repository heads were unchanged since the prior pass. Existing SQLite, LLM,
spell-creation, vote-counter and free-promotion assistant work was left intact.
