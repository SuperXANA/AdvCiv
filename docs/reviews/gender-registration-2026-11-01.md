# Gender basic-info registration — 2026-11-01

GENDER-20261101-10. Read-only source GenderSpecificDiplomacy `80e6ec595041cf335d5437b7bedea4fcaa61622b`; assistant parent `db3c3e16dfcc892222559ff2b7c28e9d39a5ed40`. Scoped correction `e4591c218bb9d4fa1c7eaabee916b04e8587c9d9` on the existing GenderCounterDraft-ChatGPT branch.

## Defect and repair

CvEnumMacros.h:48 adds Gender to DO_FOR_EACH_SMALL_DYN_INFO_TYPE. The baseline's generated declarations/vector accessors therefore refer to CvGenderInfo. Unlike UnitCombat, Memory, Attitude and other basic-info types, Gender had no alias in the same header and no dedicated class definition in the supplied feature. CvXMLLoadUtilitySet.cpp:638 instantiates LoadGlobalClassInfo for that vector, requiring a complete class. A forward declaration alone cannot be constructed or used by the loader.

At CvEnumMacros.h:168, add `#define CvGenderInfo CvInfoBase` inside new paired XANA date markers, following the adjacent baseline aliases. Supplied CIV4GenderInfos.xml contains only Type and Description for GENDER_MALE and GENDER_FEMALE, matching the base info contract. No gender enumeration values, identity choices, diplomacy rules, XML data or schema are invented. Existing markers and all earlier assistant repairs remain.

## Verification

tests/gender-registration/check.py includes the actual revised macro header and expands the actual global-info forward declarations/vector list and Gender accessor macros. A modeled loader instantiates two records, checks typed/integer accessors against the same records, deletes both and checks lifecycle accounting. Normal and ASan/UBSan runs pass C++03, -fno-exceptions, -Wall -Wextra -Werror -pedantic. Removing only the new alias reproduces an incomplete-type compilation failure.

The enum, CvInfoBase implementation and loader body are stand-ins; this does not execute the Firaxis XML parser, native loader, real localization or all generated enum definitions. The baseline MAKE_INFO_ENUM expansion has a trailing enumerator comma accepted by the native toolchain but diagnosed by the host's pedantic C++03 mode; the fixture uses a minimal GenderTypes declaration to keep this test focused on type registration without editing or suppressing warnings in baseline code.

No DLL build was triggered. This remains a sparse, scoped feature draft with older complete source copies; full validation still requires preparing/reconciling the complete pinned baseline overlay and current workflow. Host checks do not establish MSVC7.1 or DLL success. The previously documented missing external basic-info schema and actual UI/XML/gameplay/new-game save/reload validation remain open. This repair removes one concrete registration obstacle; it does not certify full-feature readiness. No original branch or 1.14 edit, merge, PR or force-push.
