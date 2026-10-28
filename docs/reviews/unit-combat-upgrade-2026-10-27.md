# Per-unit-combat upgrade-cost review — 2026-10-27

Source: PerUnitCombatUpgradeCostModifers at 3e8418a1b6840192f21af4650dcfce89a8c557d1.
Read-only baseline: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Build workflow: dll-build at 4249713909a3275c451f90986aeed94c4959a3bb.

## Scope

Carry the source feature into the complete pinned baseline, retain all baseline-only files, and preserve original XANA markers. Restore unrelated upstream differences in the older source files. The copied workflow changes its rsync source directory to ./CvGameCoreDLL/ for the complete repository layout. Its cleanup condition also uses always() with the existing build_started guard so failed builds do not skip cleanup.

## Repairs

- upgradePrice declares eCombatType but queries the undeclared eUnitCombat. Query the destination unit's combat type using eCombatType.
- Clamping after each mutation destroys trait contributions. +80, +80, -80 yielded +20. Preserve the raw sum, with the original [-100,100] effective bounds applied by the getter. The same sequence now yields +80.
- iUpgradeCostUnitCombat is declared boolean in the source XDR schema despite representing signed percentages. Declare it as an integer and retain optional list loading.
- Trait help processes zero modifiers using stale szText, and its translation requests a second parameter that is never supplied. Skip zero entries, use the localized combat description, and let setListHelp append combat links to a one-parameter prefix.
- The source appends a player map without changing format version 22. Pinned 1.14 already writes version 23. Version 24 explicitly stores the new raw map; older baseline saves rebuild from active traits without consuming map bytes.
- The unused CvUnit::getUpgradeCostModifier declaration has no implementation or callers. Retain the baseline header without that redundant declaration.

## Validation

Initial validation commit 55032b3440038ec247557a00de6637228ba4c81b failed in run 40456602311 during precompiled-header generation: C4622, C2220, C1854, followed by U1077/MSB3073. No DLL artifact was produced. Cleanup was skipped by its implicit success condition; the isolated workflow now permits guarded cleanup on failure as well.

Focused C++03 regression checks exercise the extracted production getter and updater for positive and negative trait removal, effective caps, and addition-order independence. Static XML checks confirm a well-formed schema and an optional integer modifier list.

DLL compilation and artifact status are available from the Actions run matching this branch's exact commit. XML loading, trait changes in a running game, and save/load round trips still require Civ4 runtime verification.

## Compatibility

Version 24 is scoped to this standalone feature branch. Other self-contained feature branches may independently use the same version number and need deliberate reconciliation when integrated. Existing saves written by the original unversioned feature implementation cannot be distinguished reliably from baseline version-22 saves and are not supported by the baseline migration path.

## Coverage

This pass covers upgradePrice, trait accumulation/reset, trait XML loading, trait help, and the player's read/write format. Prior completed review areas tracked separately: leader team-size attitude and timed-promotion source review.

## MSVC 7.1 build confirmation — 2026-10-28

The successful [DLL build run 40456936509](https://github.com/SuperXANA/AdvCiv/actions/runs/40456936509)
for `UnitCombatUpgradeBuild-ChatGPT` at commit
`e1f41d9bed34d4035fa09b506c9e14d377268fbb` completed Release compilation,
linking and DLL artifact upload. This proves that the assistant-refactored code
at that revision builds under MSVC 7.1 (the Visual Studio 2003 C/C++ compiler).

The remote environment initializes Visual Studio 2010's `vcvarsall.bat` and
uses MSBuild to invoke the NMake project. The machine-local
`R:\CvGameCoreDLL\Project\Makefile` and `Makefile.user` select the VS2003
compiler/toolchain. Visual Studio 2010 supplies the build tool environment;
the DLL's C/C++ compilation uses MSVC 7.1.
