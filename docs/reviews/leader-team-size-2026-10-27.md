# Leader team-size attitude review — 2026-10-27

Source: LeaderSpecificTeamSizeAttitude at 9d0004e21a9e9f4df0abc89a4d7fb2e7dad98a58.
Read-only base: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Workflow source: dll-build at 96497ed4c6efdb7a899dd05dde4e324273feb183.

## Scope

Start from the complete base tree and overlay the three target CvGameCoreDLL files; keep base-only files. Add the optional schema field and an explicit zero loader default. Preserve the source formula, C++03 syntax, and original XANA tags. Copy the build workflow, changing only its rsync source to ./CvGameCoreDLL/ for the complete repository layout.

## Findings

1. The feature branch contains no XML schema declaration for iTeamSizeAttitudeChange. Adding the field to a leader document using the base schema cannot validate. Add the integer ElementType and an optional occurrence after iFavoriteCivicAttitudeChangeLimit.
2. The new field uses the CvLeaderHeadInfo helper's MIN_INT mandatory fallback when its inherited value is zero. Omitting a zero-valued tag can take the missing-mandatory assertion path. Pass zero explicitly while retaining inherited nonzero values through the existing helper.
3. The author's commit 1e8c13ca26d340c155e156eca63526e841be9edd explicitly defines positive values as tolerance and negative values as greater distrust. The current sign follows that intent. Negative values also produce penalties between equal-sized teams; retain pending a design decision.
4. GET_TEAM(ePlayer) resolves a PlayerTypes argument as a team index; the same expression is present in pinned 1.14, so this is an inherited concern rather than a newly introduced feature defect. A later focused fix should use TEAMID(ePlayer), including cases where player and team slots differ.

## Verification limits

DLL compilation does not validate Civ4 XML loading or gameplay. The XDR schema must be exercised in Civ4; static XML checks only establish structure and the optional integer declaration. The original source and 1.14 refs remain unchanged. Build status is recorded separately through the workflow run associated with this branch's exact commit.
