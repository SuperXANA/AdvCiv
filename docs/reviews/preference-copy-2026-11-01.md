# Preference default-copy ownership — 2026-11-01

PREFERENCE-20261101-14. Original LeaderCivilizationDecisionPreferences `aac03388283a5ac316f6a19f6e3754a7435b6511` remains read-only. Reused PreferenceFrameworkDraft-ChatGPT parent `5012475e85a727dd0417bbb1249fe845a3b9d321`. Correction `6e64cbcc973dd775328b610a9cc4b20e948d1b9a`. Prior category-key, repeated-load and ownership-cleanup reports checked before this pass. Fresh inventory: 75 branches, no changed user-owned heads.

## Defect and correction

The three preference info classes own five raw index-map arrays. Their destructors free those arrays, but they had no explicit copy constructors. CvXMLLoadUtility::SetGlobalClassInfo at CvXMLLoadUtilitySet.cpp:1274 clones defaults using new T(*pDefaultClassInfo); CvInfoBase provides a public copy constructor. Implicit derived copying therefore copies the owning pointers. A child's present list invokes SAFE_DELETE_ARRAY on the shared map, invalidating its defaults/siblings; later destruction can free the same allocation twice. Omitted inherited lists also retain shared ownership.

Add explicit copy constructors for CvTechPreferenceInfo, CvEventPreferenceInfo and CvUnitPreferenceInfo, with matching header declarations. Copy base metadata, leader/civilization IDs and record vectors; initialize all destination map pointers NULL; allocate and copy each populated source map using its existing GC info count. Preserve NULL for absent lists. Five maps are independent: Tech, Event, UnitCombat, UnitClass and Unit. This follows the established baseline owning-array copy pattern. Tables must retain the same counts while copying/using these metadata records, as already required by their loader/getter contracts.

No copy assignment is introduced: the real CvInfoBase inherits a noncopyable assignment restriction. No new explicit C++ exception constructs. Ordinary new[] and vector allocation follow baseline conventions; this does not promise recovery from implicit allocation failure. Existing record parsing, index mapping, default identity selection, numeric formulas, list replacement semantics and XANA markers remain. New paired date markers enclose copy declarations/definitions.

## Verification

tests/preference-copy/check.py extracts all three actual class declarations and their implementations from constructors through read. It reuses the prior enclosing-loader fixture's engine/base/enum/XML/record stand-ins and adds copy-ownership tests.

160 sequences cover counts 1–5 and all 32 combinations of populated/NULL maps. They verify copied lookups, independent map addresses, copy-of-copy state, continued access after original destruction, and reload/clear of one copy without changing the other. The retained 960 repeated-load sequences also pass. Strict C++03 -fno-exceptions -Wall -Wextra -Werror -pedantic with ASan/UBSan; leak checking disabled and UBSan halt-on-error. Three independent negative controls remove one class's copy declaration/definition at a time; each fails the map-independence assertion before requiring an unsafe access.

These are scoped actual-owner/list implementations with simplified records and base/XML interfaces. They do not execute real CvInfoBase default merging, the actual record copy implementations, Firaxis XML or engine allocations. No full DLL/MSVC7.1/game result is claimed.

## Integration gate retained

Full DLL overlay remains deferred under the existing missing Event/Unit preference assets and Unit schema gate. No XML profiles/schema or omitted implementation is invented to obtain a build. The copy repair is independently reviewable source work; it does not activate or certify the full preference feature. New-game save/reload, XML/default installation, percentage arithmetic and actual consumers remain future integration verification. Original branches and read-only baseline unchanged. Code and documentation use [skip ci].

## Follow-up correction — 2026-11-02

PREFERENCE-20261102-15 corrects the base initializer in all three new copy constructors. The actual baseline CvInfoBase copy constructor only raises an unimplemented-copy diagnostic and does not copy metadata; the earlier fixture's empty base did not model that contract. Use base_t(), matching baseline default cloning, and read the child's own base metadata through the existing read sequence. The derived scalar/vector/five-map deep copies remain. See preference-base-2026-11-02.md and code 87a7aa044ea0ed52d304a0b3fbac9c15b5137962 for evidence, expanded regression and unchanged full-DLL integration gate.
