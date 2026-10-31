# Failure-log workflow validation — 2026-10-31

## Scope and pins

Reviewed dll-build 1cbd526fddeec564231958870aeab3f2be187a4e against 07133f27906c364b266043a1788ec0eacd2e8b3b, after inventorying 75 branches and reading the global coverage ledger at fdc705108af59618e0cf474c19222c0038574b9d. Original branches remain unchanged.

Read-only 1.14 baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6. Selected assistant source: 484ab0fca026c3b11e8975cb6c71499a2a8b685d on HatedDiplomacyDraft-ChatGPT. All 362 CvGameCoreDLL tree blobs match the complete pinned baseline plus corrected feature snapshot e3887b18825dc14d026a0d8fb5f7a6b58a5c7484 overlay, retaining baseline-only files. This DLL code previously passed at 2f37cbcc50427fbf0b81a4c8e6a30270f5af35cd. That historical build is only the control, not validation of the updated workflow.

## Completed workflow corrections

WORKFLOW-20261031-05: The log-copy step had no condition, and the failure-upload condition used only steps.build.outcome == 'failure'. Both retained GitHub Actions' implicit success() gating. Consequently, neither could run following a failed build. Add explicit always() conditions and the build_started output guard. Source: .github/workflows/auto-dll-build.yml, Copy Build Log files Over To Linux / Upload Build Artifacts Always on Failure; corrected normal-workflow lines 230–258.

WORKFLOW-20261031-06: A build invocation that fails before MSBuild opens its log can otherwise leave stale remote logs available for collection. Strictly delete previous logs, then write a run/attempt/configuration/commit token. Clear runner-side log files and require the current remote token before copying. Attempt all three log transfers independently; require a nonempty Build.log while tolerating missing optional logs. Remove the token during cleanup. This changes only build diagnostics, not protected machine-local Project settings or DLL sources.

Implementation commits: 361629eee61adf4d9cc5c354e414e5845d7d4ce3 (with temporary deliberate post-build failure) and ea9ef9f83f735bcb0660e33908449a316ffa7621 (probe removed). All changes are isolated on HatedDiplomacyDraft-ChatGPT. No PR, merge, deletion, force push, or original-branch modification.

## Verification and limits

Four local tests execute the actual Bash collection block with fake SSH/SCP: matching token, stale token rejection, missing required Build.log with independent remaining transfers, and missing optional log. Six existing source-manifest guard cases also pass. These local checks do not execute GitHub's expression engine, SSH, MSBuild or the DLL.

Probe run: https://github.com/SuperXANA/AdvCiv/actions/runs/41202703341 at 361629eee61adf4d9cc5c354e414e5845d7d4ce3. Both matrix jobs concluded failure, with successful current-log collection and failure-artifact upload. Downloaded and extracted all four ZIPs; inspected the actual MSBuild Build.log files and both source diagnostics.

- Debug: actual MSBuild succeeded with 0 warnings / 0 errors; the _MSC_VER 1310 compiler check passed. The deliberate notice CHATGPT_CONTROLLED_BUILD_STEP_FAILURE_AFTER_MSBUILD_SUCCESS actually executed, then Bash exited 1. The workflow was intentionally failed after compilation; no DLL artifact was uploaded by design. Do not call this a successful workflow or verified packaged DLL.
- Release: genuine compiler failure occurred before the deliberate probe. Build.log lines 335–338 show _precompile.cpp compiled again after the other sources, C2220, warning C4622 and fatal C1854 overwriting PCH debug information in temp_files\\Release\\_precompile.obj. Wrapper errors U1077/MSB3073 follow; summary is 1 warning / 4 errors. This is not the CvPlot size-assertion stop condition. No DLL artifact was produced. A second normal matrix is necessary to validate the normal upload path and check recurrence; no compiler-warning suppression or speculative source edit was applied.
- Probe diagnostic artifact IDs: Release 13043342290; Debug 13043780042. Failure-log artifact IDs: Release 13043153460; Debug 13042894608.
- Both manifests have 349 root .c/.cpp/.h/.inl entries, byte-identical expected/actual lists, empty diff, and SHA-256 b1ea9061f07bf130e6965cda3e0df31f2c48ad559bf5e8fd8ce5b73317edf995. Provenance pins match the tested commit, baseline, source and workflow.

Normal run: https://github.com/SuperXANA/AdvCiv/actions/runs/41203236797 at ea9ef9f83f735bcb0660e33908449a316ffa7621. Completed success. Release and Debug each passed Rebuild with 0 warnings / 0 errors. The compiler check is required in the successful command chain before MSBuild. All four artifact ZIPs downloaded and extracted; actual Build.log files, PE32 x86 DLL headers, nonempty Debug PDB, exact source lists and provenance verified. Both source manifests again match the same 349-entry digest.

Normal artifact IDs: Release DLL/logs 13043840662, diagnostics 13043915430; Debug DLL/PDB/logs 13043925823, diagnostics 13043925801. Release DLL: 6,565,888 bytes, SHA-256 bcbb6dc2baa82b7e8a9aee847d37e05e9d9f0bf1636999ea3f7506cce87041d7. Debug DLL: 25,186,304 bytes, SHA-256 f4e0d393fcc16fb2eb6d61891b8d74b03fe2e3fe76c01eca728e442883add7e6. Debug PDB: 70,585,344 bytes.

The first Release PCH failure did not recur in the normal run. Its root cause remains unconfirmed; the repository Makefile source-list/PCH rules were inspected, but protected VM configuration was not modified. No claim that this workflow change fixes C1854. Retain the original failure evidence; investigate if it recurs with otherwise warranted future builds rather than repeatedly rebuilding this unchanged successful snapshot.

## Published source links

- [Corrected workflow, normal tested commit](https://github.com/SuperXANA/AdvCiv/blob/ea9ef9f83f735bcb0660e33908449a316ffa7621/.github/workflows/auto-dll-build.yml#L230)
- [Strict old-log removal and invocation token](https://github.com/SuperXANA/AdvCiv/blob/ea9ef9f83f735bcb0660e33908449a316ffa7621/.github/workflows/auto-dll-build.yml#L61)
- [Failure upload guard](https://github.com/SuperXANA/AdvCiv/blob/ea9ef9f83f735bcb0660e33908449a316ffa7621/.github/workflows/auto-dll-build.yml#L257)
- [Executable local collection checks](https://github.com/SuperXANA/AdvCiv/blob/ea9ef9f83f735bcb0660e33908449a316ffa7621/tests/build-workflow/failure-log-check.py)


Hash implementation and game code are unchanged. The original dll-build source still needs the isolated workflow corrections applied by the user. Runtime gameplay/save compatibility is outside this workflow validation.
