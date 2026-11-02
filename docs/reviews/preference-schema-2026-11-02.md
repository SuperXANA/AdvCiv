# Preference schema integration — 2026-11-02

PREFERENCE-20261102-16. Reviewed LeaderCivilizationDecisionPreferences at c245f5c3d205437ca6db26c9b74d5e6f121de1f6, including new commits bc95f4707cd38954cea36fec3447e9c1d38ea295 and c245f5c3d205437ca6db26c9b74d5e6f121de1f6. Previous reviewed source aac03388283a5ac316f6a19f6e3754a7435b6511. Reused PreferenceFrameworkDraft-ChatGPT parent 61c5ae3119e06b97098e7ccd3c629f06b61b5b39. Read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6. The 75-branch inventory prioritized the new source schema addition; no user-owned branch was modified.

## Incorporated source and concrete corrections

Schema commit 72543d4e94d17803dc1eb31be3700b7e492cecae incorporates the supplied Unit schema and scoped corrections. Follow-up 62d2f9499ae53a2741e80798070fb8c9c60c954e makes the structural checker validate the authored technology profiles against declared requirements without imposing a new exclusive-owner policy.

The source adds only XML/Units/CIV4UnitSchema.xml; no C++ delta occurs. Prior assistant C++ fixes, including independent preference-map ownership and base default construction, remain unchanged. The supplied Unit schema's non-feature content is retained exactly; corrections stay inside its existing paired XANA 11-02-2026 block.

| Contract | Source issue | Corrected schema |
| --- | --- | --- |
| Loader root | Civ4UnitPerferenceInfos does not match the actual loader's Civ4UnitPreferenceInfos | Exact root spelling, Unit schema:747 |
| Owner fields | Leader/Civilization do not match CvUnitPreferenceInfo::read:2660–2661 | LeaderType/CivilizationType, Unit schema:703–704 and 738–739 |
| Record key | Unit is referenced without any ElementType declaration and differs from UnitPreferenceData::read:196 | Declared UnitType and matching record child, Unit schema:705 and 728 |
| Implemented fallback lists | Schema exposes only UnitPreferences; C++ also reads UnitCombatPreferences and UnitClassPreferences | Matching record/list models, Unit schema:709–743 |
| Owner cardinality | All three schemas require both owner identities; supplied technology examples each omit one | Optional owner fields in Tech/Event/Unit preference-info models |

The added combat/class record models are direct schema counterparts of the existing C++ methods, not new gameplay mechanics: each has its existing category key, iUnitValueModifierPercent and optional bPreferredChoice/bNotPreferredChoice fields. All three unit lists are optional, matching the already implemented omitted-list handling. Existing record order, matching precedence, percentage and zero-value policy are unchanged. Both owner identities can still be supplied; no exclusive-owner rule was introduced.

The original source Tech/Event schemas also retain the older Perference root spelling. The assistant branch already corrected those root names before this pass; those corrections are preserved and not presented as new work. This pass changes only their two owner cardinalities each.

## Verification

Run python tests/preference-schema/check.py. The checker parses all three schema files as XML, rejects duplicate ElementType declarations and unresolved element references, and compares roots/paths against actual LoadGlobalClassInfo calls. It compares all five record field lists against the actual CvXMLStructs.cpp read methods and checks all three unit lists against CvUnitPreferenceInfo::read. The two supplied technology profiles satisfy the revised owner requirements.

Checks pass with zero duplicate declarations and zero unresolved element references. Seven negative controls independently restore each of the three misspelled roots, the wrong unit owner field, undefined Unit key, missing unit-class list and a required technology owner field. Each is detected.

This is structural XML/source-contract validation. Python ElementTree is not an XDR validator; no actual Firaxis/MSXML loader, type registry, custom roster, embedded engine or gameplay was executed. No DLL build was triggered or claimed: production C++ is unchanged and both code commits use [skip ci].

## Gate update

The missing Unit schema is now supplied in the user source and incorporated with corrections on the assistant branch. That portion of the old gate is resolved.

CIV4EventPreferenceInfos.xml and CIV4UnitPreferenceInfos.xml are still absent from the reviewed source tree. No placeholder profiles, intended leader/civilization choices or weights were invented. The remaining full-feature integration gate now names those data files rather than continuing to claim the Unit schema is missing.

The branch's XML/ directories remain its existing source-staging layout. Actual installation under Assets/XML with the intended authored data, XDR parsing, default inheritance and installed-game behavior remain unverified. Schema availability and a native DLL compiler result are separate forms of evidence. Preserve the current C++03/MSVC7.1 source corrections; use the complete pinned baseline and actual dll-build workflow when a meaningful full-feature DLL validation is next warranted.
