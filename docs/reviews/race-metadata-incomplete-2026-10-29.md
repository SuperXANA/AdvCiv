# Race leader metadata implementation boundary — 2026-10-29

Original FFHRaceTypes a50b62ccd1ec72672c3b8b4814ad03230088ea18 unchanged. Reviewed existing RaceDemographicsDraft-ChatGPT2151dc14537e057b35d218be161c6ef0ffec9ff7, retaining prior weighted-selection/getter fixes.
RACE-20261029-05 records missing implementation, not a new fabricated metadata design.

CvInfo_Civilization.h:218–221 inline leader getters reference m_eFavoriteRace, m_eHatedRace, m_eFavoriteRaceClass, m_eHatedRaceClass. These members are not declared in the actual header; leader XANA fields353–357 contain only m_eDefaultRace and four array pointers. CvInfo_Civilization.cpp:1087–1094 XML loader also references these missing fields.

CvLeaderHeadInfo::getFavoriteRaceAttitudeChange, getFavoriteRaceClassAttitudeChange, getHatedRaceAttitudeChange, getHatedRaceClassAttitudeChange are declared at header244–247 but have no definitions in any of the23 supplied DLL files (all fetched and searched for qualified definitions). The four pointers at354–357 appear in XML load1095–1098 but not constructor/destructor lifecycle. No ownership/default/range/copy/cache policy certified.

Civilization race priority storage and CvRaceInfo are separate from this incomplete leader integration: prior scoped implementation/tests preserved, not discarded or attributed to native success.

Disposition per missing-implementation rule: skip unchanged original head until new user source work supplies missing data/integration. Do not complete the feature merely to obtain a DLL result; no code patch invented. Native build not triggered. Existing assistant branch reused for docs only [skip ci]. Baseline remains read-only.

Verification: actual header/implementation and all supplied DLL files searched. No new runtime test or MSVC/DLL/game result; no claim that these are the only remaining integration issues. Existing draft previously reviewed only selected methods. Scope: leader metadata plus constructor/read/write/destructor references.
