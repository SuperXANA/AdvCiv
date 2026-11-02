# UWAI invalid metadata IDs — 2026-11-02

Finding UWAI-20261102-08. Original source LeaderSpecificUWAIAspectWeights at d38c565a981984a7c34417a9d9529fec2bcd7165; reused UWAIWeightsDraft-ChatGPT parent f1d3125c0f35dff4c4a144c63a66d9437a270acd. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory found no changed original heads. Existing UWAI findings and installation fixes were read before this bounded follow-up.

## Concrete failure and correction

WarUtilityAspect.h xmlID overrides return NO_WARUTILITYASPECTAI (-1) when getInfoTypeForString cannot find their key. WarUtilityAspect::evaluate in WarUtilityAspect.cpp:96–97 forwards this ID to the leader override accessor and global weight accessor. Its reporting path at 165–170 forwards it to the global name accessor. The actual FAssert.h:92–96 expands release assertions to void(0); CvEnumMacros.h:249–257 shows that the generated global accessor then indexes and dereferences the vector without a native bounds check. A non-NULL leader override array similarly indexes -1. Assertions alone cannot make these accesses safe, including when debug execution continues after a diagnostic.

The supplied XML already contains all 29 required keys. This finding concerns missing/incomplete metadata, not an allegation that a supplied key is absent. No engine XML failure was induced.

- CvGameCoreDLL/UWAI.h:62–74, UWAI::aspectWeight and UWAI::aspectName: retain the bounds assertions, then explicitly reject a negative ID or an ID at/above the current metadata count. Return zero weight or a non-NULL empty wide string before any global metadata access.
- CvGameCoreDLL/CvInfo_Civilization.cpp:661–666, CvLeaderHeadInfo::getWarUtilityAspect: retain the bounds assertion, then return zero for an invalid ID before reading the optional override array.

Code commit: 800199eb609c9d1c139bb2bbe1bd5af8e59f9e4f. Only these three method bodies changed in production C++; original XANA markers, prior assistant fixes and all valid-ID behavior are preserved. Zero leader overrides retain their existing global-weight fallback. A missing aspect produces zero contribution instead of invalid memory access; the diagnostic remains available in Debug. No explicit C++ exceptions were introduced. No changes to XML, valid weights, lookup retry semantics, normal reporting or gameplay formulas.

## Host verification

tests/uwai-bounds/check.cpp contains the three actual corrected accessor definitions with stand-ins for globals, scaled and assertion reporting. Strict C++03 -Wall -Wextra -Werror -pedantic -fno-exceptions and ASan/UBSan each passed 252 combinations: zero/1/2/29/64 metadata entries, all valid IDs, negative and upper-bound IDs, INT_MIN/INT_MAX, NULL or populated leader arrays, and positive/zero/negative weights. Invalid IDs cause no global metadata lookup and retain assertion diagnostics; valid name pointer identity and values are checked. Restoring the original method bodies makes both invalid global lookups abort in the controlled metadata interface; ASan reproduces a heap-buffer-overflow in the original populated leader accessor. Leak detection disabled; no leak claim.

This fixture does not execute the real fixed-point implementation, complete production classes, Civ4 XML parser or engine debug dialogs.

## Full DLL validation

Prepared from the complete pinned baseline, overlaid the selected code snapshot while retaining all baseline-only files, and copied the actual dll-build workflow at 1cc8c3d24e9fe15126485de0b9e6604167caac36 with only the three provenance pins populated. All 872 baseline blob paths remain; all 364 selected DLL blobs match, with 351 root C/C++/header/inl sources. Independently downloaded all 11 feature-different root source files and verified their Git blob identities before native-manifest comparison.

Tested commit: b9c0c192e98a02d8003e88bf6f4e8741225a7494.
Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41402811119

Both Release and Debug completed successfully with compiler probes confirming _MSC_VER == 1310 (MSVC 7.1). Actual MSBuild Build.log files report 0 warnings and 0 errors. All four artifact ZIPs were downloaded, byte-size/SHA256 checked, extracted and compared entry-by-entry. Actual Build.log and BuildTiming.log, 351-file expected/actual content manifests, empty source-hash diffs and exact provenance pins were checked in both configurations. The source manifest SHA256 is db50619adb0940bae8026dae080488c14f2d2414374dc7c7c510f232a89dee0e. All 11 feature-different source files independently match both Git blob identities and native SHA256 records.

| Configuration | DLL artifact | Source diagnostics | DLL bytes | DLL SHA256 |
| --- | ---: | ---: | ---: | --- |
| Release | 13122058006 | 13122581116 | 6569984 | f607806b0ad6f7645f151b456cc1cb60e365693b5c8d2e08ac881435e40f558c |
| Debug | 13121968679 | 13121584643 | 25206784 | 6c6fb4e57ca763f52ada0b95b15834b59ca8ecde9da82db649114751ba1aba89 |

Both binaries are PE32 x86 DLLs. The Debug DLL's CodeView RSDS identity matches the supplied PDB: GUID 74913cea-8917-4a5b-90b7-cb865a64d1f9, age 1. PDB size 70618112 bytes, SHA256 302d2d205b2ab6c3467e24881ac83f57ae79cd7c0d05519f972436408e65f70f. Machine-readable archive/job/native evidence is in uwai-bounds-2026-11-02.json. This is an observed full DLL result, separate from the reduced host fixture.

## Remaining limits

Installed-game XML/XDR loading, actual default inheritance/cache behavior, localized report formatting and gameplay remain unexecuted. No claim of runtime recovery from every possible failed initialization; the change only guards these three known indexed accessors. The file-cache feature remains disabled in the baseline configuration. No arbitrary weight policy or wider metadata validation framework was invented. Do not repeat unchanged passing DLL builds; revisit source changes or concrete integration evidence.
