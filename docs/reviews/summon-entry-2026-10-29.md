# Summon event candidate entry points — 2026-10-29

Original source LeaderCivilizationSummoningRandomEvents d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc. Reused SummonCatchupDraft-ChatGPT a2a1e4df6084fed111755db80148f9aff37701f0, retaining prior catch-up/compatibility corrections. Current original source head unchanged.

SUMMON-20261029-06:
- CvPlayer::canDoEvent, CvPlayer.cpp:16866.
- CvPlayer::applyEvent, CvPlayer.cpp:17374.
Both called buildEligibleSummonCandidates(aeLeadersNotInGame. aeCivsNotInGame). Replace the period with a comma to pass the two vectors declared directly above each call.

Actual helper definition at15332 accepts std::vector<LeaderHeadTypes>& and std::vector<CivilizationTypes>&. Entire helper and surrounding call paths were read; both calls now match that signature. Existing candidate pool construction, resolver, gating and event effects unchanged. Two exact source occurrences confirmed, XANA markers preserved.

Verification limited to source-level signature/call inspection; no new fixture needed for this punctuation-only edit. No full method/engine/MSVC7.1/DLL build claimed. This remains an incomplete-feature draft; [skip ci]. Prior evidence and findings retained. Existing unresolved eligibility RNG, large-weight arithmetic, player-slot/city-transfer integration and real metadata remain queued. Do not infer a working summoned civilization from this syntax repair.
