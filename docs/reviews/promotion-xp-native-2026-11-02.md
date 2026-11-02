# Promotion XP native matrix — 2026-11-02

Original source: PromotionAltersUnitXPValues at 09741c7206588a8fc42b1e62b90c76ecaea13a55.
Selected assistant source: 9230eeb926de40e4d2ebd79f59b867b27f30e492.
Read-only baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Actual current workflow: 1cc8c3d24e9fe15126485de0b9e6604167caac36.
Exact prepared/tested commit: 007f5d98a97d949d69a212f525e612e9bfb1238f.

## Scope

Close the missing Debug result and actual-log/source-content evidence for the existing promotion-XP refinement. The historical run 40518367294 provides a Release-only DLL archive without embedded provenance or source manifests. That historical record is retained with its limits; it is not promoted into Debug evidence.

All C++ blobs remain unchanged from the selected assistant source. Starting with the complete pinned baseline, overlay its selected files while retaining baseline-only files. All 872 baseline paths remain, all 362 selected DLL blobs are identical, and there are 349 root source files. The five feature DLL paths are CvGameTextMgr.cpp, CvInfo_Unit.cpp/.h and CvUnit.cpp/.h. Each local feature source was independently verified against the exact tested Git blob hash.

Existing accessors/mutators, post-read promotion-derived XP reconstruction, optional zero XML defaults, signed/additive XP semantics, schema and help corrections are retained. The branch's baseline promotion roster and scoped Combat I example remain as previously published. No additional MLP content, feature code, new wire format or balancing rule is introduced. Unchanged host C++ regression suites are not rerun or presented as new evidence.

## Changed workflow review

The user-owned dll-build head 1cc8c3d adopts WORKFLOW-20261101-10's prepare_sources ID and corrected diagnostics guard. It additionally renames the preparation HASH_SCRIPT/ENCODED_SCRIPT_FOR_HASH_CALCULATION variables to step-local PS_CODE/ENCODED_SCRIPT consistently. Preparation, build and cleanup have distinct step environments; the preparation variable does not replace the build step's own script.

The actual new YAML was read. The published tests/workflow-split/check.py fixture from correction 63cfe575f29ba99686d4516e05b5af66b8ea7935 executes the actual new preparation Bash with local rsync/SSH stand-ins. All six success/hash-mismatch/early-sync-failure cases across Release/Debug pass. The old diagnostics-owner condition still fails four expected-upload cases. These local checks do not execute Windows PowerShell, the compiler or GitHub artifact uploads.

The new workflow is copied unchanged except for its three exact provenance pins. No assistant workflow patch is necessary on this source head. The user workflow branch and all other original branches remain read-only.

## Native results

[Run 41395843089](https://github.com/SuperXANA/AdvCiv/actions/runs/41395843089)

| Configuration | MSVC 7.1 | Actual Build.log | Verified artifact |
|---|---|---|---|
| Release | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL](https://github.com/SuperXANA/AdvCiv/actions/runs/41395843089/artifacts/13119054247) |
| Debug | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/41395843089/artifacts/13119830930) |

Both jobs and the run completed successfully; both source-diagnostics upload steps succeeded. All four archives were downloaded and verified against their API byte counts and ZIP SHA256 digests. Every entry was extracted and compared with its ZIP bytes. Actual Build.log and BuildTiming.log files were inspected for both configurations.

The expected/actual 349-file source-content manifests match, hash diffs are empty, filenames match the tested tree and every provenance/configuration pin matches. The five feature files independently match exact tested Git blobs and native SHA256 manifest entries. Both DLLs are PE32 x86 DLLs. Debug RSDS GUID ce974231-c9ed-4a9a-8f93-3954c7a25956, age 1, matches its extracted PDB. [Detailed hashes and evidence](promotion-xp-native-2026-11-02.json).

This closes promotion XP's missing Debug and current-procedure evidence. It also validates the adopted current workflow with only provenance pins changed; no additional workflow patch or C++ edit was required.

## Limits

Compilation/linking and artifact checks do not execute Civ4 XML/XDR validation, localized text rendering, real combat XP awards, unit load/reconstruction or gameplay/multiplayer. Prior gameplay and content-installation limits remain. No C++ change or new source defect is claimed by this validation pass.
