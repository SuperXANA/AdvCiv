# Favorite combat storage ownership — 2026-10-29

Source assistant head def638cf5c927651ef0b692fc1fac74a27bc4915 on FavoriteUnitCombatDraft-ChatGPT. Original feature head remains 799082c323ea44335c66b9714e1a9bb365c12095.

FAVORITE-COMBAT-20261029-05: CvLeaderHeadInfo::~CvLeaderHeadInfo, CvInfo_Civilization.cpp:544–562 (new cleanup:560).
m_piUnitCombatWeights is initialized NULL, allocated by XML/cache paths, and deep-copied at line 540, but the destructor omitted deletion. Add SAFE_DELETE_ARRAY inside new XANA date markers. Existing pointer ownership and deep-copy behavior retained. No arithmetic, schema or stream changes.

Verification: actual complete revised destructor extracted with scalar pointer-member stand-ins for the preexisting arrays. Existing allocCopy algorithm used for new combat storage; 500 original/copy pairs, independent contents/mutations and null destruction checked. Strict C++03, -Wall -Wextra -Werror -pedantic, ASan/UBSan passed with leak detection disabled. Deterministic counter tracks 1,000 allocations through fixture allocations and deletion macro: corrected destructor leaves zero live blocks; removing cleanup fails the same assertion. This counter checks the fixture, not arbitrary engine allocation.

LeakSanitizer was attempted with detect_leaks=1 for both variants but is unavailable here: cannot open /proc/2/task; fatal error says it cannot work under ptrace. No LSan success claimed. No full CvLeaderHeadInfo initialization/copy, XML/cache round trip, MSVC/DLL/game result. Partial draft skips CI.

Header, actual constructor/copy/destructor and all new pointer references in implementation read. Existing assistant branch reused; prior fixes retained. tests/favorite-ownership/check.cpp contains the counted fixture.
