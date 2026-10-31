# Collected-log cleanup set — 2026-10-31

WORKFLOW-20261031-09. Read-only dll-build 4dec9b6502486a8b045d1f2a44ec9d4569162613 reviewed against 733140746ebe7a488db066aa85d299897ff6e0e0. Fresh inventory: 75 branches, dll-build is the only changed original head against global ledger 35a2a9e01ebec15ccfbffe47305a0811a65b7edb. Reused HatedDiplomacyDraft-ChatGPT at 35a2a9e01ebec15ccfbffe47305a0811a65b7edb. Existing native/copy-outcome/timing reports consulted.

The source adopts prior staged-source mtime normalization, timing-log transfer, local DLL/PDB cleanup and nonempty Debug PDB checks. Its upload condition now depends only on copy_dll.outcome; this preserves the required build-success implication because the copy step itself runs only when build.outcome is success. No redundant build-success condition is imposed on the user's equivalent upload guard.

## New cleanup omission

BuildTiming.log is now collected with the three MSBuild logs, but the strict pre-invocation deletion list still contains only Build.log, JustErrors.log and JustWarnings.log. After the new invocation token is written, a preparation error before overwriting BuildTiming.log can therefore leave the previous timing file eligible for collection under the new token. Other old logs are correctly cleared first.

[Correction 7a90901362d00fa7ec43ae85bcaeadf1ca274b1f](https://github.com/SuperXANA/AdvCiv/commit/7a90901362d00fa7ec43ae85bcaeadf1ca274b1f) adds BuildTiming.log to that existing deletion list. Deletion remains strict and precedes token publication. On deletion failure, the fresh token is not written. This is a diagnostic-freshness correction; no compiler, C++ code, hash algorithm, clock settings or protected Project configuration changed. All newer source comments, sourceRoot/projectDir refactoring, copy-only upload condition and cleanup edits retained.

## Checks and limits

Updated tests/build-workflow/copy-check.py accepts the equivalent copy-only upload predicate when the copy step is gated on build success. It statically checks the collected log set is a subset of the pre-token cleared set and verifies ordering. Restoring the source omission fails with AssertionError: {'BuildTiming.log'}.

All six actual-copy Bash cases, five log-collection Bash cases and six source-manifest guard cases pass with local stand-ins. They validate local command behavior and structural invariants, not PowerShell or the Actions expression engine. YAML parsed. No new standalone C++ claim.

This diagnostic-only refinement and test use [skip ci]; no DLL build was triggered on this assistant workflow head. Prior exact native passes remain historical evidence for their recorded commits, not native validation of 4dec9b6 or 7a90901. The corrected cleanup block was also copied into the separately pinned CivicScrollDraft native preparation; that run's exact compiler/log results are recorded in the companion metadata report. No remote error was injected between token publication and timing-log writing.

User-owned dll-build and baseline 1.14 remain read-only. The PCH root cause remains unconfirmed; this cleanup-set fix makes no new claim about C1854.

## Source adoption during this pass

A final source-head check found dll-build f77f8a67cd17fdfa9d1c3f443d49005cee04421e. Its only change from 4dec9b6 is the same BuildTiming.log deletion-list correction. That latest source was read and rechecked: six copy cases, five log cases and six hash-guard cases pass locally. After removing the three filled provenance pins, the prepared workflow is byte-identical to this latest source. The original branch was never edited by the assistant. No additional DLL run was triggered merely for this adoption.

The independently pinned Civic run 41224201639 failed on two enum-return compiler errors; after scoped casts, run 41224382638 failed on the original feature's explicitly unfinished changeUnhappinessTimer API. Both complete matrices were followed; all eight ZIPs extracted and actual Build.log/BuildTiming.log plus exact source manifests inspected. The workflow preparation/log collection executed, but neither run produced a DLL. Companion report: docs/reviews/religion-weight-mutation-2026-10-31.md.
