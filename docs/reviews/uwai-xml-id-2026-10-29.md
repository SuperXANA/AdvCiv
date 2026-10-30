# UWAI aspect ID conversion — 2026-10-29

UWAI-20261029-02. Read-only source LeaderSpecificUWAIAspectWeights at d38c565a981984a7c34417a9d9529fec2bcd7165; assistant parent 0bbb2bbb7456d38e57ac79b736667816cd8244f8, existing UWAIWeightsDraft-ChatGPT reused. Complete 75-branch inventory found no changed original heads against the latest ledger. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Committed correction

CvGameCoreDLL/WarUtilityAspect.h contains 29 xmlID overrides assigning GC.getInfoTypeForString's int result directly to mutable WarUtilityAspectAITypes m_eXMLID. The baseline CvGlobals.h:185–188 declares an int return; supplied CvEnumMacros.h:48 registers the info category and MAKE_INFO_ENUM at 221–226 declares an enum. Standard C++03 does not implicitly convert int to that enum in assignment. Add an explicit (WarUtilityAspectAITypes) cast at each cache assignment, matching the baseline's explicit enum casts around other getInfoTypeForString consumers. Preserve all XANA blocks, lookup strings (including ILL_WIL), -1 retry semantics and cache behavior.

| Function | WarUtilityAspect.h line |
| --- | ---: |
| GreedForAssets::xmlID | 176 |
| GreedForVassals::xmlID | 195 |
| GreedForSpace::xmlID | 206 |
| GreedForCash::xmlID | 217 |
| Loathing::xmlID | 229 |
| MilitaryVictory::xmlID | 244 |
| Assistance::xmlID | 264 |
| Reconquista::xmlID | 278 |
| Rebuke::xmlID | 290 |
| Fidelity::xmlID | 302 |
| HiredHand::xmlID | 314 |
| BorderDisputes::xmlID | 328 |
| SuckingUp::xmlID | 340 |
| PreEmptiveWar::xmlID | 352 |
| KingMaking::xmlID | 365 |
| Effort::xmlID | 388 |
| Risk::xmlID | 401 |
| IllWill::xmlID | 414 |
| Affection::xmlID | 433 |
| Distraction::xmlID | 447 |
| PublicOpposition::xmlID | 459 |
| Revolts::xmlID | 471 |
| UlteriorMotives::xmlID | 485 |
| FairPlay::xmlID | 497 |
| Bellicosity::xmlID | 511 |
| TacticalSituation::xmlID | 523 |
| LoveOfPeace::xmlID | 539 |
| ThirdPartyIntervention::xmlID | 551 |
| DramaticArc::xmlID | 566 |

## Verification

The actual 29 revised method definitions were extracted into tests/uwai-info/xml-id-check.cpp. A stand-in global lookup retains the baseline int-return contract; wrapper classes supply the mutable enum cache. A surrogate enum supports the numeric test IDs; this does not compile the complete production enum generation, classes or engine headers. Strict C++03, -Wall -Wextra -Werror -pedantic, ASan and UBSan passed 87 cases: all 29 keys in forward and reverse numeric-ID assignments (two calls, one lookup each), plus missing-key retries (two calls/lookups). Restoring the original definitions reproduces invalid int-to-enum compiler errors. All 29 literal names match distinct Type entries in the supplied CIV4WarUtilityAspectAIInfos.xml. Leak detection disabled as unsupported; no leak claim.

No observed MSVC7.1/full DLL/game result. This partial draft uses [skip ci]. Earlier UWAI-01 metadata class correction retained. Full XML loading/global registration, fixed-point and reporting consumers, invalid lookup handling and zero override policy remain review scopes. Missing keys still return -1 and retry, preserving existing behavior; the consumers' assertions alone are not certified release-mode bounds protection.
