# Gender attitude helper follow-up — 2026-10-28

Source GenderSpecificDiplomacy: 80e6ec595041cf335d5437b7bedea4fcaa61622b.
Previous draft dd611543024315f513c2f58b6b7e601936b7df40; new code https://github.com/SuperXANA/AdvCiv/commit/eefccff731f8cf35cbcd2ed9bae249974d0f9c61.
1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## GENDER-20261028-04 — unreachable reversal predicates and broken helper syntax

Affected functions:
- [AI_getFavoriteGenderAttitude, line 8058](https://github.com/SuperXANA/AdvCiv/blob/eefccff731f8cf35cbcd2ed9bae249974d0f9c61/CvGameCoreDLL/CvPlayerAI.cpp#L8058)
- [AI_getHateGenderAttitude, line 8083](https://github.com/SuperXANA/AdvCiv/blob/eefccff731f8cf35cbcd2ed9bae249974d0f9c61/CvGameCoreDLL/CvPlayerAI.cpp#L8083)

Original draft favorite helper first requires eWeLike == eTheyAre. bPreferOwn then equals eWeAre == eTheyAre. Its reversal test chooses eWeAre != eTheyAre when that equality is true, or the equality when false. Either way it is false. The following extra identity test in the shared-favorite condition is always true under the same gate.

The hated helper similarly requires eWeHate == eTheyAre, and defines bPreferOwn as eWeAre != eTheyAre. Its reversal test again contradicts the definition on both branches; the following identity test is always true.

Thus both reversal branches are unreachable. Their expression -iAttitude also lacks assignment, but changing that expression alone would not make the reversal reachable. The refinement removes the unreachable branches and redundant identity conditions/variables. It retains the actual effective rules: a matching target sharing the favorite preference adds one; a target favoring the hated identity subtracts one. NO_GENDER, conflicting own favorite/hate, and nonmatching target gates remain. This is a behavior-preserving simplification of the predicates after repairing syntax, not a newly invented reciprocal-dislike rule.

Two missing closing parentheses at original draft lines 8079/8110 prevent compilation. Repaired limit expressions are at new lines 8073/8098. The sign-based divisor/limit selection, distinct counter getters, and ALLY_GENDER/ENEMY_GENDER markers remain unchanged. Existing XANA 10-25-2025 boundaries are preserved.

If reciprocal dislike was intended to reverse attitude, its trigger needs an explicit mechanics decision: the current identity predicates cannot achieve it. No speculative replacement trigger is activated in this draft.

## Verification

python tests/gender-attitude/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined; LeakSanitizer disabled.

The fixture extracts the actual two helpers. It enumerates four identity values (NO_GENDER plus three synthetic identities) independently for own identity, own favorite/hate, target identity and target favorite/hate, and base attitudes -3..3: 28,672 combinations. It checks early returns, effective base +/-1 results, matching counter/ideology marker forwarding, and sign-based divisor/limit arguments. It also asserts the original reversal predicates are false and original extra shared-preference identity predicates true whenever their early gates permit evaluation.

Engine/info access and AI_ideologyAttitudeChange are stubs. The latter returns zero and records arguments; actual population weighting and its switch implementation are not validated. Configuration extrema, metadata loading, cached attitudes, paranoia, save streams, whole-feature C++ compilation, MSVC 7.1, DLL, gameplay and multiplayer remain unverified. No full DLL build was triggered; no workflow was added.

Prior findings GENDER-20261027-01..03 remain in their original report. This follow-up does not repeat or replace their counter/scalar repairs. The existing assistant branch was reused, the original feature branch remains untouched, and only CvPlayerAI.cpp plus this fixture and documentation changed in this pass.

## Coverage

Fresh inventory showed no changed source heads. The CivicScroll head difference was already-published spell evidence documentation. UnitStatusEffects stays deferred; the ScaledNum alert stays closed. Partial reviews and failed/unverified native builds remain, so the stop gate is false.
