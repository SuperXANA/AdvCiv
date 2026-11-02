# Unit-combat upgrade native matrix — 2026-11-01

Original feature: PerUnitCombatUpgradeCostModifers at 3e8418a1b6840192f21af4650dcfce89a8c557d1.
Selected assistant source: cf97766d59822b81772d0ab50a80dba139d8a787.
Read-only baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Current user workflow: a9d225d2e9e5a44a47d5f357bd3f6dbc9017807a.
Previously reviewed workflow correction: 63cfe575f29ba99686d4516e05b5af66b8ea7935.
Exact prepared/tested commit: d0ee554823f99f0d72a2c90a77463235e08c2fa6.

## Scope and justification

The earlier historical run 40456936509 provides Release-only binary evidence, with no archived actual Build.log, source-content hash verification or embedded provenance. Its inspected archive does not establish Debug coverage. This pass closes that specific validation gap; it is not a repeat of an already fully verified matrix and does not introduce another C++ edit.

The complete tree starts from all 872 pinned-baseline blobs, then overlays the selected assistant files while retaining baseline-only paths. All 362 selected DLL blobs are unchanged. There are 349 root source files and exactly six feature DLL files relative to the baseline. Those six local feature files were independently checked against their exact tested Git blob hashes before artifact inspection.

The actual workflow is copied from a9d225d. Its already reviewed two-line source-diagnostics ownership correction is retained: id prepare_sources on preparation and steps.prepare_sources.outputs.source_verification_started in the upload guard. Three provenance pins are populated. No machine-local build configuration, feature logic, XML data, marker or original branch is changed.

This remains an independent unit-combat-upgrade overlay. Prior fixes to destination combat selection, reversible raw totals/effective bounds, signed schema, trait help and player stream are preserved; no other feature's C++ is imported. No unchanged host regression suite is rerun or presented as new verification.

## Results

[Run 41390572710](https://github.com/SuperXANA/AdvCiv/actions/runs/41390572710)

| Configuration | MSVC 7.1 | Actual Build.log | Verified artifact |
|---|---|---|---|
| Release | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL](https://github.com/SuperXANA/AdvCiv/actions/runs/41390572710/artifacts/13116997931) |
| Debug | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/41390572710/artifacts/13117322516) |

Both jobs and the run completed successfully. All four ZIP archives were downloaded, their API byte counts and SHA256 digests verified, and every entry extracted and compared with the ZIP. Both actual Build.log and BuildTiming.log files were inspected. The expected and actual 349-file source-content manifests match, hash diffs are empty, filenames match the tested tree and every provenance pin/configuration matches. All six feature source files independently match both tested Git blobs and native SHA256 entries.

Both DLLs are PE32 x86 DLLs. Debug's RSDS GUID c768a29b-58f3-407d-9d80-19c2e983fd7e, age 1, matches its extracted PDB. Detailed sizes, hashes, artifacts and provenance are in [upgrade-native-2026-11-01.json](upgrade-native-2026-11-01.json).

The new matrix closes this feature's missing Debug validation and unavailable current-log/hash evidence. Its earlier run remains historical Release-only evidence with the limits recorded at the time. No C++ change or new gameplay finding was required.

## Limits

Compilation/linking does not execute Civ4's XML/XDR parser, nonzero trait configurations, actual trait addition/removal, upgrade selection/pricing UI, engine EnumMap/stream operations or gameplay/multiplayer. Extreme accumulation and price arithmetic remain outside this pass; no saturation rule or arbitrary cap is added.

The earlier historical run remains recorded with its original evidence limits. The new tested commit has its own exact provenance and validation status. User-owned source branches and 1.14 remain unchanged.
