# Favorite combat building key — 2026-10-29

Continuation on FavoriteUnitCombatDraft-ChatGPT, prior assistant head 4345e5cb350407f069d561e9855ae81dac62972f. Original source unchanged at 799082c323ea44335c66b9714e1a9bb365c12095; baseline read only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

FAVORITE-COMBAT-20261029-04: CvCityAI::AI_buildingValue, CvCityAI.cpp:4071.
The UnitCombatFreeExperience map key perUnitCombatVal.first is already a UnitCombatTypes. The source attempts GC.getInfo(key).getUnitCombatType(), treating a combat-category key as unit metadata. Pass the key directly to getFavoriteUnitCombatWeight.

Contracts read: baseline CvInfo_Building.h:278 declares DEF_INFO_ENUM_MAP(UnitCombatFreeExperience, UnitCombat, int, char, NonDefaultEnumMap); baseline CvCity.h:98 declares canTrain(UnitCombatTypes) const. Baseline building loop also passes this combat key directly to canTrain. Therefore keep that overload call unchanged. CvCity provides getPersonalityType, so the nearby personality lookup is not a demonstrated declaration issue.

Verification: actual revised preference/conditional contribution lines extracted into a strict C++03 ASan/UBSan fixture using a distinct UnitCombatTypes enum and pair key. 286 key/XP/base-weight combinations checked, plus unavailable-training case. Stub personality records queried key; assertions verify the requested category. Full map macro expansion, complete AI_buildingValue, engine XML/cache/native DLL/game not tested. No full build triggered; partial draft [skip ci].

Existing XANA markers and contribution formula retained. Prior findings preserved; no new assistant branch. Metadata ownership/copy/cache/schema integration remains partial.
