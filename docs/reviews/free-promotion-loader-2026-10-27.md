# Per-unit-combat free-promotion loader review

Source: PerUnitCombatFreePromotionTraits at
`c122a8c130b6e47760aade7d2d438c798dca8951`.
Read-only 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Workflow source: dll-build at `058e4d0e1760f76195071823d3e2dc85c81b7285`.

## Findings and committed refinements

- **FREEPROMO-20261027-01 — template visibility and scalar type.**
  Source CvXMLLoadUtility.h:191–195 lacks the terminating semicolon on its
  function declaration. The template body lives in CvXMLLoadUtilitySet.cpp,
  while CvInfo_Civilization.cpp instantiates it in a different translation unit.
  No explicit instantiation is supplied. Furthermore, the actual baseline
  ArrayEnumMap2D inherits ValueType/defaultValue for its outer map: these are
  an inner-map pointer/null, not the inner bool. Reading XML into ValueType and
  passing it to insert therefore uses the wrong type. Move the full definition
  into the header and explicitly read bool values. This helper is intentionally
  for boolean maps; it does not promise arbitrary scalar map support.
- **FREEPROMO-20261027-02 — value cursor and Release bounds.**
  Source CvXMLLoadUtilitySet.cpp:2099–2117 calls NextSibling to reach the
  scalar value, then GetNextXmlVal, advancing past that value. Use GetXmlVal
  on the current node. Both resolved key indices now receive lower and upper
  bounds checks before insert in all configurations; source upper checks were
  assertions only. Invalid dimensions return before traversal. Every successful
  descent is paired with a parent operation, including empty/malformed entries.
  Explicit false values are inserted too, so a later duplicate can clear an
  earlier true value.

