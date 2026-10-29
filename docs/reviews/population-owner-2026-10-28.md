# City population owner context — 2026-10-28

Finding POPULATION-20261028-01.
Source CityPopulationTrait at dd39c040ee3a25fc8463ad4c484b72bd5f0d8ab3; baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6 read only.

Actual source read: all XANA blocks in CvCity.cpp, CvPlayer.cpp, CvPlayer.h, CvInfo_Civilization.cpp and .h, plus CvCity.h and corresponding baseline population helper.

Completed changes:
- CvCity::initialPopulation, originally CvCity.cpp:13145–13153: static helper incorrectly accessed city instance methods getCivilization/getOwner. Accept PlayerTypes owner explicitly and obtain civilization/trait totals from that player.
- CvCity.h:438: owner parameter defaults to NO_PLAYER. No-owner calls retain baseline initial-plus-era population; owner-aware callers include the source's existing civilization and trait bonuses.
- CvCity::init, line 236: pass actual city owner.
- Static calculateDistanceMaintenanceTimes100, calculateNumCitiesMaintenanceTimes100 and calculateColonyMaintenanceTimes100 (original lines 13160,13232,13277): pass projected owner when population was omitted.
- CvPlayer::getSingleCivicUpkeep, original line 10433: pass getID() for projected additional cities.
No formulas for bonus size or current city population changes were introduced. XANA markers preserved.

Verification: extracted actual revised helper compiled as static under strict C++03 (-Wall -Wextra -Werror -pedantic), ASan and UBSan; 32 combinations checked two distinct players plus no-owner baseline behavior (96 assertions). Metadata/player/global interfaces were stubs. No full city initialization, maintenance/upkeep function execution, XML/cache/save round trip, native MSVC 7.1 or DLL build is claimed. All known call sites in the supplied changed files were inspected.

Incomplete source integration: both new m_bExtraPopulation metadata flags are initialized false but have no XML load calls in the supplied CvInfo_Civilization.cpp; the supplied player code only resets and changes m_iExtraPopulation, with no explicit serialization field. These are remaining integration questions, not functionality certified by this draft. Do not fabricate XML/schema/save policy to force a build. Naming/type and XML/cache/save review remain queued; CI skipped for this partial draft.

Tests: tests/population-owner/check.cpp.
