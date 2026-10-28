# Hated civic/religion scoped refinement — 2026-10-28

Original source: HatedCivicReligionDiplomacy at a9c1a754b5e9b64e10ceaa22fd02fa78f3718785.
Isolated branch: HatedDiplomacyDraft-ChatGPT.
Code: [bd9fe6e0816ed0f6c5311b5fb2aefa6505df4e5e](https://github.com/SuperXANA/AdvCiv/commit/bd9fe6e0816ed0f6c5311b5fb2aefa6505df4e5e).

This pass turns earlier partial-review observations into actual committed code
and executable tests of source fragments. It does not present those observations
as newly discovered defects. Branch inventory found no changed original heads.
The four existing missing-implementation skip gates remain in force, and no
unchanged failed build was retried. The original feature is self-contained.

## HATED-20261028-01 — history written to the wrong array

CvPlayerAI::AI_changeHateCivicCounter, lines 18779–18785, specifically assignment
18783: both sides referenced m_aiFavoriteCivicCounter. Thus the hated-civic path
in AI_doCounter (19573–19583) changed favorite history while leaving hate history
unchanged. The subsequent assertion checked the untouched hate counter, so it
would not detect this cross-write.

Both references now use m_aiHateCivicCounter. Existing increment/decrement,
assertions and caller policy are retained. Example: favorite 17, hate 3,
delta +2 previously yielded favorite 19, hate 3; the repair yields 17 and 5.

No new saturation policy or release-mode bounds handling is introduced. Existing
index and nonnegative-history contracts, and signed integer limits, still apply.

## HATED-20261028-02 — cache writer uses an undeclared name

CvLeaderHeadInfo::write (starts 821), line 877: m_iHateeligionAttitudeChangeLimit
does not match the actual header member m_iHateReligionAttitudeChangeLimit.
The reader at line 727 already uses the correctly spelled name. The repair
writes that declared field in the existing stream position. This addresses
compilation when this cache path is compiled, without altering field order or
adding data. No cache compatibility or whole-class compilation is claimed.

## Verification

Run python tests/hated-diplomacy/check.py.
The fixture extracts the actual counter method and declaration plus the two
marked cache read and write blocks. Six int members come from the source header.
Minimal player/stream stubs replace engine dependencies.

Passed g++ -std=c++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan;
ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1.
Checks cover each of four player slots with +2, -2 and zero changes, isolation
of other slots/favorite history, six distinct cache values, exact stream order,
round-trip values and an untouched trailing sentinel.

Independent negative controls restore only one original defect at a time:
the counter version fails the favorite-history assertion; the cache version
fails compilation on the undeclared member. The published diff was inspected:
exactly two production lines changed, all inside existing XANA blocks.

## Limits / remaining work

No workflow was added and no DLL build was triggered. This sparse source
refinement is not a complete pinned-1.14 overlay or MSVC 7.1 verification.
Tests do not execute full AI_doCounter, attitude calculation/cache invalidation,
the real stream implementation, save migration, XML loading, or gameplay.

Previously recorded religion-scoring arithmetic remains unresolved; this pass
does not choose a replacement scoring rule. Player-save version compatibility,
remaining integration and cache metadata need separate review before whole-feature
validation. Missing mechanics are not invented to obtain a build.
Original branches, read-only 1.14 and XANA 05-24-2025 markers are preserved.
