# Hated-religion conversion cache refresh — 2026-11-01

HATED-20261101-08. Original HatedCivicReligionDiplomacy `a9c1a754b5e9b64e10ceaa22fd02fa78f3718785` remains read-only. Reused HatedDiplomacyDraft-ChatGPT parent `a13d837a06dc6f26508673e1ba242bc1c34b5296`. Correction `946f0dc7c4153354636db0abece3247f4554a53d`. Exact tested overlay `ebccd9c32ef9644762d280489dc3ba949832d55d`.

## Defect and correction

CvPlayer::setLastStateReligion, CvPlayer.cpp:9451–9462, refreshes attitudes in both directions after conversion, but its inherited filter admits only observers with a state religion or the converting player itself. AI_getHateReligionAttitude, CvPlayerAI.cpp:8071–8091, does not require the observer to have a state religion: NO_RELIGION differs from its hated religion, so it can dislike a target following that religion. Thus a religionless observer with a hated religion is skipped when the target adopts or leaves that religion. Its cached total can retain the old contribution until a later full attitude update.

At CvPlayer.cpp:9453, include observers whose getHateReligion()!=NO_RELIGION in the existing filter. Both existing directional AI_updateAttitude calls remain. Stateful observers and the converting player's self case are preserved; religionless observers without a hated religion remain skipped. Existing major-civ and downstream update guards remain. No religion preference, counter, sign, scoring formula, denominator or serialization change. The single added predicate has paired XANA date markers; earlier user/assistant edits are retained.

Concrete case: observer has no state religion and hates R; target changes from no religion to R. With base hated contribution -3 and no holy-city/counter adjustment, direct evaluation changes from 0 to -3, but the old filter does not recompute that observer's cached total. The repaired filter does.

## Scoped regression

tests/hated-refresh/check.py extracts the actual conversion-refresh condition and complete current AI_getHateReligionAttitude. A reduced player/personality/global interface models cache assignment only when the condition admits it. The ideology helper returns zero, fixing the counter-derived contribution for this scope; no population/fixed-point behavior is asserted.

648 cases pass strict C++03 -fno-exceptions -Wall -Wextra -Werror -pedantic, ASan/UBSan: three converter IDs, both distinct observer IDs, six before/after religion changes, three observer state religions, three hated religions and holy-city adjustment on/off. Check direct helper result versus refreshed modeled cache, filter inclusion/exclusion and self refresh. A negative control removes only the new predicate and fails cached==actual on a religionless affected observer. Leak checking disabled; UBSan halt-on-error.

This does not execute the entire conversion routine, real iterator eligibility, AI_updateAttitude's other terms/guards, engine diplomacy UI, worst-enemy updates or gameplay. No complete cache-coherence guarantee is made for other changes or third-party population effects.

## Full DLL preparation and result

Baseline `5970334b64a875b5cdb370c94fc9a98db4eacda6`, selected source `946f0dc7c4153354636db0abece3247f4554a53d`, actual current dll-build workflow `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`. Existing complete baseline-plus-feature assistant snapshot retained; all 872 baseline blobs present, 362 DLL blobs, 349 root source files, exactly eleven feature DLL files differ from baseline. Workflow copied with three exact provenance pins. Prior passing source and all previous counter/save/workflow fixes retained.

Run https://github.com/SuperXANA/AdvCiv/actions/runs/41344075881
Release job 124960033943 and Debug job 124960034185 both completed successfully. Both compiler probes explicitly verified _MSC_VER==1310 (MSVC7.1). Actual MSBuild Build.log files each report Build succeeded with 0 warnings and 0 errors. All four ZIPs downloaded, metadata size/SHA256 checked and extracted. Expected/Windows SHA256 source manifests match, source-hashes.diff is empty, all provenance pins match and all 349 source names match the exact tested tree. CvPlayer.cpp and CvPlayerAI.cpp independently hash to their manifest rows.

| Configuration | DLL artifact | Source diagnostics | DLL SHA256 |
|---|---|---|---|
| Release | 13098582664 | 13098274854 | 8541565cd4fcf899abf2099b4adf5a4209ec21a6269a0b41103cd6d271ce19cc |
| Debug | 13098731700 | 13098866059 | f60f56a4f8cf295fbd1e9af5751272b4e01ada47c692c947703908ac26c43630 |

Both binaries are PE32 x86 DLLs. Debug PDB matches the DLL's RSDS GUID e39c6668-a531-4617-bf1b-81eaee6fffb7, age 1. Both fresh BuildTiming logs inspected; common source manifest SHA256 686baedba8d5ddaef320845ed955cbaf08bf9d43f8b9a77586d3df75d6aa4f0c. Machine-readable details are in hated-refresh-2026-11-01.json. This verifies the corrected assistant overlay, not the unchanged original feature head.

Static AgentIterator.h:58–60 also confirms MAJOR_CIV with no relation predicate uses the MAJOR_ALIVE cache. The existing loop's scope is unchanged; the fixture does not execute the iterator or its cache lifecycle.

Original feature, baseline and workflow branches unchanged. No merge, PR, force push or invented implementation. Code/test commit skips CI; prepared overlay intentionally triggers both configurations; final report/ledger uses [skip ci]. Live new-game save/reload and XML/UI/game behavior remain untested.