Original source links:
[declaration](https://github.com/SuperXANA/AdvCiv/blob/c122a8c130b6e47760aade7d2d438c798dca8951/CvGameCoreDLL/CvXMLLoadUtility.h#L191),
[loader](https://github.com/SuperXANA/AdvCiv/blob/c122a8c130b6e47760aade7d2d438c798dca8951/CvGameCoreDLL/CvXMLLoadUtilitySet.cpp#L2044),
[trait call](https://github.com/SuperXANA/AdvCiv/blob/c122a8c130b6e47760aade7d2d438c798dca8951/CvGameCoreDLL/CvInfo_Civilization.cpp#L1273).

## Scope and integration limits

This branch is a **loader foundation**, not a completed gameplay mechanic.
The original branch's XANA blocks only add storage and loading; its CvPlayer,
CvPlayerAI and text-manager files contain no marked consumers of this map.
There is no public trait query for this map and no matching schema/data addition
in the selected branch. Consequently no new promotion distribution is enabled
here. Gameplay consumers, XML schema and help text remain separate integration
work. Static inspection of baseline CvXMLLoadUtilitySet.cpp:632,669–670 confirms
UnitCombat and Promotion load before Trait, making both counts available at
this call. Actual game XML loading still needs validation. No save format or
existing promotion rules change.
The generic global enum resolver can detect unknown/out-of-range indices but
cannot by itself reject a wrong enum family whose numeric index happens to fit.
The eventual schema should constrain those key names.

Baseline files were retained in full. The selected branch's marked trait storage,
loader call and helper were overlaid; the helper definition was relocated and
refined as above. All unmarked differences in the eight older source copies were
reconciled to current pinned 1.14. Original XANA 11-22-2025 boundaries remain, with
a dated refinement annotation. This avoids importing unrelated old upstream code.

## Verification

`python3 tests/free-promotion-loader/check.py` compiles the actual loader
extracted from the modified header under strict C++03 with warnings as errors.
It checks asymmetric dimensions in both directions, true/false duplicate keys,
missing roots, comments, empty entries, missing/bad values, unknown keys,
out-of-range keys, zero dimensions, reload/reset and final parser position.
The cursor and map are stubs; the map intentionally exposes pointer ValueType
and a scalar-bool insert overload like the relevant baseline API.
Cursor operations were checked against baseline CvXMLLoadUtility.cpp:258 and
CvXMLLoadUtilityGet.cpp:107,177,335: SkipToNextVal skips comment siblings,
GetXmlVal reads the current node, and GetNextXmlVal advances first.

ASan/UBSan also passed with `ASAN_OPTIONS=detect_leaks=0`.
LeakSanitizer itself is blocked by this host's ptrace environment.
These fixtures are not a DLL, game XML parser or in-game validation.

The copied build workflow uses the complete pinned overlay, preserves machine
Project configuration, checks the root-source manifest, removes stale root
source files only, clears generated build outputs and probes MSVC 7.1 before
sequential Release/Debug rebuilds. These safety refinements match the already
validated LLMDiplomacyTextBuild-ChatGPT workflow; no LLM feature code is imported.
Native results:

- Initial commit `a5cabdd77a7b547c3094d075dd17b8452e6281aa`,
  [run 40556363676](https://github.com/SuperXANA/AdvCiv/actions/runs/40556363676):
  Release and Debug completed successfully, each with zero warnings and errors,
  verified MSVC 7.1, successful uploads and output cleanup.
  Artifacts: Release 12757242896; Debug/PDB 12756024555.
- An expanded fixture then covered comments before keys and between an outer
  key and its list. The latter needs SkipToNextVal before descending. Corrected
  code commit `f5c7d3e40717fa2ac19324c70ee38882473632e3` includes that change
  and the expanded passing fixture.

Final code commit `f5c7d3e40717fa2ac19324c70ee38882473632e3` passed
[run 40556617050](https://github.com/SuperXANA/AdvCiv/actions/runs/40556617050).
Both configurations verified `_MSC_VER == 1310`, rebuilt successfully with
**zero warnings and zero errors**, uploaded their exact requested artifact files
and completed output cleanup. GitHub reports the run and both jobs successful.

| Configuration | Job | Artifact |
|---|---|---|
| Release | 122376438039 | [DLL 12757312692](https://github.com/SuperXANA/AdvCiv/actions/runs/40556617050/artifacts/12757312692) |
| Debug | 122376438572 | [DLL/PDB 12757513382](https://github.com/SuperXANA/AdvCiv/actions/runs/40556617050/artifacts/12757513382) |

Artifact metadata names this exact final code SHA and reports both archives
unexpired. Validation here comprises native compiler/linker logs, source-manifest
checks and successful exact-file upload; no downloaded PE inspection or game
launch was performed. All 872 baseline files remain; only the three source
files identified above differ from the pinned baseline. This results update
changes documentation only, so its path-filtered workflow does not rebuild.

## Coverage checkpoint

Reviewed all XANA blocks present in the selected eight DLL files at the pinned
feature head. SidSaysPatch at 2971698219a7a586718599b99fe50a51b02386ad was also
inspected: its two DLL files have no XANA blocks, so no upstream-only finding was
attributed to the mod. Newly present LLM and spell-creation assistant branches
were checked for concurrent review scope and left untouched. Prior vote-counter,
SQLite, colony and promotion-XP findings were not reopened in this pass.

## MSVC 7.1 build confirmation — 2026-10-28

The successful [DLL build run 40556617050](https://github.com/SuperXANA/AdvCiv/actions/runs/40556617050)
for `FreePromotionLoaderBuild-ChatGPT` at commit
`f5c7d3e40717fa2ac19324c70ee38882473632e3` completed Release and Debug compilation,
linking and DLL artifact upload. This proves that the assistant-refactored code
at that revision builds under MSVC 7.1 (the Visual Studio 2003 C/C++ compiler).

The remote environment initializes Visual Studio 2010's `vcvarsall.bat` and
uses MSBuild to invoke the NMake project. The machine-local
`R:\CvGameCoreDLL\Project\Makefile` and `Makefile.user` select the VS2003
compiler/toolchain. Visual Studio 2010 supplies the build tool environment;
the DLL's C/C++ compilation uses MSVC 7.1.

Both configuration logs additionally confirm the compiler probe:
`Verified selected compiler: _MSC_VER == 1310 (MSVC 7.1).`
