# Organization and religion-weight enum interfaces — 2026-10-31

ORGLOAD-20261031-06/07. Original UniqueCivicsReligions `d0fc7c0f93320e112903416c17bb2a2030819d60`; reused CivicScrollDraft-ChatGPT parent `98d3214ad7489a6de53b1572d010820e3734111d`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh inventory of 75 branches has no original-head changes against global ledger 80c72f26cd336bc8557669d6027c3ed4244dda94. Prior organization pass-3/default/read reports were checked; their integer-alias fixture limit is addressed here.

[Correction and fixture 62d4e049a45471267ea6f356d9695f16dbb452ed](https://github.com/SuperXANA/AdvCiv/commit/62d4e049a45471267ea6f356d9695f16dbb452ed).

## Completed corrections

ORGLOAD-20261031-06 — CvInfo_Organization.h:
- CvOrganizationInfo::getPrereqCivilization, line 25: explicitly static_cast stored m_iPrereqCivilization to CivilizationTypes.
- CvOrganizationInfo::getPrereqLeader, line 26: cast m_iPrereqLeader to LeaderHeadTypes.
- CvReligionInfo::getHybridOrganizationType, line 69, and CvCorporationInfo::getHybridOrganizationType, line 126: cast m_iHybridOrganization to HybridOrganizationTypes.

C++03 does not implicitly convert arbitrary int values to an enum return type. The fields remain ints, as expected by current late ID-resolution code, and the API return types remain the declared enums. Only explicit conversions are added; no class layout, ID lookup, fallback or range policy changes. The actual feature CvEnumMacros.h registers HybridOrganization, and its generator emits Name##Types.

ORGLOAD-20261031-07 — CvInfo_Civilization.h:234–236 and CvInfo_Civilization.cpp:700,705,713:
Replace nonexistent ReligonTypes with ReligionTypes in declarations/definitions of CvLeaderHeadInfo::getReligionWeightModifier, changeReligionWeightModifier and setReligionWeightModifier. The pinned baseline enum macro registers Religion and generates ReligionTypes; surrounding source already uses that spelling. No method body or weight arithmetic changes.

Original XANA markers and earlier refinements are preserved. No metadata, schema, enum category, game mechanics or independent feature implementation is invented.

## Verification

Run `python tests/organization-enums/check.py`. The complete actual organization header is compiled against distinct enum types, not the int aliases of earlier scoped fixtures. Stub base/string/interface types and organization constructors/destructors support the test; real constructor order/ownership is not certified. It also extracts all three actual religion-weight declarations and complete definitions into a reduced leader shell with a real int-array backing store.

Passed strict C++03/ASan/UBSan with no warning suppression:
- 15 organization getter cases: nine civilization/leader value pairs and three hybrid IDs in each derived class. Member-pointer assignments also require the exact distinct enum return types.
- 20 religion-weight cases: two religion IDs, three starting values, three changes, adjacent-slot preservation, and two null-map getter defaults. No null-map mutation or overflow behavior claim.

Negative controls independently remove the explicit casts or restore the typo. The original getter bodies produce exactly four int-to-enum conversion compiler errors; original religion-weight signatures produce undeclared ReligonTypes errors. Earlier tests using int aliases could not establish this enum conversion property.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1. No leak claim.

## Remaining scope

The enum declarations in this fixture are stand-ins with distinct types and representable test IDs; actual enum registry/ABI/category validation is not established. Full metadata loaders/default/copy/cache behavior, repeat staging, real religion-weight array allocation/mutation bounds, pass-3 failure propagation, engine bindings and hybrid gameplay remain unverified. Explicit casts do not validate that stored numeric IDs belong to the requested category.

No MSVC7.1/full DLL/game result. Partial code/report publication uses [skip ci]; no build workflow triggered. Original branches and baseline remain untouched.
