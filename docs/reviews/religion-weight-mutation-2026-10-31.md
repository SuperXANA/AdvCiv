# Religion-weight mutation safety and native readiness — 2026-10-31

RELIGION-20261031-02; ORGLOAD-20261031-08. Read-only original UniqueCivicsReligions d0fc7c0f93320e112903416c17bb2a2030819d60. Reused CivicScrollDraft-ChatGPT parent 07bf390e44fca4927d0043d73fa276d45d8aa782. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory and global ledger 35a2a9e01ebec15ccfbffe47305a0811a65b7edb checked; prior organization/load/pass-3/type reports read. Workflow was the only changed original source and was reviewed first, including adoption at f77f8a67cd17fdfa9d1c3f443d49005cee04421e (companion workflow-log-set report).

## Completed religion-weight correction

Actual CvLeaderHeadInfo construction initializes m_piReligionWeightModifier to NULL. Its getter explicitly treats NULL as all-zero weights. The two mutation methods nevertheless dereferenced this optional pointer, including for a valid religion ID. Their bounds protection was assertion-only; release builds could index invalid IDs in getters or setters. The original source bodies match the pre-patch assistant bodies after only the already-delivered ReligonTypes spelling correction, so this is not an assistant-introduced issue.

[Source/fixture commit 3ac8bca1a805156652028fe71376fddc43eab428](https://github.com/SuperXANA/AdvCiv/commit/3ac8bca1a805156652028fe71376fddc43eab428), CvGameCoreDLL/CvInfo_Civilization.cpp:
- [getReligionWeightModifier, line 700](https://github.com/SuperXANA/AdvCiv/blob/3ac8bca1a805156652028fe71376fddc43eab428/CvGameCoreDLL/CvInfo_Civilization.cpp#L700): return zero for IDs outside [0,getNumReligionInfos()) before indexing; retain the existing implicit-zero NULL representation.
- [changeReligionWeightModifier, line 709](https://github.com/SuperXANA/AdvCiv/blob/3ac8bca1a805156652028fe71376fddc43eab428/CvGameCoreDLL/CvInfo_Civilization.cpp#L709): validate ID/nonzero delta and delegate to the checked setter.
- [setReligionWeightModifier, line 716](https://github.com/SuperXANA/AdvCiv/blob/3ac8bca1a805156652028fe71376fddc43eab428/CvGameCoreDLL/CvInfo_Civilization.cpp#L716): ignore invalid IDs; on the first nonzero write allocate and zero all religion slots before publishing the pointer, then set the requested weight. A zero write to an absent array remains an allocation-free no-op.

This chooses safe zero/no-op behavior for invalid array IDs and preserves the getter's existing zero-default policy. No class member/layout, enum signature, XML tag, weight arithmetic for bounded valid inputs, byte format or unrelated civic-weight behavior changed. All 28 existing XANA marker lines in this implementation remain byte-for-byte and in order. The previous enum/copy/UI/loading refinements are retained.

## Scoped verification

Run python tests/religion-weight-mutation/check.py.

2,695 C++03/ASan/UBSan cases pass against the actual three complete method bodies using a reduced owning leader-info shell and GC/enum stand-ins. Counts 0 through 6, absent/preallocated maps, negative/sentinel/valid/upper-out-of-range IDs, bounded positive/negative/zero values and deltas are checked for correct target values, adjacent-slot preservation and allocation-free zero/invalid writes. The fixture enum includes a high sentinel so the tested out-of-array IDs remain within its representable enum range; this does not certify actual engine enum/category IDs.

Injected first-write new[] failures preserve the NULL/implicit-zero state, and subsequent retries succeed. Successful arrays are released by the shell destructor; a logical allocation counter checks ownership. Three independent negative controls remove lazy allocation, getter bounds or setter bounds. UBSan reports a null-pointer store for the first; ASan reports heap-buffer-overflows for the latter two.

The prior actual organization-header/getter fixture also passes its 15 getter and 20 religion-weight cases unchanged. Flags: -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined; ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1. No warning suppression, LeakSanitizer or full-class/engine claim.

Extreme signed addition overflow, registry growth after allocation, complete ownership/copy/cache/loading behavior and gameplay remain outside this bounded refinement. The native attempts below stop before compiling the changed CvInfo_Civilization.cpp translation unit, so they do not certify these method bodies under MSVC.

## Native overlay and first failure

Complete pinned baseline then all 24 selected source DLL files overlaid, retaining every baseline-only file. Recursive blob check found zero missing baseline files and zero supplied-DLL mismatches; resulting DLL tree has 362 blobs and 349 hashed root source files. Existing source Python/UI/docs/tests retained; no other feature's DLL code integrated. Workflow source 4dec9b6502486a8b045d1f2a44ec9d4569162613 copied with the isolated timing-log deletion-list correction and exact provenance pins. Protected VM Project configuration unchanged.

First selected source 3ac8bca1a805156652028fe71376fddc43eab428; prepared tested commit 5a31326b440238e97d8f831da17c6bd9631f8216. [Run 41224201639](https://github.com/SuperXANA/AdvCiv/actions/runs/41224201639) completed with both Release and Debug failure.
Actual Build.log: CvInfo_Civics.h:77 C2440 int-to-CivilizationTypes and :78 C2440 int-to-LeaderHeadTypes, followed by NMAKE U1077/MSB3073. Each summary: 0 warnings, 4 errors including wrappers.

ORGLOAD-20261031-08 — [cast correction 3c7b7f01d41396cad0ced2b4d38fdaf5cbb546b1](https://github.com/SuperXANA/AdvCiv/commit/3c7b7f01d41396cad0ced2b4d38fdaf5cbb546b1), [CvInfo_Civics.h:77–78](https://github.com/SuperXANA/AdvCiv/blob/3c7b7f01d41396cad0ced2b4d38fdaf5cbb546b1/CvGameCoreDLL/CvInfo_Civics.h#L77): explicitly cast the stored int prerequisite IDs to their already-declared enum return types. Integer fields, ID-resolution policy and all six existing XANA marker lines in this header remain. No category validity or gameplay change invented.

First-run artifacts downloaded/extracted: Release failure logs 13050164675, source diagnostics 13051106020; Debug failure logs 13051145948, source diagnostics 13051036171. Both expected/actual 349-entry manifests match; digest 2c59de8f76fad331bfc7ff5c1a161ea8c7f8b13664473303ff5594dd872e286a. Actual Build.log and BuildTiming.log inspected.

## Exact final native blocker and skip

Selected corrected source 3c7b7f01d41396cad0ced2b4d38fdaf5cbb546b1; tested prepared commit 596f539981627e0373d557804f80410e248dc6c0. [Run 41224382638](https://github.com/SuperXANA/AdvCiv/actions/runs/41224382638) completed with both configurations failing.

The enum-return errors are gone. Actual Build.log now reports:
CvCity.cpp(13582): error C3861: 'changeUnhappinessTimer': identifier not found, even with argument-dependent lookup.
NMAKE U1077 and MSB3073 follow. Both summaries: 0 warnings, 3 errors including wrappers. No DLL artifact was produced.

[Original source CvCity::setCityChangesDueToMinorReligionLeaving](https://github.com/SuperXANA/AdvCiv/blob/d0fc7c0f93320e112903416c17bb2a2030819d60/CvGameCoreDLL/CvCity.cpp#L13576) contains the explicit XANA TODO: an unhappiness timer is needed for anger when a minor religious organization leaves, followed by the unimplemented call. Actual supplied CvCity.h has no such API/state, supplied CvCity.cpp has only this use, and the pinned baseline CvCity.h also has no UnhappinessTimer API. Existing happiness/hurry/conscript/defiance timers have separate semantics.

This is missing user feature implementation, not a typo that can safely be mapped to another timer. Do not add a no-op, suppress the call, substitute another anger source, or invent timer magnitude/stacking/decay/save/UI policy just to obtain a build. Skip original source d0fc7c0f93320e112903416c17bb2a2030819d60 and associated assistant integration until changed user work supplies the missing details. Other whole-feature scopes remain queued behind this source readiness gate. This is not a CvPlot size-assertion stop.

Final-run artifacts downloaded/extracted: Release failure logs 13050976411, source diagnostics 13050164909; Debug failure logs 13051760256, source diagnostics 13051271027. Exact tested-commit/configuration/baseline/source/workflow pins verified in all four diagnostics across both runs. Final expected/actual 349-entry manifests match; digest 752e992a06d65ee09794fd5d778a5b319aefa921e26b0f40813b18d506749c2b. All eight ZIPs from both runs were extracted, actual logs inspected, no DLLs present. Neither local fixtures nor these failed compiler runs are full DLL validation.

Source draft/cast and evidence commits use [skip ci]; the two preparation commits intentionally triggered the two observed matrices. Original branches, baseline and newer edits remain intact. Completed scoped fixes are reviewable code; missing unhappiness mechanics are recorded for user development, not fabricated.
