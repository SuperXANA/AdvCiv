# Leader team-size attitude review — 2026-10-27

Source: LeaderSpecificTeamSizeAttitude at 9d0004e21a9e9f4df0abc89a4d7fb2e7dad98a58.
Read-only base: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Workflow source: dll-build at 96497ed4c6efdb7a899dd05dde4e324273feb183.

## Scope

Start from the complete base tree and overlay the three target CvGameCoreDLL files; keep base-only files. Then narrow CvPlayerAI.cpp to the tagged feature change on the pinned baseline to remove unrelated snapshot drift. Add the optional schema field and an explicit zero loader default. Preserve the source formula, C++03 syntax, and original XANA tags. Copy the build workflow, changing only its rsync source to ./CvGameCoreDLL/ for the complete repository layout.

## Findings

1. The feature branch contains no XML schema declaration for iTeamSizeAttitudeChange. Adding the field to a leader document using the base schema cannot validate. Add the integer ElementType and an optional occurrence after iFavoriteCivicAttitudeChangeLimit.
2. The new field uses the CvLeaderHeadInfo helper's MIN_INT mandatory fallback when its inherited value is zero. Omitting a zero-valued tag can take the missing-mandatory assertion path. Pass zero explicitly while retaining inherited nonzero values through the existing helper.
3. The author's commit 1e8c13ca26d340c155e156eca63526e841be9edd explicitly defines positive values as tolerance and negative values as greater distrust. The current sign follows that intent. Negative values also produce penalties between equal-sized teams; retain pending a design decision.
4. Checked GET_TEAM(ePlayer) against CoreAI.h: the PlayerTypes overload correctly resolves TEAMID(ePlayer). No player/team index defect is present here.
5. The target CvPlayerAI.cpp is an older upstream snapshot: wholesale overlay reverses baseline changes unrelated to this feature, including specialist-commerce detection, unit upgrade ordering, event building-value scaling, and the strategy-hash rename. The refined version restores pinned 1.14 CvPlayerAI.cpp and reapplies only the XANA-marked team-size function; this preserves the author's feature and the current baseline fixes.

## Verification limits

DLL compilation does not validate Civ4 XML loading or gameplay. The XDR schema must be exercised in Civ4; static XML checks only establish structure and the optional integer declaration. The original source and 1.14 refs remain unchanged. Build status is recorded separately through the workflow run associated with this branch's exact commit.

## MSVC 7.1 build confirmation — 2026-10-28

The successful [DLL build run 40448128843](https://github.com/SuperXANA/AdvCiv/actions/runs/40448128843)
for `LeaderTeamSizeBuild-ChatGPT` at commit
`23b8e74ea630209d67deaa53475d31113bd614b1` completed Release compilation,
linking and DLL artifact upload. This proves that the assistant-refactored code
at that revision builds under MSVC 7.1 (the Visual Studio 2003 C/C++ compiler).

The remote environment initializes Visual Studio 2010's `vcvarsall.bat` and
uses MSBuild to invoke the NMake project. The machine-local
`R:\CvGameCoreDLL\Project\Makefile` and `Makefile.user` select the VS2003
compiler/toolchain. Visual Studio 2010 supplies the build tool environment;
the DLL's C/C++ compilation uses MSVC 7.1.
