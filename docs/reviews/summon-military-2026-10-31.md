# Summon military helper and unit API boundary — 2026-10-31

SUMMON-20261031-10/11. Read-only LeaderCivilizationSummoningRandomEvents `d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc`; reused SummonCatchupDraft-ChatGPT parent `493cb38589f903411956d6117681f4b7c3a22b88`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no original-head changes against global ledger db3c3e16dfcc892222559ff2b7c28e9d39a5ed40. Prior catch-up, compatibility, eligibility, entry, weights and resolver reports checked before this new military scope.

[Scoped correction and fixture ca04e9c2a6477de23ab9e6b3e15f843f4bd4d858](https://github.com/SuperXANA/AdvCiv/commit/ca04e9c2a6477de23ab9e6b3e15f843f4bd4d858).

## SUMMON-20261031-10 — completed helper corrections

Anonymous-namespace doWorldMilitaryUnitBreachforSummonedPlayer, CvGameCoreDLL/CvPlayer.cpp:
- line 15795: make iCreateNum mutable. The existing minimum-one branch assigns 1 after population/2; declaring the variable const makes that assignment ill-formed. Existing count calculation, minimum and comment remain.
- line 15811: remove the semicolon after if(eSummoner!=NO_PLAYER). The empty statement made the following defection block unconditional, bypassing the explicit source guard.
- line 15816: declare std::vector<CvUnit*> apDefectors locally before collecting candidates. No declaration exists in the supplied function/scope. Retain the existing collect-first, transfer-after-iteration structure.

No creation probabilities, first-unit guarantee, owner comparisons, great-person/settler filters, transfer implementation or promotion-copy policy is changed. Existing XANA boundaries and previous corrections remain; changed lines have dated ChatGPT annotations.

## Verification

Run `python tests/summon-military/check.py`. It extracts the complete actual corrected helper. Event/city/player/unit interfaces, plot iteration, RNG and defectUnitToPlayer are stand-ins.

1,344 strict C++03/ASan/UBSan configurations passed: populations 0,1,2,3,4,7,10; four creation and defection chances (0,1,50,100); NO_PLAYER/three summoner IDs; and three deterministic roll values (0,49,99). Sixteen synthetic units exercise visual owner and great-person/settler combinations. Checks cover minimum/default creation, creation RNG draw counts, no defection metadata access/iteration/RNG for NO_PLAYER, owner exclusion, eligible candidate roll counts and ordered calls to the transfer stand-in.

The mocked initUnit records creation but does not insert created units into the plot; the mocked transfer records calls but does not kill/convert units. These are explicit limits, not actual transfer/game behavior certification.

Three independent negative controls restore const on the count, remove the local vector declaration, or restore the empty if. The first two fail compilation; the third fails the no-summoner metadata-access assertion. Only that original-empty-if negative mode suppresses -Wempty-body/-Wmisleading-indentation to reach runtime behavior. Corrected tests need no warning suppression.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No leak claim. Earlier resolver/weight/catch-up fixtures remain separate.

## SUMMON-20261031-11 — exact-source-head integration skip

Skip user source `d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc` and associated full-DLL preparation until new user changes provide the missing unit integration. The source's defectUnitToPlayer at 15764–15770 requires canFoundCity() and isHero(); the military selection loop also calls canFoundCity() at revised 15819. Neither method exists in pinned baseline CvUnit.h or its CvDLLEntity.h inheritance interfaces. Both baseline and source inventories were checked; this feature supplies no CvUnit.h/.cpp replacement. Baseline offers isFound()/canFound(plot,...), but no hero classification contract is supplied here.

Do not import independent feature branches, invent a hero system, or remove the explicit source rule excluding heroes merely to get a green build. The local fixture models the supplied interfaces and cannot establish actual engine availability. The existing great-person/settler/hero exclusion intent and existing conversion code are preserved pending author implementation.

No MSVC7.1/full DLL, actual city transfer/slot behavior, real unit creation/conversion, real RNG, metadata/schema/save or gameplay validation. No automated DLL run triggered. Scoped code and this blocker record use [skip ci]. Preserve completed fixes and resume after the original head changes with the missing details.
