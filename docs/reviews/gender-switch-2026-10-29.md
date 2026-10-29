# Gender ideology switch scope — 2026-10-29

GENDER-20261029-06. Existing GenderCounterDraft-ChatGPT head9bcb4c8a9663665d459ce2f4bffa175a0e910e0a reused; original GenderSpecificDiplomacy remains80e6ec595041cf335d5437b7bedea4fcaa61622b.

CvPlayerAI::AI_ideologyAttitudeChange, original CvPlayerAI.cpp:19002–19017: ALLY_GENDER and ENEMY_GENDER declare initialized local variables without case scopes. Following case labels jump past these initializations. Enclose each gender case in braces, retaining both original break statements and all predicates. XANA markers, shared-preference matching (not actual-gender matching), iMatching aggregation and downstream formula unchanged.

Verification: actual complete switch, including unchanged religion/civic cases, compiled strict C++03 (-Wall -Wextra -Werror -pedantic) with ASan/UBSan. Controlled player metadata interfaces; 729 combinations of gender preference/religion values, five case results each, checked. Actual outer city visibility iteration, fixed-point formula, real XML and complete method not tested. Restoring original switch fails compilation with jump-to-case/crosses-initialization errors. No MSVC7.1/DLL/game result; partial draft [skip ci].

Current full branch inventory checked against latest ledger; no new non-assistant source changes. Existing native first-impression success retained in ledger. Gender save version/array reconstruction and UI/basic-info consistency remain unverified.
