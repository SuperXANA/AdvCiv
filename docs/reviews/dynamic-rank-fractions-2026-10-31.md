# Fractional dynamic-rank attitude terms — 2026-10-31

RANK-20261031-03. Original LeaderSpecificDynamicRankBonusDiplomacy ff5560a1f2af752be1446e8bbd8d37bcdbe64a1e remains read-only. Reused DynamicRankDraft-ChatGPT parent 8f8f6830478d97c0f0fb88856dff5561098e9f4b after reading its naming, return-conversion and native reports. Fresh inventory: 75 branches, no changed original heads against global ledger f843027233b4cacee3709a5de80b16506189a5d0. This is the previously queued arithmetic scope, not a repeat of naming/compiler findings.

## Defect and concrete correction

AI_getShareRelativeProgressAttitude in CvGameCoreDLL/CvPlayerAI.cpp divided integers before constructing scaled:
((ourRank + theirRank) / (totalPlayers - 1)) / 2.
For distinct valid zero-based player ranks, their sum is strictly less than 2*(totalPlayers-1), so those two integer divisions always give zero. Subtracting 0.5 therefore gives a constant negative rank contribution, independent of how poorly the two players rank. The separate counter/divisor integer division also discarded partial counter progress.

[Code and fixture commit 96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4](https://github.com/SuperXANA/AdvCiv/commit/96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4):
- [CvPlayerAI.cpp:8690](https://github.com/SuperXANA/AdvCiv/blob/96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4/CvGameCoreDLL/CvPlayerAI.cpp#L8690): construct the average normalized rank directly as scaled(ourRank + theirRank, 2*(totalPlayers-1)).
- [Line 8691](https://github.com/SuperXANA/AdvCiv/blob/96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4/CvGameCoreDLL/CvPlayerAI.cpp#L8691): construct counter/divisor directly as a rational scaled value.
- [Line 8680](https://github.com/SuperXANA/AdvCiv/blob/96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4/CvGameCoreDLL/CvPlayerAI.cpp#L8680): reject counts <=1 before normalization.

Concrete mechanics proposal implemented for review: evaluate the existing formula base + (averageNormalizedRank - 0.5) * (counter/divisor) with its fractions retained until existing fixed-point rounding, then apply the existing limit. This intentionally changes integer-plateau behavior. With six ever-alive players, ranks 3 and 4, base 0, counter 20, divisor 2, cooperation threshold 2, current attitude 4 and unbounded limit 0, the old formula gives -5 while the corrected formula gives +2. At ranks 4 and 5 with counter 3/divisor 2, preserving fractional counter progress gives +1 after rounding, rather than 0 with counter truncation.

The same attitude metadata still serves both the attitude gate and rank multiplier. That policy is not redesigned here. Existing strict attitude comparison, counter accumulation/decay, half-point center, base value, zero-limit-unbounded convention, signed divisor handling, integer return rounding and absolute bound are retained. No save/cache format change. All 25 XANA marker lines in CvPlayerAI.cpp remain byte-for-byte and in order; prior assistant fixes retained. No other feature branch's DLL code integrated.

## Scoped arithmetic verification

Run python tests/dynamic-rank-fractions/check.py. It extracts the complete actual production method. Game/personality/counter interfaces and fixed-point arithmetic are explicit stand-ins. The arithmetic stand-in uses the actual header's default 2048 scale, rounded signed MulDiv-style operations and integer-return rounding. The reference independently uses long double with quantization at those operation boundaries. The real Windows MulDiv/ScaledNum implementation is not executed by this fixture.

2,313,362 C++03/ASan/UBSan cases passed: distinct rank pairs for player counts 2/3/6/12/18, six thresholds -1 through 4, three current attitudes, five positive/negative/zero divisors, six counter values, three base values, three signed/unbounded limits, and zero/one-player guards. Two focused assertions cover the sign reversal and partial-counter result above. Independent negative controls restore only rank integer division or only counter integer division; each fails its corresponding focused assertion.

Flags: -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak guarantee. Extreme metadata/counter overflow, abs(INT_MIN), invalid engine ranks and actual game execution are outside these bounded fixtures.

Actual ScaledNum.h inspected: signed-int rational constructor calls mulDiv(SCALE,numerator,denominator), the signed-int path uses Windows MulDiv, default scaled uses scale 2048, round() provides the existing nearest-integer conversion. No arithmetic library change.

## Full DLL validation

Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6; selected source 96ed28f2cd67a8f9e96d9409f6f0fc4df11f4aa4; workflow dll-build 1cbd526fddeec564231958870aeab3f2be187a4e. Recursive inventory verifies complete baseline plus selected DLL overlay, all baseline-only files retained, no changed baseline files outside CvGameCoreDLL, 362 DLL-tree blobs. Current workflow copied with previously validated failure-log guards/token, source-hash gate and MSVC7.1 probe retained. No change to protected VM Project files.

Prepared tested commit b273b1505d5ffa46870af947250ea5fc6e5bd3a0. [Run 41211949237](https://github.com/SuperXANA/AdvCiv/actions/runs/41211949237).
First run completed with Release failure and Debug success. All four ZIPs downloaded and extracted. Release actual Build.log shows _precompile.cpp twice (lines 167 and 335), followed by C2220, C4622, fatal C1854 overwriting PCH debug information in temp_files\\Release\\_precompile.obj, then NMAKE U1077 / MSB3073. Summary: 1 warning / 4 errors. Debug actual Build.log: success, 0 warnings / 0 errors. First-run diagnostics 13046129818 (Release), 13046399034 (Debug); failure logs 13046029991; Debug DLL/logs 13047305245. Both source manifests match, 349 entries. This was not a CvPlot size-assertion failure.

### Build-preparation mitigation, WORKFLOW-20261031-07

[Workflow commit 4d4672665066214036fb57678e13a6b8990db2ec](https://github.com/SuperXANA/AdvCiv/commit/4d4672665066214036fb57678e13a6b8990db2ec) changes no game code. After source-hash verification and strict fresh-output deletion, normalize staged root .c/.cpp/.h/.inl LastWriteTimeUtc to the VM's own UtcNow minus two seconds. This prevents preserved runner timestamps from being newer than freshly created VM objects. No machine clock, protected Project configuration, source bytes, hash algorithm or source manifest changes. BuildTiming.log records VM UTC and _precompile.cpp timestamps before/after, is cleared strictly with previous logs, and is copied with the other diagnostics under the current-invocation token.

Evidence and limit: the first Release runner line at 14:50:05.3148037Z contains Windows Build started 10:49:58 AM, suggesting approximately seven seconds of clock lag or output delay. This is not an independent clock-synchronization measurement. Timing artifacts from the corrected run show _precompile.cpp's pre-normalization timestamp was the prior day, not future-dated; included-header timestamps were not recorded. Therefore the exact C1854 root cause remains unconfirmed. Timestamp normalization is a dependency-time mitigation, not proof of a universal C1854 cure. In the corrected Release run, _precompile.cpp appears once and compilation succeeds. Retain both runs' evidence and investigate any recurrence during otherwise warranted future builds, rather than repeatedly rebuilding this unchanged passing snapshot.

Five actual Bash log-copy cases with SSH/SCP stand-ins pass, including optional missing BuildTiming.log; the existing six source-manifest guard cases pass. Local YAML parsed successfully. These checks do not execute PowerShell or Actions expressions; the full native run below executes the actual PS preparation.

### Verified corrected native run

Exact tested commit [4d4672665066214036fb57678e13a6b8990db2ec](https://github.com/SuperXANA/AdvCiv/commit/4d4672665066214036fb57678e13a6b8990db2ec), [run 41212425210](https://github.com/SuperXANA/AdvCiv/actions/runs/41212425210), completed success. Release and Debug each report Rebuild succeeded, 0 warnings / 0 errors in their actual artifact Build.log. Both job logs explicitly report _MSC_VER == 1310. All four ZIPs downloaded/extracted; both BuildTiming.log files inspected.

Verified exact baseline/source/workflow/tested-commit provenance, matching expected/actual source lists, empty diffs, 349 root source files and common manifest SHA-256 1c5ec7ff6242106addeb5d23e88bd3e358fd5075ba5f1d86b34a4c31e8e2d00a, unchanged from the first run. Both binaries have MZ/PE signatures, machine 0x14c, PE32 optional header 0x10b and DLL characteristic.

- Release DLL/log/timing artifact 13047011759; source diagnostics 13047515056. DLL 6,565,888 bytes, SHA-256 3a2a990530883befeda80b4239d0f87c1ef8b7566d47c7096cf19faaf0d729c3.
- Debug DLL/PDB/log/timing artifact 13047012057; source diagnostics 13047480576. DLL 25,186,304 bytes, SHA-256 0c5be49d1c18a502abbd139024163f592697cb531c2da9aa079678d2031e1616. PDB 70,609,920 bytes.

No DLL, PDB or full runner log is committed to the source repository. Native compilation/linking and artifact identity are verified; numerical/gameplay outcomes still rely on the bounded standalone stand-ins, not actual DLL execution in Civilization IV.

## Remaining coverage

The shared cooperation-threshold/rank policy still needs design review. Version-22 player-counter persistence and leader-info cache compatibility remain queued. XML installation/defaults, actual save/load, multiplayer and observed gameplay are not certified. Original source is unchanged; corrected native evidence applies only to its pinned assistant derivative. Code draft used [skip ci]; build-preparation commit intentionally triggered the matrix. Final documentation uses [skip ci]. No PR, merge, force push or original-branch edit.
