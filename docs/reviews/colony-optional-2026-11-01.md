# Optional colony derivative leader — 2026-11-01

Source branch: LeaderSpecificColonySplitVassal at c2c8690c4854482f98ea3ceae2974586e5d1503d.
Assistant parent: d3c5e6aeb2c29606d10cfbb931205c709e01250b.
Correction: de358671fd7f7e3b9e9d1d396fde4632b11de243.
Exact full-overlay build: 0f66179997115e5c4c49715033f643fe282dd243.
Baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Workflow: f77f8a67cd17fdfa9d1c3f443d49005cee04421e.

## COLONY-20261101-02 — optional omission after leader index zero

CvLeaderHeadInfo::readPass2 called the generic SetInfoIDFromChildXmlVal helper for DerivativeLeader. For an int value, this reaches SetGlobalTypeFromChildXmlVal, which passes a NULL string default when the existing ID equals zero. The string reader then reports a missing mandatory tag when assertions are enabled. Zero is a valid leader index.

The concrete trigger is a modular leader record that sets DerivativeLeader to the first leader, followed by a later record for the same parent leader that omits this optional field. The monolithic pass and module passes revisit the final info record by Type; omission must retain the earlier value. Instead, the prior reader could raise the missing-tag assertion. Release storage normally remains zero, so this finding concerns a false Debug assertion rather than an established wrong-release selection.

The correction at CvInfo_Civilization.cpp:1090 reads the string with an explicit empty fallback and performs the existing info lookup only for nonempty text. Omitted or empty values retain the previous setting even when it is zero. NONE continues through the baseline lookup and clears to NO_LEADER. Explicit valid names still override. Unknown-name handling remains the baseline lookup behavior.

Original enclosing XANA 05-25-2025 markers are unchanged; the new lines have paired XANA 11-01-2026 markers. No class layout, eligibility filter, scoring weight, Random Personalities policy, schema, or live XML record changed.

## Source trace

- CvXMLLoadUtilitySet.cpp:696 registers leader info with two passes.
- CvXMLLoadUtilitySet.cpp:1403–1440 completes monolithic/module first passes, then runs second passes.
- CvXMLLoadUtilitySet.cpp:1239–1241 maps second-pass records by Type rather than positional order.
- CvXMLLoadUtility.h:424–429 routes the int ID through the generic helper.
- CvXMLLoadUtilityGet.cpp:814–823 chooses the NULL default for zero.
- CvXMLLoadUtilityGet.cpp:603–639 contains the string reader and missing-tag assertion.
- CvPlayer.cpp:17422–17425 remains the existing derivative-leader scoring consumer.

## Scoped checks

tests/colony-optional/check.py extracts the actual corrected readPass2 and actual string/generic reader bodies. Four prior IDs (-1, 0, 1, 3), five first tags and five second tags, under both mandatory-assert settings, produce 200 two-read sequences. Cases cover omitted tags, empty tags, NONE, leader zero and leader three.

All 200 pass strict C++03, -fno-exceptions, warnings-as-errors and pedantic checks, normally and under ASan/UBSan (LSan disabled). Reinstating the original field reader makes the assertion diagnostic check fail.

The test uses stand-ins for the FXml interface, strings, ID lookup and record shell; it models the baseline int-template dispatch. It does not execute Civ4's parser, module discovery/order, full info/default cloning, engine allocation, Python UI or live colony creation.

## Full DLL preparation and results

The tree was assembled from all 872 pinned-baseline blobs and the selected assistant overlays, retaining baseline-only files. All 362 selected DLL blobs match the prepared tree; there are 349 root source files. The actual current dll-build workflow was copied with only its three source/provenance pins changed.

Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41359029328

| Configuration | Compiler | Actual Build.log | Verified binary artifact |
|---|---|---|---|
| Release | MSVC 7.1, _MSC_VER 1310 | 0 warnings, 0 errors | [DLL](https://github.com/SuperXANA/AdvCiv/actions/runs/41359029328/artifacts/13104801439) |
| Debug | MSVC 7.1, _MSC_VER 1310 | 0 warnings, 0 errors | [DLL + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/41359029328/artifacts/13104003723) |

Both jobs and the run completed successfully. All four archives were downloaded, their API-reported ZIP sizes and SHA256 digests checked, and all entries extracted. The actual Build.log and BuildTiming.log files from both binary archives were inspected. Both source-verification archives contain matching 349-file expected/actual manifests, empty hash diffs and the exact baseline/selected-source/workflow/tested-commit provenance. Manifest names match the tested tree. All five feature DLL files plus the baseline string-helper file were independently checked against both exact Git blob hashes and the native SHA256 manifests.

Both DLLs are PE32 x86 DLLs. The Debug DLL's RSDS GUID 3593ef38-01fa-438b-afc1-50d30fb7766d, age 1, matches the extracted PDB. Detailed sizes, hashes, pins and artifact identities are in [colony-optional-2026-11-01.json](colony-optional-2026-11-01.json).

## Limits

Full native compilation is separate from executing installed XML and actual colony creation. A real modular configuration, the optional-tag assertion path, selected leader/civilization, UI and live gameplay still need engine validation. No runtime result is inferred from the host fixture or DLL build.
