# Explicit summon resolver paths — 2026-10-30

SUMMON-20261030-08/09. Read-only source LeaderCivilizationSummoningRandomEvents d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc; reused SummonCatchupDraft-ChatGPT parent d0a02a7eec47c41830647ab218595a68518f8894. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against global ledger dafd2bb0294d822a51e3d3dd13c81e9946fae67f.

## Committed changes

CvPlayer.cpp, resolveSummonLeaderAndCiv:
- SUMMON-08: lines 15617–15624 validate explicitly supplied IDs against the eligible unused leader/civilization pools before assignment or selection. buildEligibleSummonCandidates:15332–15386 supplies those pools by excluding currently alive/in-use entries. This implements the resolver's existing comment that specific IDs still check in-game status; no new exclusion rules introduced. Out-of-pool IDs cannot reach selector fallback.
- SUMMON-08: lines 15634–15636 return the explicitly supplied pair immediately when both IDs exist and pass those checks. Previously this configuration skipped one-sided resolution, then either fell through false or let weighted-array paths overwrite explicitly supplied values. The source documents specific pairs as deterministic. They now take precedence over arrays and perform no selector callback.
- SUMMON-09: final failure at 15759–15760 writes NO_LEADER/NO_CIVILIZATION to the actual output references. Previous code declared unused eSummonLeader/eSummonCiv locals, leaving partial output values untouched.

All existing weighted-selection, compatibility-selection and fallback algorithms are otherwise unchanged. Explicit pairs remain author-specified pairs; no new isLeaders compatibility restriction was added to this deterministic path. Existing single-sided/weighted paths retain their compatibility helpers. XANA markers and earlier weight/eligibility/call-site corrections are preserved.

Actual callers in canDoEvent (16886 before this insertion) and applyEvent (17394 before insertion) initialize outputs to NO_* and rebuild candidate pools before resolving. The correction makes valid explicit-pair events eligible without allowing already-used explicit IDs. Full engine timing/state changes are not tested. Early failures and one-sided failures are not claimed to clear every output reference; only the previously incorrect terminal cleanup is repaired.

## Verification

tests/summon-resolver/check.cpp embeds the complete actual revised resolver. Event metadata and all four selector functions are stubs; selector callbacks return the first supplied candidate or NO_* and count invocations. Compatibility metadata and real weighted RNG are not executed.

6,400 strict C++03 -Wall -Wextra -Werror -pedantic ASan/UBSan configurations passed: every subset of three candidate leaders/civilizations, five explicit ID values including NO_* and out-of-range 99, and all four array-presence combinations. Includes 576 valid explicit-pair configurations with exact outputs and zero selector calls, and 4,800 unavailable-ID rejections before selector callbacks. Three focused regression cases also pass, including a terminal-failure call seeded with stale output references.

Restoring the original resolver in focused controls:
- Eligible explicit pair: false before, true after, zero callbacks both.
- Explicit leader absent from pool: accepted with one callback before, rejected with zero callbacks after.
- Terminal failure: outputs (-1,88) before versus (-1,-1) after.
Original-only negative control used -Wno-unused-variable to reach behavior despite the two unused locals. Corrected fixture needed no warning suppression. Leak detection disabled as unsupported; no leak claim.

No complete CvPlayer/engine, actual eligibility snapshot construction, real selectors/RNG, event execution, transfer/slot handling, metadata loading, MSVC7.1 or DLL/game verification is claimed. This remains a partial resolver draft using [skip ci]; no native build triggered. Full canDoEvent RNG consumption, selected-pair persistence between checks/application, slots/transfers and metadata integration remain review scopes. Existing prior fixtures retained as distinct evidence.
