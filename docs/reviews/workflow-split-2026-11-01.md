# Split-workflow source diagnostics — 2026-11-01

## WORKFLOW-20261101-10 — output owner left behind after step separation

The changed read-only dll-build head a9d225d2e9e5a44a47d5f357bd3f6dbc9017807a separates source synchronization/hash verification from the MSBuild step. The actual workflow was read and compared with parent f77f8a67cd17fdfa9d1c3f443d49005cee04421e.

Preparation now writes source_verification_started=true to GITHUB_OUTPUT at line 109, but has no step ID. The diagnostics upload at line 280 still tests steps.build.outputs.source_verification_started. The build step no longer writes that output. Consequently the source-verification archive is skipped, both after successful verification and after a verification failure that creates useful diagnostics. Compiler log and DLL upload guards are separate; this finding does not claim that compilation or the DLL upload is disabled.

The scoped correction adds id: prepare_sources to the preparation step and changes the diagnostics condition to steps.prepare_sources.outputs.source_verification_started. It preserves the author's two-step separation, source hash refusal gate, compiler/build guards, current-run log token, failure log collection and output cleanup. No C++ file is changed.

Correction commit: 63cfe575f29ba99686d4516e05b5af66b8ea7935.
Published only on existing LeaderTeamSizeBuild-ChatGPT; dll-build and every other user-owned branch remain read-only.

## Local checks

tests/workflow-split/check.py parses the actual workflow and executes its actual preparation Bash body with local rsync/SSH stand-ins. Release and Debug each exercise success, source-hash mismatch, and sync failure before verification starts: six cases. It checks the actual written output, diagnostic files and upload guard, while preserving the separate build_started output.

Success and hash-mismatch cases produce the flag and permit diagnostics; pre-verification sync failure does not. Restoring the old build-step output reference suppresses all four uploads expected after verification starts. The fixture executes no remote PowerShell, compiler or GitHub artifact upload and does not claim remote fault injection.

## Exact native validation

Original feature: LeaderSpecificTeamSizeAttitude at 9d0004e21a9e9f4df0abc89a4d7fb2e7dad98a58.
Selected assistant source: 74098492ca88543c88e5e30781b84a687cb51e42.
Baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
User workflow source: a9d225d2e9e5a44a47d5f357bd3f6dbc9017807a.
Assistant workflow correction: 63cfe575f29ba99686d4516e05b5af66b8ea7935.
Exact prepared/tested commit: 1e6ae047440c62ec2b1fbff7f2e2b015d7188b36.

The complete tree starts from all 872 baseline blobs, overlays the selected assistant files while retaining baseline-only paths, and copies the new workflow with the two output-owner edits and three provenance pins. All 362 selected DLL blobs are identical in the prepared tree; no gameplay code is rewritten. There are 349 root source files. The selected team's three feature DLL source files were also independently checked against the exact tested Git blob hashes.

This run is justified by a changed workflow defect and the team-size feature's previously unestablished Debug result, rather than another run of unchanged, already complete evidence.

[Run 41384996106](https://github.com/SuperXANA/AdvCiv/actions/runs/41384996106)

| Configuration | MSVC 7.1 | Actual Build.log | Verified artifact |
|---|---|---|---|
| Release | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL](https://github.com/SuperXANA/AdvCiv/actions/runs/41384996106/artifacts/13114288608) |
| Debug | _MSC_VER 1310 probe passed | 0 warnings, 0 errors | [DLL + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/41384996106/artifacts/13114678269) |

Both jobs and the run completed successfully, including both source-diagnostics upload steps. All four archives were downloaded, checked against API ZIP byte counts and SHA256 digests, fully extracted and compared entry-by-entry. Both actual Build.log and BuildTiming.log files were inspected. Both 349-file content manifests match expected/actual values, have empty diffs and exact provenance pins, and their names match the tested tree. The three feature files independently match both tested Git blobs and native SHA256 entries.

Both binaries are PE32 x86 DLLs. Debug's RSDS GUID bac68889-1874-4e0b-939c-2d8911a64ea4, age 1, matches the extracted PDB. Detailed hashes, sizes, artifacts and pins are in [workflow-split-2026-11-01.json](workflow-split-2026-11-01.json).

This supplies a current verified Debug result for the team-size feature and replaces its earlier Release-only status for this unchanged DLL source. The earlier run remains Release-only historical evidence; it was not reclassified.

## Limits

Successful source-diagnostics uploads exercise the corrected owner reference remotely. Hash-mismatch and early-sync failure behavior were exercised locally; no remote failure was deliberately injected. Native compilation does not execute Civ4 XML/default parsing, team membership/personality cache behavior, diplomacy UI, gameplay or multiplayer. Previous historical build limitations remain in their original records.
