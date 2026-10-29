# Dynamic rank metadata naming — 2026-10-28

Source: LeaderSpecificDynamicRankBonusDiplomacy, ff5560a1f2af752be1446e8bbd8d37bcdbe64a1e.
Finding RANK-20261028-01. XANA markers retained.

Completed:
- CvInfo_Civilization.h:309: correct m_iShareRelativeProgressAttitudeChangLimit to ...AttitudeChangeLimit, matching its accessor and constructor/read/write.
- CvInfo_Civilization.cpp:464,736,880,1008: use the header's existing ...AttitudeChangeDivisor member consistently in construction, cache read/write and XML loading.
- CvPlayerAI::AI_doCounter, CvPlayerAI.cpp:19516: call the declared getShareRelativeProgressAttitudeChangeDivisor().
The XML tag iShareRelativeProgressAttitudeDivisor is intentionally preserved; no XML migration or stream order change.

Why: the original header accessor references an undeclared limit member, while constructor/load/store reference an undeclared divisor member; the counter code calls an absent accessor. These are compile blockers, independent of gameplay inputs.

Verification:
An extracted actual four-accessor/four-field C++03 fixture compiled with -Wall -Wextra -Werror -pedantic and ASan/UBSan and returned the four distinct initialized values correctly. A negative control restoring the original limit spelling failed compilation. The fixture uses a small synthetic constructor, not the full CvLeaderHeadInfo class. No DLL build, native MSVC 7.1 result, cache/XML integration test or game test is claimed.

Deferred:
AI_getShareRelativeProgressAttitude (8663–8695) needs a separate arithmetic/mechanics pass: integer divisions occur before fixed-point conversion, and the attitude threshold doubles as a rank multiplier. This commit does not invent a replacement formula. The full source class and metadata integration remain unverified. No DLL build is appropriate for this naming-only partial draft; CI skipped.
