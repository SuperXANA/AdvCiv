# FFHRaceTypes demographics draft — 2026-10-27

## Scope and immutable inputs

Source branch: [FFHRaceTypes](https://github.com/SuperXANA/AdvCiv/tree/a50b62ccd1ec72672c3b8b4814ad03230088ea18), source head a50b62ccd1ec72672c3b8b4814ad03230088ea18, root tree f1b396344f9237dd511ba07c5b8042c2083f7e81.
Read-only baseline: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

No original branch head changed since the preceding coverage snapshot. The SidSaysDiscoveryBuild documentation head difference is the already delivered build-evidence update. This pass resumes the pending first-pass rotation rather than rebuilding an unchanged failed target.

All 27 source blobs were retrieved. The XANA blocks across 21 DLL files and the supplied race/class XML and marked schema additions were read. This refinement is deliberately limited to selection arithmetic, the typed lock accessor, and unit initialization scope. It preserves the sparse feature source and every unrelated file; it is not a complete-base overlay or install-ready race feature. XANA 06-21-2025 boundaries/dates are retained around changed feature code and the new helper.

## RACE-20261027-01 — race pools exceed the baseline RNG interface

[buildRaceInformationCache](https://github.com/SuperXANA/AdvCiv/blob/a50b62ccd1ec72672c3b8b4814ad03230088ea18/CvGameCoreDLL/CvPlayer.cpp#L19760) sums positive priorities in signed int and passes the total directly to getSorenRandNum. [getDemographicRace](https://github.com/SuperXANA/AdvCiv/blob/a50b62ccd1ec72672c3b8b4814ad03230088ea18/CvGameCoreDLL/CvPlot.cpp#L8434) passes total plot culture to the same API.

The apparent int parameter does not imply a 32-bit random bound. Pinned [CvGame::getSorenRandNum](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvGame.h#L824) delegates to [CvRandom::getInt(int)](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvRandom.h#L25), which asserts a maximum bound of 65,535 and narrows it to unsigned short. For example, 65,536 becomes zero in Release and the draw is zero; selection then favors the first eligible bucket instead of the intended weighted pool. A sufficiently large sum can also overflow before the call.

The committed RaceWeightedRandom.h keeps the existing single draw for totals 1–65,535. Larger positive int totals use three explicitly sequenced bounded draws (15+15+1 bits), reject the high incomplete modulo interval, then reduce into the requested range. No call exceeds the baseline 16-bit bound. This avoids adding modulo bias under the uniform-draw abstraction; no claim of independent or cryptographic engine RNG output is made. Explicit sequencing matters because C++03 operand evaluation order is unspecified.

Both selectors use the helper. Empty priority pools return NO_RACE without consuming a draw. The priority sum is checked before each addition; totals above INT_MAX report an error and return NO_RACE without signed overflow or RNG consumption. The plot selector's existing countTotalCulture implementation is retained; supporting a plot culture total beyond the baseline int representation is outside this refinement.

## RACE-20261027-02 — ordinary units bypass race initialization

The only [initRaceType call](https://github.com/SuperXANA/AdvCiv/blob/a50b62ccd1ec72672c3b8b4814ad03230088ea18/CvGameCoreDLL/CvUnit.cpp#L347) is inside the isWorldUnit condition in CvUnit::finalizeInit. Ordinary units therefore bypass their explicit XML race and demographic fallback path.

Move the same XANA-bracketed call outside that condition, after the world-unit notification block and before unitCreated is reported. The existing resolution order remains unit XML default, then plot demographic result, then the owner's cached ordinary race. This code belongs to finalizeInit, despite the original helper comment referring to init; the comment is corrected.

## RACE-20261027-03 — lock accessor takes the wrong enum category

[CvRaceInfo::get](https://github.com/SuperXANA/AdvCiv/blob/a50b62ccd1ec72672c3b8b4814ad03230088ea18/CvGameCoreDLL/CvInfo_Civilization.h#L559) takes inherited IntElementTypes, while LOCK_TO_CIV is declared in the derived BoolElementTypes enum and is consumed as such in the selector. Distinct enum types do not implicitly convert to one another here. Taking BoolElementTypes restores the declared Boolean API and forwards through CvXMLInfo's Boolean overload.

## Mechanics preserved and proposed

Civ-locked races remain eligible for the owner's ordinary priority roll and excluded from its visible-culture roll. Nonpositive priorities remain excluded. The plot selector keeps its original total-culture denominator, including skipped-owner and otherwise unselected culture mass. That residual mass can lead to NO_RACE and then the owning unit's fallback. It is not silently renormalized into a foreign-culture-only distribution.

Moving race initialization makes ordinary creations participate in the intended mechanic. It also consumes demographic RNG draws for creations that previously bypassed initialization. Multiplayer peers need matching code; deterministic replay or multiplayer compatibility with the old implementation is not claimed. Large-pool behavior necessarily changes because the old direct draw exceeded the RNG contract. Save compatibility is not established.

Future integration should explicitly define race inheritance for gifting, capture and upgrade, cache readiness at starting-unit creation, and versioned persistence. This draft preserves those unresolved paths rather than inventing lore rules.

## Verification and limits

Run:

```
python3 tests/race-demographics/check.py
```

Passed strict g++ C++03 with -Wall -Wextra -Werror -pedantic, ASan and UBSan. LeakSanitizer is disabled for host compatibility.

The fixture compiles the actual helper, CvPlayer priority selector, CvPlot demographic selector, CvRaceInfo Boolean enum/accessor and existing CvUnit::initRaceType method with engine dependencies stubbed. It exercises weighted bucket boundaries; lock filtering; empty/negative weights; 65,535 and 65,536; large int pools; rejection/retry at 65,537, 2^30+1 and INT_MAX; checked sum overflow; plot residual/fallback mass; explicit and demographic unit race resolution; and the exact bounded RNG call sequence.

A separate structural check of the actual finalizeInit body confirms one race-init call at unconditional function scope, outside the world-unit block and before unitCreated. This is not an execution test of the full unit initializer. It is not a whole-header/translation-unit compiler check either; only the listed methods/accessor are compiled.

No DLL workflow is added and no DLL build is triggered. The feature remains an incomplete integration draft: for example the supplied civilization/leader info declarations and readers do not yet form a consistent set (m_piRacePriorities is used in the civilization reader/constructor but is absent from that class's header). Lifecycle/cache readiness and the new stream fields also need integration work before a meaningful whole-feature build. Those areas are recorded as pending scope, not represented as fixed or validated by the fixture.

A later coherent native build must follow the complete pinned 1.14 overlay procedure and copy the then-current named dll-build workflow on this same isolated branch. No historical DLL artifact, standalone fixture, or build of an unrelated feature is substituted for that validation. No game startup, XDR loader, save/load, real engine PRNG distribution, or multiplayer test was run.

## Coverage continuation

The companion ledger carries all prior evidence forward, changes FFHRaceTypes from pending to partial scoped review, and records this draft separately from the unchanged source head. Ten first-pass branches remain pending, so the stopping condition is not met.

Code revision: [df98a66934ff1ecc810e19357c686834c6cfac24](https://github.com/SuperXANA/AdvCiv/commit/df98a66934ff1ecc810e19357c686834c6cfac24). The documentation/coverage follow-up does not modify code.
