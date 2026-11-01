# First-impression UWAI storage — 2026-11-01

Source: FirstImpressionDiplomacyModifiers `cc764ad80e89f751f809998a61a23225254109f2`.
Assistant parent: `3589d41a23b722a2b4bac89d0f32c759a4599d85`.
Correction: `b0802e9365fea80de4bedc41fa920a122dd48ba2`. Tested overlay: `08a82f722a9c6d56d94d0ed68f61927796dc7989`.
Finding: FIRST-20261101-01.

## Defect and correction

In UWAI::applyPersonalityWeight, UWAI.cpp:215–222, the XANA first-impression addition used the baseline's static aiDevNull[100] when m_piFirstImpressionModifier was NULL. It then appended one indexed pointer for every leader. CvXMLLoadUtility.h:261–302 explicitly retains NULL for absent/all-zero lists; this is a supported metadata state, not a fabricated invalid pointer. With UWAI_PERSONALITY_PERCENT other than 100 and more than 100 leader definitions, the weighting loop reads/writes beyond that buffer. Even below the bound, writes to the sink never reach the NULL-backed leader's getter, and shared fallback cells can be mutated between rows.

The scoped correction materializes a zero-initialized int array using GC.getNumLeaderHeadInfos() for a NULL first-impression list before collecting pointers. Existing non-NULL arrays retain their addresses and signed values. The normalizer can now retain its computed results in the owning metadata; the existing copy constructor and destructor already copy/free this field. The weight==100 early return, existing median/rounding algorithm, other personality fields, and XANA markers are unchanged. Other baseline aiDevNull uses are outside this feature repair.

## Host checks

tests/first-weight/check.py extracts the actual XANA block. Sixteen cases cover null and populated lists at leader counts 0, 1, 2, 99, 100, 101, 149 and 257, signed values, pointer ownership, persistent writes and repeat collection. Strict C++03 with -fno-exceptions/-Wall/-Wextra/-Werror/-pedantic passes normally and under ASan/UBSan (leak checking disabled, UBSan halt-on-error).

Negative controls using the old actual block fail the retained-storage assertion; a separate 149-leader NULL case reproduces ASan global-buffer-overflow on the original static sink. Globals, enum iteration and leader metadata are host stand-ins; these tests do not execute the game's XML parser, exact scaled-number median/rounding implementation or Civ4.

## Full DLL preparation

Complete pinned baseline `5970334b64a875b5cdb370c94fc9a98db4eacda6` is retained: all 872 baseline blobs exist. The source overlay contains the five authored DLL files; all remaining DLL files retain baseline blobs. Previous debug-loader and declaration-order fixes are preserved. All supplied XML blobs match the source snapshot; no authored leader values are invented. The current workflow is copied from dll-build `f77f8a67cd17fdfa9d1c3f443d49005cee04421e` with only its three provenance pins substituted.

Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41286570324
Both jobs completed successfully: Release 124788967899 and Debug 124788967990. Both compiler probes verified _MSC_VER==1310 (MSVC 7.1). Actual MSBuild Build.log files report 0 warnings and 0 errors, with fresh BuildTiming logs. All four ZIPs were downloaded, checked against artifact sizes/SHA256 and extracted. Both actual/expected 349-file SHA256 manifests are identical, hash diffs empty, exact provenance pins verified, manifest names match the tested Git tree and UWAI.cpp independently hashes to its manifest row.

| Configuration | DLL artifact | Source diagnostics | DLL SHA256 |
|---|---|---|---|
| Release | 13075243536 | 13075637711 | 314148e24f72af987965c471fe5c7ca2bc21910533c50045a6d2651b4c347eb7 |
| Debug | 13075094182 | 13075623011 | 1c465fe5abb912045d626a1062461fc8db9fdf7974b8284c0c539973fc78383a |

Both binaries are PE32 x86 DLLs. Debug's PDB matches the DLL's RSDS GUID 46acb82c-897d-49bb-8452-b4c7febed4b9, age 1. Machine-readable details are in first-impression-weight-storage-2026-11-01.json. This result certifies the exact corrected assistant overlay, not the unchanged user source.

## Boundaries

No explicit C++ exception constructs are introduced. Allocation follows the baseline's ordinary new[] convention; this is not a guarantee against implicit allocation failure. In-game initialization, modified-weight gameplay, cache/save behavior and multiplayer remain untested. Original feature/baseline/workflow branches are read-only. No cross-feature integration or merge is performed.
