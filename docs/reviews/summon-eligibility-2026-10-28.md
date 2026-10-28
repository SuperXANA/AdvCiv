# Summon leader eligibility follow-up — 2026-10-28

Source LeaderCivilizationSummoningRandomEvents: d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc.
Previous draft 59393f566d83bb2004dec0a061b420bc95584fa7; code https://github.com/SuperXANA/AdvCiv/commit/c04de7e1dcaf8509fa0f0c844189c17afbf98345.
Read-only 1.14 pin remains 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## SUMMON-20261028-04 — civilization-first leader selector ignores availability

[selectCompatibleLeaderForSummonCiv, line 15528](https://github.com/SuperXANA/AdvCiv/blob/c04de7e1dcaf8509fa0f0c844189c17afbf98345/CvGameCoreDLL/CvPlayer.cpp#L15528).

The source comment promises leaders compatible with a civilization AND not already in the game. The original loops the civilization leader entries but receives no availability pool and performs no in-game test. This permits an already-present leader to be selected even though buildEligibleSummonCandidates has built an available-leader pool elsewhere in the same resolver.

The implementation also calls kCiv.getLeader(i), absent from the pinned [CvCivilizationInfo interface](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvInfo_Civilization.h). That interface provides isLeaders(int), a compatibility mask rather than an indexed list accessor.

The proposal adds a const available-leader-vector parameter, iterates that supplied pool, rejects out-of-metadata-range IDs before lookup, and tests kCiv.isLeaders(eLeader) unless GAMEOPTION_LEAD_ANY_CIV is enabled. The opposite-direction selector already consults that option; civilization-first selection now also respects it. Event positive-weight filtering and selection are otherwise retained.

The four resolver call sites at new lines 15652, 15659, 15721 and 15728 pass aeEligibleLeaders. Pool order is retained; duplicate pool entries are not normalized. This helper trusts the supplied snapshot's availability and does not independently scan current players. The source pool-building policy is unchanged.

Only this helper and its four call sites change; existing XANA 08-22-2026 boundaries and earlier SUMMON-20261027-01..03 refinements remain. No other feature branch is imported.

## Verification

python tests/summon-eligibility/check.py passed using the actual helper body with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. LeakSanitizer disabled; UBSan halt_on_error enabled.

The fixture models a compatible leader omitted from the pool because already in use, an eligible compatible leader, and an eligible incompatible leader. It checks exclusion of the omitted leader, positive/zero event filters, LEAD_ANY_CIV, all five integer roll positions in a 2:3 weighted fixture, uniform unfiltered selection, absent weight arrays, empty pools, and metadata-range guards without consuming RNG on empty/invalid input. Synthetic enum sentinels permit testing metadata-out-of-range IDs without constructing enum-representation-invalid values.

The fake civilization class exposes isLeaders and intentionally does not expose getLeader/getNumLeaders. Engine, metadata and RNG are stubs; caller updates are checked structurally, not by executing the full resolver. Fixture weights are small and totals fit the 16-bit RNG interface. Large weight totals, overflow, opposite-direction selection, full event eligibility/execution queries, slot creation, transfers, persistence and game/multiplayer behavior remain unvalidated.

No workflow or DLL build was triggered. This remains a sparse feature draft; it is not a complete pinned-base DLL result or a functioning summoning feature certification. Subsequent integration should reuse this assistant branch before the authorized complete-base native validation.

## Coverage

Fresh inventory showed no changed source heads. PlotTimerDraft's head difference was its already-delivered lifecycle documentation. UnitStatusEffects remains deferred and the ceiling alert closed. Initial scoped rotation has no pending branch rows; partial scopes and failed/unverified builds remain, so the stop gate is false.
