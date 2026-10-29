# Custom diplomacy contact integration — 2026-10-29

Source CustomAIDiplomacyComments at ca3531fac64b2e70ea66b98745e45733da1f0c37. Baseline remains read-only 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Actual marked AI contact call/complete AI_bragAboutFriend read; actual header, enum additions, Python, diplomacy XML, README and other supplied C++ files searched. This is an independent feature, not covered by successful LLM text-cache builds.

CONTACT-20261029-01: CvPlayerAI::AI_bragAboutFriend, CvPlayerAI.cpp:22215–22219; CvPlayerAI.h:816–818.
m_aeLastBragFriend is declared mutable PlayerTypes[MAX_CIV_PLAYERS], then read as >0 to block repetition. Searches of all supplied CvPlayerAI.cpp show no initialization, write, reset, persistence or expiry for this new member. Existing m_aeLastBrag (unit type) has separate lifecycle and is not this state. Reading the new array may depend on indeterminate memory; storing PlayerTypes would also not establish a duration/expiry rule. A fix needs the intended repeat suppression policy (per recipient/per named friend, delay and reset semantics), not a guessed timer. No arbitrary implementation supplied.

CONTACT-20261029-02: AI_bragAboutFriend lines 22221–22228 requests GC.getAIDiploCommentType("BRAG_ABOUT_FRIEND") and starts diplomacy. Supplied CIV4DiplomacyInfos.xml has existing UNIT_BRAG but no friend-brag entry; supplied CvDiplomacy.py likewise has UNIT_BRAG handling but none for friend brag. Contact enum was added at CvEnums.h:1205, but dialogue and response integration remain absent. A meaningful feature test cannot certify the missing comment or invent its text/response behavior.

Further observed boundary: call site 21494–21497 permits AI recipients and the method unconditionally calls beginDiplomacy; human-contact gating and candidate knowledge restrictions require review after implementation resumes. Not repaired piecemeal around missing behavior.

Disposition: skip this exact original head until user source changes provide missing implementation, in accordance with missing-implementation policy. No corrective code/feature branch or DLL build; no MSVC result claimed. Documentation stored on existing assistant ledger branch only; independent production C++ untouched. This prevents repeated unchanged build attempts and avoids inventing gameplay/dialogue. Other eligible source review remains queued.
