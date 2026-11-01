# Gender complete overlay and native validation — 2026-11-01

Read-only source GenderSpecificDiplomacy `80e6ec595041cf335d5437b7bedea4fcaa61622b`. Assistant parent `a36846ebc68b5943a0ba69fbc064cfd3bba2767b`. Read-only baseline `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Reconciled selected source `04d6b9ff004ae47178958a1b047715f1130a99cd`. Tested complete overlay `5b122549e6df54bc61bcfbb19b7482cc9bec756e`. Current workflow copied from dll-build `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`, changing only the three provenance pins.

## Completed source reconciliation

Completed the eight implementation-file comparisons queued by gender-baseline-headers-2026-11-01.md. Against actual baseline and assistant code, 34 difference hunks contain marked feature additions/repairs and are retained. Fifty-seven unmarked older-upstream difference hunks are replaced with exact pinned-baseline content across five implementation files. This is baseline reconciliation, not a new Gender mechanics design or a claim that every old difference was user-authored.

- CvPlayer.cpp: restore vassal-trade eligibility, explicit trait handling for free city culture, current message-processing comments and base-player version-23 religion/corporation-count read/write logic matching the already restored short-encoded header members.
- CvPlayerAI.cpp: restore city-value percentile direction, deterministic experience-based upgrade ordering and budget/discount passes, safe upgrade-disband conditions, specialist-commerce accumulation, same-team Always War handling, alive-player valuation scope, corrected war-price placement, building-value scaling, own-victory-countdown handling and current strategy accessor. Retain all marked Gender history, attitude, ideology, paranoia and versioned counter changes.
- CyInfoInterface3.cpp: restore getReligionRequired to CvEventTriggerInfo::getReligionRequired, isPickOtherPlayerCity to its matching member, and event getNumUnits to CvEventInfo::getNumUnits. Gender bindings retained.
- CyPlayer.cpp: restore baseline void disbandUnit wrapper and string-return branches. Marked bounded Gender query wrappers retained.
- CvGameTextMgr.cpp: restore baseline wide plus/empty literals in existing wide-formatting calls and the existing commented Go To snippet. Marked wide Gender descriptions/lookup guards retained.
- CvInfo_Civilization.cpp, CvXMLLoadUtilitySet.cpp and UWAI.cpp contain only marked feature differences in this comparison and require no source change.

All XANA marker lines in each implementation file remain exactly the same and in the same order as the assistant parent. Six-header comparison/restored count widths and Gender info alias are documented separately; all prior fixes remain. No explicit C++ exception constructs introduced. No cross-feature DLL code imported.

## Exact complete build tree

Started from complete baseline, overlaid the selected assistant tree, and copied the current workflow. Verified all 872 baseline blobs exist, 362 DLL blobs and 349 root c/cpp/h/inl files. Exactly the fourteen supplied feature DLL files differ from baseline. Baseline-only sources retained; no machine-local Project change. Schema/example XML supplied by the user is preserved; no external basic-info schema or localization data invented.

Run https://github.com/SuperXANA/AdvCiv/actions/runs/41328157020
Release job 124912368732; Debug job 124912369043.
Both configurations completed successfully with verified MSVC7.1 compiler probes. Actual artifact Build.log files each report Build succeeded, 0 warnings and 0 errors. All four ZIPs were downloaded, checked against metadata byte counts/SHA256 and extracted. Actual expected/Windows source manifests match byte-for-byte, hash diffs are empty, all pins match and all 349 names match the tested tree. Fourteen feature source files were independently hashed against their manifest rows.

| Configuration | DLL artifact | Source diagnostics | DLL SHA256 |
|---|---|---|---|
| Release | 13091714548 | 13092471219 | ea2280efc30cd3e1027c4bccb2d5b6127e2da941d0debeee383abcaf6f0df69e |
| Debug | 13091992764 | 13091927955 | ee60278362f13d3a0a5dad5f4814ecd97cd6a19e03f830e1e2d40d70a61e6e68 |

Common source manifest SHA256: 65f1e538f40446dafc7f0e0557897058f773a6a7e12b1fa749b7b2c9bed5794d. Fresh BuildTiming logs inspected. Both DLLs are PE32 x86. Debug PDB matches RSDS GUID f5cc7806-c26e-48f6-a64d-7403a42bfc3e, age 1. Machine-readable details are in gender-native-2026-11-01.json. Native result applies to the exact corrected assistant overlay, not the untouched original source branch.

## Scoped regressions

Existing tests rerun against reconciled source: attitude helper 28,672 combinations; paranoia 1,280 configurations with two starting scores; generated basic-info alias/accessor lifecycle normal and ASan/UBSan with missing-alias negative control; versioned counter streams 252 cases across 1/2/4/19 players; bounded counter/update plus supplied schema/scalar checks; existing save/switch fixtures; 750 UI wide-description/bounds/pass cases. All pass strict host C++03 with warnings as errors and ASan/UBSan. The existing fixtures use engine, enum, XML, fixed-point or stream stand-ins and do not prove actual game behavior. Registration and direct C++ fixtures also use -fno-exceptions; other prior Python fixture flags are unchanged.

The large leader XML exceeded GitHub's contents-endpoint inline limit. Retrieved its Git blob and verified exact Git SHA1 4b901a3e35e266500a102ca82b5448f67a9816ab before the XML scalar check. Empty connector content was not interpreted as an empty source file. No XML source bytes were edited in this pass.

## Limits

Full DLL validation does not certify the external CIV4BasicInfoSchema.xml installation, Gender localization keys, actual Firaxis XML/schema parsing, gameplay/UI, fresh-game save/reload, multiplayer, arithmetic extrema or reciprocal preference design. XML file caching is disabled in baseline; no enabled-cache execution claimed. Existing fixtures and prior review records retain their own scoped qualifications. Original feature/baseline/workflow branches remain read-only. No PR, merge or force-push.
