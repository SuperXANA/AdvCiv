# Summoned-player catch-up draft — 2026-10-27

## Scope and immutable source

Source branch: [LeaderCivilizationSummoningRandomEvents at d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc](https://github.com/SuperXANA/AdvCiv/tree/d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc), root tree f8577fab184ed11b9e226e85714432a89f1bc85c.
Read-only baseline: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

The source inventory contains 12 blobs. This pass focuses on the XANA-bracketed world technology diffusion and era-median helpers in CvPlayer.cpp and reads their adjacent event call paths. Candidate resolution, new-player creation, city/unit transfers, messages and event metadata remain partial review scope. No original branch head changed since the prior snapshot; the PartnerDiplomacyBuild documentation head is already delivered evidence.

Only the two helpers are changed. The original XANA 08-22-2026 marker boundaries and all unrelated files remain intact. This sparse draft is not a complete 1.14 overlay or a functioning summoning feature.

## SUMMON-20261027-01 — OR prerequisites start satisfied

[doWorldTechDiffusionForSummonedPlayer](https://github.com/SuperXANA/AdvCiv/blob/d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc/CvGameCoreDLL/CvPlayer.cpp#L15819) initializes bOrMet from whether an OR list exists. For a nonempty list, that starts true and never becomes false, so all-unknown OR prerequisites are bypassed once the compile gaps are repaired.

Start the OR condition true only for an empty list, then require at least one known or newly accepted alternative. Require every AND prerequisite. Bounds-check prerequisite IDs before indexing the temporary arrays. Keep newly accepted prerequisite knowledge separate from existing team knowledge.

The helper also refers to nonexistent CvTechInfo count methods, an out-of-scope iAdditionalChance, and undefined eNewPlayer. The rewrite uses pinned [CvInfo_Tech.h](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvInfo_Tech.h) getNumAndTechPrereqs/getNumOrTechPrereqs, keeps the bonus in scope, and passes kNewPlayer.getID to [CvTeam::setHasTech](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvTeam.h). The target team is spelled explicitly as kNewPlayer.getTeam.

## SUMMON-20261027-02 — stated probabilities are multiplied and failed rolls repeat

The source comments specify 5% for one living owner and +8% per additional owner, with a +5% summoner contribution and a 75% cap. The implemented non-summoner expression is (5 + owners - 1) * 8: one owner becomes 40%. The summoner boost is also inside that multiplication. In addition, each successful grant starts another pass that retries earlier failed rolls. This further raises the eventual chance depending on progress elsewhere.

The proposed rule is:

```
chance = min(75, 5 + 8 * (livingOwners - 1) + summonerBonus)
summonerBonus = 5 only when the living summoner knows that technology
```

Give each technology at most one chance attempt per helper invocation, after its prerequisites are eligible. Later passes may unlock previously blocked technologies; an attempted failure is not rerolled. With no living owner there is no random draw. Previously known technologies are untouched.

This one-attempt policy is an explicit mechanics refinement implementing the comments' per-technology chance, not a claim that source balance was tested in-game. Owner counts remain living players, including players sharing a team, as in the source; this draft does not switch to distinct-team prevalence.

Record accepted technologies in order and commit them in that order. The source commits by numeric technology ID, which can put an accepted dependent before its newly accepted prerequisite. Acceptance order preserves the prerequisite closure during the commit sequence. This does not promise atomicity or validate engine callbacks.

## SUMMON-20261027-03 — lower-median era uses the upper index

[calculateMedianEraOfMajorCivs](https://github.com/SuperXANA/AdvCiv/blob/d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc/CvGameCoreDLL/CvPlayer.cpp#L15926) documents a conservative lower median, including index 2 for six civilizations, but uses n / 2, which selects index 3.

After the existing empty-list guard, use (n - 1) / 2. Keep the existing living-major-civilization population, including the newly created player if it qualifies. Remove the invalid trailing const qualifier from this anonymous-namespace free function. Empty population still returns the first era.

## Mechanics boundary

The helper now implements prerequisite-aware, one-opportunity world-tech diffusion and prerequisite-first grant ordering. The later era-floor path can separately add technology, so these probabilities do not describe the overall final research state of a summoned civilization.

Selection must eventually distinguish a pure availability check from random selection, and city/player transfer needs a coherent lifecycle before runtime validation. Those parts are not certified or activated by this draft. No leader/civilization lore preferences, event data, player limit or save format are changed.

## Verification

Run:

```
python3 tests/summon-catchup/check.py
```

The actual revised two helper bodies compile under strict g++ C++03 with -Wall -Wextra -Werror -pedantic, AddressSanitizer and UndefinedBehaviorSanitizer. LeakSanitizer is disabled for host compatibility. Engine, metadata, iteration and RNG dependencies are simulated.

Passed checks cover:

- Empty/blocked OR prerequisites and a satisfied alternative; AND prerequisites requiring every member.
- Probability boundaries at 5%, 10% with the summoner, 13% for two living owners, and the 75% cap.
- No duplicate roll after an independent technology succeeds.
- A reverse-ID dependency chain with prerequisite-first commit order.
- Already-known/no-owner technologies, dead owners, malformed prerequisite IDs and cyclic dependencies without a known entry point.
- Correct grant-player argument with different player/team IDs.
- Empty, one-, two-, three- and six-member era samples, even-count lower median, and dead/nonmajor exclusions.

The stub exposes the pinned prerequisite-count method names and the setHasTech call shape. This is not a compile of the full CvPlayer.cpp, a real engine metadata graph, statistical PRNG test, or MSVC 7.1 DLL validation.

No build workflow is added and no DLL build is triggered. The surrounding summoning branch still contains unfinished integration and compile gaps outside these helpers; for example the adjacent event paths contain buildEligibleSummonCandidates(aeLeadersNotInGame. aeCivsNotInGame). No historical build or unrelated DLL artifact is substituted for full validation. A useful future DLL build must reuse this isolated branch with a complete pinned 1.14 overlay, retained base-only files and the actual named dll-build workflow.

Game startup, actual summoning, engine technology callbacks, event eligibility/UI queries, cache/save loading and multiplayer remain untested. The original branch and 1.14 snapshot remain unchanged.

The companion ledger records a partial scoped review, preserving prior findings and native results. Seven first-pass branches remain pending, so the stopping condition is not met.
