# Unique religion native eligibility — 2026-10-28

Source UniqueCivicsReligions: d0fc7c0f93320e112903416c17bb2a2030819d60.
Previous draft 20ddb4c784af340adde3cec2dc615967067fe5a5; code https://github.com/SuperXANA/AdvCiv/commit/30fb84064c9c791868d70582875e7a8e01814df4.
Read-only 1.14 pin: 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## RELIGION-20261028-01 — existing prerequisite predicate is disconnected

Affected function: [CvPlayer::canDoReligion, header lines 417–424](https://github.com/SuperXANA/AdvCiv/blob/30fb84064c9c791868d70582875e7a8e01814df4/CvGameCoreDLL/CvPlayer.h#L417).
Existing predicate: [CvPlayer::isAllowedReligion, implementation line 6968](https://github.com/SuperXANA/AdvCiv/blob/30fb84064c9c791868d70582875e7a8e01814df4/CvGameCoreDLL/CvPlayer.cpp#L6968).

The source adds isAllowedReligion, which conjunctively checks optional PrereqCivilization and PrereqLeader against actual civilization and leader identity. But canDoReligion remains the baseline city-presence test and never invokes the predicate. The source's corresponding civic path already calls isAllowedCivic from canDoCivics. A present religion can therefore pass native religion eligibility despite an incompatible configured identity.

The proposal applies the existing isAllowedReligion predicate before the city-presence test for real religions. It does not create new metadata, identity rules or missing mechanics. The NO_RELIGION sentinel bypasses the metadata predicate and retains the original getHasReligionCount(eReligion)>0 evaluation, because source callers such as verifyStateReligion can supply it. No change to the existing predicate or source data is made.

Normal canConvert, verifyStateReligion and conversion-eligibility consumers call canDoReligion and can therefore observe the restriction. These callers were read, not executed in the fixture. Explicit forced conversion remains governed by the existing bForce bypass; this patch does not claim to constrain all forced assignments, founding, spread or event effects. Identity changes may make an existing state religion ineligible through the existing verifyStateReligion path; in-game consequences remain untested.

## Verification

python tests/religion-eligibility/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. LeakSanitizer disabled; UBSan halt_on_error enabled.

The fixture compiles the actual revised inline canDoReligion body and actual unchanged isAllowedReligion definition. It enumerates two player civilizations, two player leaders, optional/matching/mismatching civilization and leader prerequisites and absent/present religion counts: 72 combinations. It checks prerequisite failures short-circuit the count query, permitted cases retain the presence check, and NO_RELIGION follows the original count result without a metadata lookup.

Engine objects, metadata and city counts are stubs. Actual info registration/loading, Python/Boost exports, count enum-map behavior, caller execution, AI adoption weights, force conversion, real save/gameplay and multiplayer remain unverified. These are direct method checks, not a full header/translation-unit build, MSVC 7.1 or DLL result. No workflow or DLL build was triggered.

Only CvPlayer.h changes in production this pass, adding the gate within XANA 06-27-2026 markers. Original branches and 1.14 are unchanged; the existing CivicScrollDraft-ChatGPT branch is reused. Prior civic/religion UI findings remain separate and are not reopened.

## Coverage

Fresh inventory showed no original source-head changes. SimpleStorageChangeDraft's different head was already-delivered documentation. The missing-implementation skip rules remain in effect. This gate connects already-supplied functionality; it does not fill a missing feature specification to obtain a build. Partial reviews and failed/unverified native states remain, so the stop gate is false.
