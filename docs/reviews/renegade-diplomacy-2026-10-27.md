# Renegade-team diplomacy review

Source: LeaderSpecificRebelliousTeamDiplomaticDecisions at
`4b24f235ef0056a6dcab56b0dada3dcd0909798d`.
Read-only 1.14: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Workflow source: dll-build at `058e4d0e1760f76195071823d3e2dc85c81b7285`.

## Findings and proposed refinements

**RENEGADE-20261027-01 — UI queries consume synchronized RNG and reroll.**
The XANA return in AI_isWillingToTalk uses SyncRandSuccess100, even when bAsync
is true. This query is called by the interface; its baseline comment explicitly
notes repeated EXE calls. Baseline CvGame.h:1289–1292 expands the macro into a
draw from the shared game RNG for chances strictly between 0 and 100. Clients
that inspect diplomacy differently can therefore advance the shared RNG
differently. Repeated checks can also disagree within one unchanged state.
Endpoints 0 and 100 already short-circuit without a draw; those are not claimed
to have this consumption problem.

The refinement creates a local CvRandom, seeded by an unsigned 32-bit mix of
the game's saved initial synchronization seed, game turn, speaker ID, recipient
ID and personality. It draws only from that local object. Both async and
synchronized queries return the same result in unchanged game/UI context;
neither global RNG changes. Unsigned overflow in
the seed mix is intentional and defined. The local generator's init/reset/get
paths were read in baseline CvRandom.cpp; null-log draws only update the local
seed, with no global RNG operation.
CvGame::getInitialRandSeed().second reads the saved initial seed, not mutable
RNG state. Its read/write paths at baseline CvGame.cpp:8984–8985,9287–9288 were
checked. CvInitCore's separate startup seed is unsaved and is not used.

This deliberately proposes a **per-turn willingness roll**, replacing the
original per-call roll. A new turn permits a new answer, without a persistent
cache, new save fields, or dependence on UI call order. It does not add
independent war declarations, grant peace authority or change negotiation terms.
The override remains limited to an AI member of a human-controlled team, at
war with the recipient, after existing relationship/vassal/human checks. All
other baseline guards and UWAI behavior remain.

**RENEGADE-20261027-02 — optional field reads a mandatory-value sentinel.**
The schema makes iRenegadeFromTeamDiploProb optional, but its loader omits an
explicit default. CvLeaderHeadInfo::GetChildXmlValByName defaults to MIN_INT
when the initial member is zero and no inherited nonzero value exists.
Use an explicit zero default and clamp configured values to [0,100]. This
preserves nonzero XML-default inheritance and explicit zero overrides. Missing
values now mean no renegade override, with no invalid percentage left stored.

**RENEGADE-20261027-03 — a marked value violates its declared XDR order.**
The source LEADER_BARBARIAN record puts the new value before
iDemandRebukedWarProb; the schema puts it after that element. The overlay
places matching marked values after iDemandRebukedWarProb and before iRazeCityProb.
The schema remains optional and its integer declaration is retained.

