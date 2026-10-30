# Summon weight domain and RNG bounds — 2026-10-30

SUMMON-20261030-07. Read-only source LeaderCivilizationSummoningRandomEvents at d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc; existing SummonCatchupDraft-ChatGPT parent 926641f1ffdda15e7347797fee6e0be5ded00b6b reused. All 75 current branch heads checked against the latest ledger; no original heads changed. Read-only 1.14: 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Completed correction

CvPlayer.cpp contains these anonymous-namespace selectors within the existing XANA 08-22-2026 feature block:

| Function | Old line | Revised line |
| --- | ---: | ---: |
| selectWeightedSummonLeader | 15392 | 15405 |
| selectWeightedSummonCiv | 15426 | 15440 |
| selectCompatibleCivForSummonLeader | 15461 | 15476 |
| selectCompatibleLeaderForSummonCiv | 15516 | 15533 |

The first two total every weight, including negative values, while their selection loops skip weights <=0. Example [2,-1,2] totals 3 but selects from four positive tickets, biasing the result; [-2,0,1] returns no selection despite one valid positive candidate. Sum the same positive domain used for selection.

All four previously used unchecked int addition and could pass sums >65535 to SyncRandNum. The actual pinned CvRandom.h:16–35 documents the 0..65535 bound, asserts it, then casts the int bound to unsigned short. Large weights can overflow before the call or silently narrow the RNG bound in nonasserting builds.

Add shared addSummonWeight at revised 15390–15400: nonpositive weights contribute nothing; a positive weight is accepted only if <=65535-currentTotal, checked before addition. Each selector returns its existing NO_LEADER/NO_CIVILIZATION sentinel on an unsupported sum, before drawing. Compatible uniform paths also use checked unit contributions. Ordinary supported draws retain one synchronized RNG call and their positive-weight distribution.

This is explicit rejection of unsupported totals, not arbitrary-large-weight support, clamping or invented rescaling. XML authors must keep each eligible weighted total <=65535 until a separately reviewed wider-range selection algorithm exists. Master-resolver fallback and later RNG consumption are outside this selector-only claim.

## Verification

tests/summon-weights/check.cpp embeds the actual helper and four complete revised selector functions with enum/metadata/game/RNG stand-ins. Strict C++03 (-Wall -Wextra -Werror -pedantic), ASan and UBSan passed 131 weight families and 526452 weighted draw/result checks, plus absent-array/uniform/empty-pool checks. Every possible roll is enumerated for the supported tested distributions, including total 65535. Invalid totals 65536 and INT_MAX combinations produce no selector RNG call. Negative and INT_MIN weights are ignored consistently.

Original-selector negative controls reproduce the negative-weight result mismatch and UBSan signed overflow for INT_MAX+INT_MAX. Existing compatible-civilization and compatible-leader fixtures also passed after including the shared helper; their earlier compatibility, lead-any, invalid-ID and pool behavior remains covered. The leader fixture now supports SUMMON_SOURCE override like its counterpart. Leak detection disabled as unsupported.

No MSVC7.1/full DLL/live RNG/game result; no DLL triggered. Existing draft uses [skip ci]. No change to event slot creation, eligibility enumeration, transfer logic, XML schema or synchronization policy outside these selectors. Larger-weight support, full resolver execution, repeated eligibility RNG and whole-feature integration remain unverified.
