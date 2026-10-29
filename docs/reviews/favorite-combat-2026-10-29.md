# Favorite unit combat adjustment — 2026-10-29

Original source: LeaderSpecificFavoriteUnitCombats at 799082c323ea44335c66b9714e1a9bb365c12095.
Existing assistant branch inventory checked; no matching feature draft existed. Earlier scoped diagnostic files were inspected, then actual source read before preparing these committed refinements.

FAVORITE-COMBAT-20261029-01: CvPlayerAI::AI_unitValue, CvPlayerAI.cpp:14465–14470 (new braces end at 14471). Original if guards multiplication only; following divide by 100 is unconditional. A unit valued 2500 becomes 25 even with zero preference; a unit valued 50 becomes 0. Put multiplication and division together inside the positive-weight guard. Existing positive bonus formula and integer weight conversion retained.

FAVORITE-COMBAT-20261029-02: CvLeaderHeadInfo::getFavoriteUnitCombatWeight, CvInfo_Civilization.cpp:667–673. Return neutral zero for negative/out-of-range unit combat IDs before indexing, allowing NO_UNITCOMBAT in generic unit evaluation. Existing valid bounds assertion, null-array fallback and /100 conversion retained.

FAVORITE-COMBAT-20261029-03: CvCityAI building evaluation, original CvCityAI.cpp:4130: add missing semicolon after favorite-combat contribution. Syntax-only correction.

Verification: actual revised getter and AI_unitValue adjustment block extracted into strict C++03 -Wall -Wextra -Werror -pedantic fixture with ASan/UBSan. 29 weights (-200..500 by25), 101 input values (0..1000 by10), two valid IDs and -1/out-of-range2 checked; null metadata pointer checked. Metadata count and unit interfaces stubbed. Full functions/engine metadata/building path were not compiled. No MSVC7.1/DLL/game result claimed; [skip ci].

Deferred: building-value loop at 4067–4077 passes a UnitCombat map key into unit-info/canTrain paths; inspect baseline contracts and map macro typing before revising. Metadata ownership/copy/cache/schema and complete integration remain partial. No formula redesign or feature merging.