Source:
[random query](https://github.com/SuperXANA/AdvCiv/blob/4b24f235ef0056a6dcab56b0dada3dcd0909798d/CvGameCoreDLL/CvPlayerAI.cpp#L7470),
[XML read](https://github.com/SuperXANA/AdvCiv/blob/4b24f235ef0056a6dcab56b0dada3dcd0909798d/CvGameCoreDLL/CvInfo_Civilization.cpp#L961),
[schema order](https://github.com/SuperXANA/AdvCiv/blob/4b24f235ef0056a6dcab56b0dada3dcd0909798d/Assets/XML/Civilizations/CIV4CivilizationsSchema.xml#L240),
[source first record](https://github.com/SuperXANA/AdvCiv/blob/4b24f235ef0056a6dcab56b0dada3dcd0909798d/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml#L42).

## Baseline and authored data preservation

The complete current 1.14 baseline is retained. All marked additions in the
three DLL files and the schema were ported, with the refinements above; older
unmarked code differences were reconciled back to 1.14. In particular, the
baseline's same-team exception to its Always War UI guard is retained.
Original XANA 11-08-2025 markers remain, with a dated RNG refinement marker.

The source has 149 leader records, with this field marked in 45. The overlay
keeps 1.14's 54 records and ports the two matching marked values
(LEADER_BARBARIAN and LEADER_DEFAULTS, both zero). It does not import the
unmarked extra roster or unrelated older leader settings. All 45 marked
source values, including the 43 extra leader settings, are preserved in
tests/renegade/source-values.xml as an **inactive provenance fixture**.
It is not an engine XML file. Original source branch data remains untouched.
The demonstration therefore enables no new live renegade behavior by default.

## Verification

`python3 tests/renegade/check.py` compiles the actual complete modified
AI_isWillingToTalk method and probability-read fragment under strict C++03
with warnings as errors, using small game/XML stubs and the actual baseline
RNG arithmetic, percentage macro and XML-default helper.
The original complete willingness method is compiled separately in the fixture
to reproduce shared-seed changes and inconsistent answers on repeated 40%
queries. This is not a DLL build of the original feature.

For the refinement, 40,000 repeated async/synchronized probes across 1,000
turns agree within each context and leave both global RNG seeds unchanged.
The tests cover recipient variation, nonconstant outcomes, endpoints,
missing/default/inherited/explicit values, clamping and existing diplomacy gates.
The sample outcome-count check only rules out a constant result; it does not
establish a formal statistical distribution. All 54 leader records were checked
against schema child ordering, and all 45 extracted probabilities are in range.
ASan/UBSan also passed with halt-on-error and
`ASAN_OPTIONS=detect_leaks=0`; LeakSanitizer is blocked by host ptrace.

The copied workflow retains the tested compiler probe, root-source manifest,
shared workspace concurrency, stale-root-source protection and output cleanup
adaptations used by CityBonusDiplomacyBuild-ChatGPT. No resource-diplomacy
feature code is imported.

Native code commit: `dc22ea9a64cb4c2ee45af31d4c20191e08e8247d`.
[Run 40583685157](https://github.com/SuperXANA/AdvCiv/actions/runs/40583685157)
uses this exact commit and the complete pinned overlay. The run and both jobs
completed successfully. Both configurations verified MSVC 7.1
(`_MSC_VER == 1310`), rebuilt with **zero warnings and zero errors**, uploaded
their exact requested DLL files and completed generated-output cleanup.

| Configuration | Job | Artifact |
|---|---|---|
| Release | 122469460621 | [DLL 12770887082](https://github.com/SuperXANA/AdvCiv/actions/runs/40583685157/artifacts/12770887082) |
| Debug | 122469461006 | [DLL/PDB 12770842991](https://github.com/SuperXANA/AdvCiv/actions/runs/40583685157/artifacts/12770842991) |

GitHub artifact metadata names the exact code SHA and reports both archives
unexpired. Validation covers native compiler/linker logs, source-manifest
checks and exact-file uploads. No downloaded PE inspection was performed.
All 872 baseline files remain; only the three selected DLL files and the two
selected civilization XML files differ. This final results update changes
documentation only and does not trigger another unchanged DLL build.

These fixtures and a native build do not establish Civ4 XML acceptance,
in-game negotiation behavior, game-load behavior, multiplayer synchronization
or exact game balance. No multiplayer session or game launch was performed.
The disabled legacy binary info-cache path remains untested.

## Coverage checkpoint

All XANA blocks in this source branch's three DLL files, schema and leader data
were read. Branch heads were unchanged since the previous pass. Completed
family/resource diplomacy, SQLite, LLM and other assistant branches were not
edited or rebuilt.

## MSVC 7.1 build confirmation — 2026-10-28

The successful [DLL build run 40583685157](https://github.com/SuperXANA/AdvCiv/actions/runs/40583685157)
for `RenegadeDiplomacyBuild-ChatGPT` at commit
`dc22ea9a64cb4c2ee45af31d4c20191e08e8247d` completed Release and Debug compilation,
linking and DLL artifact upload. This proves that the assistant-refactored code
at that revision builds under MSVC 7.1 (the Visual Studio 2003 C/C++ compiler).

The remote environment initializes Visual Studio 2010's `vcvarsall.bat` and
uses MSBuild to invoke the NMake project. The machine-local
`R:\CvGameCoreDLL\Project\Makefile` and `Makefile.user` select the VS2003
compiler/toolchain. Visual Studio 2010 supplies the build tool environment;
the DLL's C/C++ compilation uses MSVC 7.1.

Both configuration logs additionally confirm the compiler probe:
`Verified selected compiler: _MSC_VER == 1310 (MSVC 7.1).`
