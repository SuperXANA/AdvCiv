# Gender paranoia block refinement — 2026-10-28

Code 0d69e69e0d491dd6ec49249351d48455f05764bf, reused GenderCounterDraft-ChatGPT.
Original source GenderSpecificDiplomacy 80e6ec595041cf335d5437b7bedea4fcaa61622b.
No original source heads changed in this inventory.

## GENDER-20261028-05

CvPlayerAI::AI_updateStrategyHash, CvPlayerAI.cpp, XANA block 25723–25754:
- Line 25743 assigned bPreferOwn after its declaration inside the favorite-gender
  conditional had left scope. The hated-gender conditional now declares its own
  bool const variable. The favorite path variable (25730) is also const.
- Lines 25734 and 25747 passed the iterator object to GET_PLAYER. The code now
  calls itRival->getGender(), consistent with the actual AgentIterator.h
  operator-> and the actual branch CvPlayer.h getGender() const declaration.

The branch's coarse same-versus-other-gender predicates are preserved, as are
NO_GENDER gating and the per-rival -10/+10 changes. This does not substitute
a rule that matches only the exact favorite/hated identity when several gender
types exist. Such a gameplay change is outside this compilation repair.

## Verification

python tests/gender-paranoia/check.py extracts and executes the actual marked
block with iterator, rival and metadata stubs. Strict C++03 -Wall -Wextra
-Werror -pedantic plus ASan/UBSan passed. UBSAN_OPTIONS=halt_on_error=1;
ASAN_OPTIONS=detect_leaks=0.

1280 configurations cover own/favorite/hated values -1 through 2, zero through
four rivals and four target seeds, at starting paranoia 200 and -20.
Reference expectations preserve the source predicates, not a newly chosen rule.
An isolated negative control restoring only the old local-variable assignment
fails compilation: bPreferOwn was not declared in this scope.
Real iterator/operator and player method declarations were read from source;
the fixture does not compile the real iterator or run its filtering logic.

No DLL workflow was added or triggered. Code and docs commits use [skip ci].
The rest of AI_updateStrategyHash, ideology weighting, stream migration,
metadata/UI integration and game balance remain unverified. Existing older
findings are retained, not presented as newly discovered.
Original branches, baseline and existing XANA date markers remain unchanged.
