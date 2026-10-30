# Promotion expiry sentinel handling — 2026-10-29

Read-only source: PromotionTimedExpireTurns at 5f0e1235780e19a81a09aba91234bb0487489fcf. Existing assistant head before this change: ac7b831ea5305cb6c279546e5b29ba2d78251fd2. Baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6. All 75 current branch heads were inventoried; no original feature head changed against the recorded inventory. The retired dll-build-debug ledger row is historical, not a current branch. The existing expiry assistant branch was reused.

## Implemented findings

EXPIRY-20261029-03 — CvUnit::doExpireTempPromotions, CvGameCoreDLL/CvUnit.cpp:728–734.
The expiry map is ArrayEnumMap<PromotionTypes,int,short> (CvUnit.h:1217). Baseline EnumMap.h documents numeric default zero. Untimed promotions leave that default untouched because setHasPromotion's XANA metadata block only schedules nonzero durations (10471 onward). The old loop skipped only -1, so every held ordinary promotion with default deadline zero was removed on the next expiry pass. Skip nonpositive entries: zero means no scheduled deadline; -1 retains infinite duration. Positive deadlines still expire at deadline <= current turn. This intentionally does not resolve positive durations scaled to zero at game turn zero, where the representation is ambiguous.

EXPIRY-20261029-04 — CvUnit::applyEvent, CvGameCoreDLL/CvUnit.cpp:11724–11734.
The event block multiplied every nonzero duration by train percent and added the current turn. Negative durations therefore became finite past deadlines (or overflowed for extreme negative values), unlike the same feature's setHasPromotion path at 10479–10490, which normalizes negative durations to -1 and avoids arithmetic. Apply that already implemented convention to events. Event duration zero still preserves normal promotion timing. Positive duration scaling and division order remain unchanged. XANA enclosing markers preserved.

## Verification

tests/promotion-expiry/sentinel-check.cpp embeds the actual revised complete doExpireTempPromotions method and actual applyEvent promotion block, with minimal game/event/unit interfaces. Strict C++03, -Wall -Wextra -Werror -pedantic, address and undefined-behavior sanitizers passed 172 cases: absent/held promotions, deadlines -1/0/positive/INT_MAX, current turns zero through INT_MAX, NO_PROMOTION and three valid IDs, durations INT_MIN/-2/-1/0/positive, and four train percentages. The fixture asserts both retained/removed state and write counts/deadlines.

Restoring the original method/block fails the ordinary-promotion assertion. Running the original event block separately under UBSan reports signed overflow for INT_MIN * 50. Leak detection disabled because unsupported in this environment; no leak claim. These are extracted-code fixtures, not the entire engine, MSVC 7.1 or DLL/game validation.

## Remaining limits

No DLL run triggered: partial draft uses [skip ci]. Save/load remains unversioned relative to the baseline layout, reset/reuse needs review, the map's short compact representation and large positive deadline arithmetic need review, and info constructors/schema/cache/UI/game integration are not certified. Do not infer full save compatibility from the sentinel fixture. Earlier EXPIRY-01/02 fixes and tests are retained; this review supersedes only their listed zero/infinite-duration outstanding item.
