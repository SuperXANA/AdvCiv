# Technology preference consumer declarations — 2026-10-29

Existing PreferenceFrameworkDraft-ChatGPT head 04f8986c3bca0c58aa43c82443a615d6052a3d67 reused. Original LeaderCivilizationDecisionPreferences source remains aac03388283a5ac316f6a19f6e3754a7435b6511.

PREFERENCE-20261029-03:
- CvPlayerAI::AI_techValue, CvPlayerAI.cpp:4659–4660: use TechPreferenceData const* for leader and civilization records. CvTechPreferenceInfo::getTechPreference returns const TechPreferenceData& (CvInfo_Civilization.h:524); the prior pointer assignment discards const and cannot compile normally.
- TechPreferenceData::isNotPreferredChoice, CvXMLStructs.cpp:22: definition was misspelled isbNotPreferredChoice, matching neither declaration (CvXMLStructs.h:15) nor consumer calls. Rename definition to declared name.
Existing XANA blocks, early preferred/not-preferred precedence, leader-then-civilization ordering, and final percent adjustments unchanged. No new scoring mechanics.

Validation: actual TechPreferenceData declaration and all four accessors plus both actual AI_techValue XANA consumer blocks compiled under strict C++03 (-Wall -Wextra -Werror -pedantic) with ASan/UBSan. Metadata lookup, globals and surrounding method are stubs. 144 configurations of flags and presence/selection indices, each also testing a missing tech entry, passed. Leader and civilization percentage application checked in order. No intervening AI_techValue computation, RNG, extreme integer ranges, actual XML loading/cache, MSVC7.1/DLL/game validation claimed. Partial draft uses [skip ci].

Remaining unit consumers/initialization and XML/cache integration remain queued; prior event/cleanup fixes preserved.
