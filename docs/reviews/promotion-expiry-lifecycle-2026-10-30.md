# Promotion deadline ownership on removal — 2026-10-30

EXPIRY-20261030-05. Original PromotionTimedExpireTurns at 5f0e1235780e19a81a09aba91234bb0487489fcf; reused PromotionExpiryDraft-ChatGPT parent 5936fd7b89045e8f84d9b039c6c41f5745e2790d. Baseline 1.14 read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Full 75-branch inventory found no changed original heads against the global coverage ledger at f159c2c47de9c8a3b2dca31f02e5abf513d20305.

## Committed correction

CvUnit::setHasPromotion, CvGameCoreDLL/CvUnit.cpp:10471–10489: clear a promotion's scheduled deadline on every actual removal, independently of its metadata duration. Continue to schedule positive/negative metadata durations only on acquisition.

Previously the complete timing block was gated by GC.getInfo(ePromotion).getExpireTurns()!=0. applyEvent can schedule an ordinary promotion whose metadata duration is zero; when it expires or is removed manually, that outer condition prevented cleanup. Reacquiring that ordinary promotion does not set a metadata deadline, so the stale event deadline removes the new grant.

Concrete 100-percent-speed reproduction: metadata duration zero; event duration five at turn 100 sets deadline 105; expiry at turn 105 removes the promotion but leaves deadline 105; ordinary regrant at turn 110 is immediately removed by doExpireTempPromotions. Before/after extracted reproductions return held=false/deadline=105 and held=true/deadline=0 respectively.

The existing early return for unchanged held state remains intact; an attempted removal of an already absent promotion is still a no-op. No refresh/stacking policy is introduced. Earlier XANA markers, acquisition duration arithmetic, event overrides and prior sentinel fixes are preserved. Deadline cleanup performs no promotion-stat replay or recursive call.

## Verification

tests/promotion-expiry/lifecycle-check.cpp embeds the actual revised timing block, actual event promotion block and complete actual expiry method, with reduced game/info/map/unit interfaces and a wrapper preserving setHasPromotion's actual early-return/held-state/iChange sequence. It omits unrelated promotion stat changes and uses int deadlines rather than the production map's compact short storage.

450 strict C++03/ASan/UBSan grant/remove/regrant sequences passed: three promotion IDs, five metadata and five event durations (-2,-1,0,1,5), three speeds (50,100,200), manual removal versus automatic expiry where applicable; ordinary reacquisition, repeated removal and unaffected other IDs. Restoring the original block fails the deadline-cleared assertion. The focused finite-deadline reproduction separately confirms the regranted promotion is lost before the correction and retained afterward. No warning suppression. Leak detection disabled as unsupported; no leak claim.

Actual source inspection also found CvUnit::reset was deleted in baseline-derived code (constructor comment at line 24). The deadline map is a value member and baseline EnumMap.h documents numeric zero defaults and reset semantics. No speculative reset/uninit function was added. Constructor/destructor allocation reuse and actual map behavior are not tested by this fixture.

## Limits and next scope

This partial draft uses [skip ci]. No MSVC 7.1, full DLL, actual event application, savegame or gameplay validation is claimed. Remaining scopes: positive duration multiplication/addition overflow, compact short deadline range, scaled-to-zero turn-zero ambiguity, unversioned persistence relative to baseline, event/info/schema/cache integration and full engine lifecycle. Existing stale deadlines in already absent saved promotions are not migrated by this patch; a subsequent no-op removal stays a no-op. Do not infer save compatibility or complete runtime safety from these tests.
