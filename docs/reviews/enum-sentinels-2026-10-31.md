# Optional enum lookup sentinels — 2026-10-31

## ENUMLOOKUP-20261031-01

Original source: CodeMacroHelpers `d9908667cdc5fddef11a49e3864dfad1ecc47e92`. Reused assistant parent: CodeMacroHelpersBuild-ChatGPT `7880264054c6066e60bf862df848102e3105a680`. Baseline: 1.14 `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Actual current workflow: dll-build `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`. Original branches remain read-only.

The [baseline lookup failure handler](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvGlobals.cpp#L1062) deliberately accepts empty strings and NONE without an unknown-type assertion. When these names are absent from the map, getInfoTypeForString returns -1. The [original proxy](https://github.com/SuperXANA/AdvCiv/blob/d9908667cdc5fddef11a49e3864dfad1ecc47e92/CvGameCoreDLL/CvGlobals.h#L979) and prior assistant proxy validate the requested enum prefix before the lookup. Neither accepted sentinel has a UNIT_, CIVIC_, etc. prefix. Consequently a normal empty optional name generates a false type-mismatch assertion in an assertions-enabled DLL, even through GET_ENUM_HIDE_ASSERT("NONE"). Release returns the underlying lookup result without this assertion.

The extended actual-proxy regression reproduced the false assertion in its Debug-mode configuration before correction; the no-assertions configuration passed. This is a helper API compatibility defect, not evidence of an observed gameplay crash or an already-integrated consumer.

[Code correction 9187b83372c4086d4f3f1d34e10abd4f3097b0ac](https://github.com/SuperXANA/AdvCiv/commit/9187b83372c4086d4f3f1d34e10abd4f3097b0ac) exempts only empty and exact uppercase NONE names from prefix validation at [CvGlobals.h:990](https://github.com/SuperXANA/AdvCiv/blob/9187b83372c4086d4f3f1d34e10abd4f3097b0ac/CvGameCoreDLL/CvGlobals.h#L990). The actual lookup still runs with the original hide-assert flag and result conversion. No -1 result is fabricated, valid-name lookup semantics remain unchanged, and ordinary mismatched prefixes still assert. Existing XANA markers and the caller-string ownership correction are preserved. No class field, executable interface, save format or explicit exception syntax is added.

## Focused verification

Run from the branch root:

```sh
python tests/enum-lookup/check.py
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 ENUM_LOOKUP_SANITIZE=1 python tests/enum-lookup/check.py
```

Both assertion configurations passed in normal and ASan/UBSan builds under strict C++03, -fno-exceptions and warnings-as-errors. Each configuration checks 240 typed sentinel conversions across the actual 80 dynamic/static enum macro entries: normal NONE, empty and hidden-assert NONE. The retained tests also cover valid copy/direct initialization, delayed conversion from a temporary, independence from caller string mutation, unknown lookup flag forwarding and a nonempty wrong-prefix assertion. The old proxy fails the new no-false-assertion regression.

The fixture extracts the actual production proxy, declaration and macro lists. CvString, lookup results and concrete enum declarations are stand-ins; it does not execute Civ4's global map or load XML. Actual baseline handler code was separately read to establish the accepted-name contract. No live game or save result is claimed.

## Full native DLL verification

Exact tested commit: [04ef4c9a5bc91308c1dbef5af3a9004f117fb535](https://github.com/SuperXANA/AdvCiv/commit/04ef4c9a5bc91308c1dbef5af3a9004f117fb535), selecting corrected assistant source `9187b83372c4086d4f3f1d34e10abd4f3097b0ac`. [Run 41270728749](https://github.com/SuperXANA/AdvCiv/actions/runs/41270728749) completed successfully in both configurations; both job probes confirmed _MSC_VER == 1310 (MSVC 7.1).

| Configuration | Actual MSBuild Build.log | Verified DLL artifact | Source-hash diagnostics |
| --- | --- | --- | --- |
| Release | 0 warnings, 0 errors | [13068978301](https://github.com/SuperXANA/AdvCiv/actions/runs/41270728749/artifacts/13068978301) | 13068774388 |
| Debug | 0 warnings, 0 errors | [13069211745](https://github.com/SuperXANA/AdvCiv/actions/runs/41270728749/artifacts/13069211745), with matching PDB | 13069281476 |

All four ZIPs were downloaded, their byte sizes and SHA-256 digests checked against GitHub metadata, and their contents extracted. Actual Build.log and BuildTiming.log files were read. Both 349-file source manifests match their expected manifests exactly, with empty hash diffs, passed status and exact commit/configuration/baseline/selected-source/workflow provenance. CvGlobals.h and the preserved CvMemoryManager.h were independently hashed against the manifests. Both output binaries are PE32 x86 DLLs; the Debug DLL's CodeView RSDS record matches its PDB GUID `ece69d07-5aac-4c13-b977-314a3afc94e1`, age 1. [Machine-readable evidence](enum-sentinels-2026-10-31.json) records all hashes, sizes and timing fields.

This establishes full DLL compilation/linking and artifact provenance for the exact prepared commit. It does not execute the DLL's enum proxy, real XML/global map or game; the sentinel behavioral regression is exercised by the focused fixture above.

The complete 872-blob baseline remains present, including all 362 DLL blobs and 349 root C/C++/header/inl source files. The selected assistant snapshot overlays that complete baseline. The only new DLL delta against its assistant parent is the small CvGlobals.h guard. The existing CvMemoryManager.h 2D-deletion helper from this feature is preserved unchanged; it is not a new correction or independently certified by these enum tests. No other feature was merged.

The actual current build workflow is copied with only its three pins set. A documentation-only publication follows native validation using [skip ci].
