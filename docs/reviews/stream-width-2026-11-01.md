# Serialization wrapper character widths — 2026-11-01

## STREAM-20261101-01

Original SerializationHelpers source remains read-only at `2be6010dc6787a717c851cd125e005010cf71450`. Reused assistant parent: SerializationHelpersBuild-ChatGPT `6b74935fd718db11c108ae2feeb4c6c961a22bd4`. The prior [string-codec repair](serialization-helpers-2026-10-27.md) is preserved.

The previous assistant Write(const TCHAR*) fix covers only the build's selected character width. In a narrow-TCHAR configuration, Write(L"wide") has no matching wide-string overload; the pointer instead converts to bool and selects Write(bool). In a wide-TCHAR configuration the same problem affects Write("narrow"). The wrapper therefore still writes a boolean rather than the text for the other supported string width. Reading that record with a string codec cannot restore the original content and can disrupt subsequent record interpretation.

An overload-sensitive reproduction against the actual previous wrapper failed its expected string-dispatch check: one raw string used the boolean path. This is a helper-level defect; no existing gameplay/save consumer or observed corrupt save is asserted.

[Committed correction e2436464da6e4bde74a90166c0347d016257c191](https://github.com/SuperXANA/AdvCiv/commit/e2436464da6e4bde74a90166c0347d016257c191) adds explicit [char and wchar Write overloads at FDataStreamExtended.h:43](https://github.com/SuperXANA/AdvCiv/blob/e2436464da6e4bde74a90166c0347d016257c191/CvGameCoreDLL/FDataStreamExtended.h#L43), and [matching raw Read overloads at line 50](https://github.com/SuperXANA/AdvCiv/blob/e2436464da6e4bde74a90166c0347d016257c191/CvGameCoreDLL/FDataStreamExtended.h#L50). Each delegates to the matching base string codec. The base API already supplies both widths in [FDataStreamBase.h:45–57](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/FDataStreamBase.h#L45).

TCHAR remains an alias of a supported character width, so existing matching-width calls still resolve to their prior string codec. Owning std::string/std::wstring methods, primitive int/bool methods, enum-as-int forwarding/static checks, constructor assertion and null-stream no-op behavior remain unchanged. No executable-facing base virtual interface, class field, save version or explicit exception syntax is added. All pre-existing XANA comments are retained with new dated refinement markers.

## Focused checks

```sh
python tests/stream-width/check.py
ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 STREAM_WIDTH_SANITIZE=1 python tests/stream-width/check.py
```

Each narrow/wide TCHAR configuration passes 133 cases normally and under ASan/UBSan, using strict C++03, -fno-exceptions and warnings-as-errors. Coverage includes both raw pointer widths, mutable buffers, lengths 0–64, owning strings, a trailing integer/bool, enum sentinels/positive values and unchanged outputs when the stream is absent.

The actual production wrapper is compiled. FDataStreamBase is an overload-sensitive tagged-record stand-in, wchar/TCHAR and enum traits/assertions are small stand-ins, and string reads use deliberately sufficient fixture buffers. These checks verify wrapper dispatch/order/value preservation, not the EXE's binary string format or byte counts. Host wchar size is not presented as a Windows ABI test. The trait fixture explicitly declares its negative/positive enum test values so its sanitizer run does not rely on invalid dummy-enum values. LeakSanitizer remains disabled; no leak-detector result is claimed.

Raw reads still require a sufficiently large destination; owning ReadString overloads remain available when capacity is unknown. No existing stream is migrated. A consumer that previously persisted the wrong boolean codec must version its own record before adopting a different encoding; the wrapper cannot reconstruct lost text. No such consumer integration is invented here.

## Full native DLL verification

Exact tested commit: [ca30529184c37257ef49172c6d0be7af0729c5ff](https://github.com/SuperXANA/AdvCiv/commit/ca30529184c37257ef49172c6d0be7af0729c5ff), selecting corrected assistant source `e2436464da6e4bde74a90166c0347d016257c191`. [Run 41278422639](https://github.com/SuperXANA/AdvCiv/actions/runs/41278422639) and both jobs completed successfully, with _MSC_VER == 1310 (MSVC 7.1) probes verified in both jobs.

| Configuration | Actual MSBuild Build.log | Verified DLL artifact | Source diagnostics |
| --- | --- | --- | --- |
| Release | 0 warnings, 0 errors | [13072421048](https://github.com/SuperXANA/AdvCiv/actions/runs/41278422639/artifacts/13072421048) | 13072660818 |
| Debug | 0 warnings, 0 errors | [13071824108](https://github.com/SuperXANA/AdvCiv/actions/runs/41278422639/artifacts/13071824108), including matching PDB | 13072292698 |

All four ZIPs were downloaded, byte sizes/SHA-256 digests checked against GitHub metadata, and contents extracted. Actual Build.log and BuildTiming.log files were read. Both 350-file actual-source manifests match their expected manifests exactly, with empty hash diffs, passed status and exact commit/configuration/baseline/selected-source/workflow provenance. FDataStreamExtended.h and the preserved CvGameCoreDLL.h were independently hashed against those manifests. Both binaries are PE32 x86 DLLs. The Debug DLL CodeView RSDS identity matches its PDB GUID `c3d0ef0e-0abe-4ca5-a412-9721206da2c0`, age 1. [Machine-readable evidence](stream-width-2026-11-01.json) records all hashes, sizes, timing and scope.

The complete pinned 1.14 baseline `5970334b64a875b5cdb370c94fc9a98db4eacda6` remains present: 872 baseline blobs, including 362 DLL blobs. The selected serialization overlay adds FDataStreamExtended.h, giving 363 DLL blobs and 350 root source files. The existing CvGameCoreDLL.h inclusion is unchanged. The current actual dll-build workflow `f77f8a67cd17fdfa9d1c3f443d49005cee04421e` is copied with only the three pins set.

Native compilation checks the ordinary raw-string member bodies against the real base overloads and engine headers. It does not execute a save/load round trip or test native Unicode project settings separately. No independent feature code is merged. Original branches and baseline remain unchanged; the final documentation publication uses [skip ci].
