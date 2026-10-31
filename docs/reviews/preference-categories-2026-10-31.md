# Preference record key categories — 2026-10-31

PREFERENCE-20261031-13. Read-only original LeaderCivilizationDecisionPreferences aac03388283a5ac316f6a19f6e3754a7435b6511. Existing PreferenceFrameworkDraft-ChatGPT reused from 4d183d19b36c374f1fd3bf4830ca12c69b7b2a1f after consulting the current global ledger 45dabe719c0fea87478ac99df4381e4d7c7f0785 and prior bounds/cursor/consumer reports. Fresh 75-branch inventory has no changed original source heads; the only inventory difference is the last expiry report publication. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

[Scoped source and fixture correction d103db3cc9e2ddb9f2b997364bfd8c899c04be33](https://github.com/SuperXANA/AdvCiv/commit/d103db3cc9e2ddb9f2b997364bfd8c899c04be33).

## Defect

The five record readers in CvXMLStructs.cpp store IDs as int and delegate to SetInfoIDFromChildXmlVal. The actual baseline int path uses the global type registry. CvGlobals::getInfoTypeForString returns an index only; it does not encode the info category. Technology ID 1, event ID 1 and unit ID 1 can coexist under different string keys.

The earlier enclosing-loader range guards correctly prevent out-of-bounds writes, but cannot reject a foreign key whose numeric ID is within the destination table's range. For example, an event name resolving to index 1 in a TechPreferenceData record would select technology 1 and apply its percentage/choice flags to the wrong technology. The same issue affects Event, UnitCombat, UnitClass and Unit records. This correction completes that specifically deferred category-validation scope rather than repeating the range finding.

## Committed correction

New internal readPreferenceInfoID<EnumType>, CvGameCoreDLL/CvXMLStructs.cpp:13:
1. Invalidate the destination ID to -1 before parsing, including when a record object is reused.
2. Read the exact XML key string using the baseline CvString reference overload.
3. Resolve it through the existing global registry. Missing/unknown/NONE/negative IDs return false.
4. Reject candidates outside the requested info count before any typed metadata lookup.
5. Compare the key with getType() from the requested enum category's table entry. A mismatch or NULL canonical type asserts and returns false, leaving the destination at -1.
6. Publish the ID only after all checks succeed.

The comparison is exact and case-sensitive, matching the baseline std::string-keyed hash_map lookup. No prefix heuristic, alias registry, fallback preference or new schema convention is introduced. Existing enclosing loaders already skip -1, so even callers that ignore read's bool result do not append the invalid record or write its lookup slot. Additional scalar fields are read only for accepted records. Valid scalar values/choice flags and enclosing duplicate/order behavior are unchanged.

| Actual record reader | Key tag | Expected category | Revised line |
| --- | --- | --- | ---: |
| TechPreferenceData::read | TechType | TechTypes | 63 |
| EventPreferenceData::read | Event | EventTypes | 97 |
| UnitCombatPreferenceData::read | UnitCombatType | UnitCombatTypes | 131 |
| UnitClassPreferenceData::read | UnitClassType | UnitClassTypes | 162 |
| UnitPreferenceData::read | UnitType | UnitTypes | 193 |

Explicit CvInfo_Tech, CvInfo_RandomEvent and CvInfo_Unit includes provide the complete metadata classes for getType; cstring supplies std::strcmp. Record headers, field types/layouts and public signatures remain unchanged. All original and parent XANA marker lines remain in order. The new helper has dated markers. No C++ exception syntax was added.

## Verification

Run python3 tests/preference-category/check.py from repository root.

The fixture compiles the complete actual record declarations, full revised implementation and helper under strict C++03, -fno-exceptions, -Wall -Wextra -Werror -pedantic, ASan and UBSan. GC and XML interfaces are stand-ins, with separate typed tables and one shared string-to-index registry mirroring the relevant baseline contract.

1,195 cases pass across all five categories and independent table sizes 0–5. Inputs include valid canonical keys, all foreign categories with overlapping in-range indexes, absent/unknown/NONE/empty/lowercase keys, synthetic negative and INT_MAX/out-of-range registry values, NULL canonical metadata and reuse of a populated record. Checks cover bool result, invalidated IDs, preserved valid scalar/choice values, skipped scalar reads on rejection, modeled cursor identity and absence of out-of-bounds metadata calls.

Five independent negative controls restore the old untyped read for one record class at a time. Each negative executable runs only foreign keys whose IDs are simultaneously in range in both categories; all five fail. This isolates the category collision from missing-key, zero-table or ordinary range errors.

Engine tables, XML parser/cursor internals and enum ABI are modeled. Real parser execution, enclosing loader execution with these record definitions, owning-info/default/cache lifecycles, MSVC7.1 and full DLL/game validation are not claimed. The separate prior enclosing range fixtures remain historical evidence; their result count is not added to this pass. LeakSanitizer is disabled; no leak-detector result is claimed.

## Build disposition and remaining work

No DLL build was triggered. The previously recorded exact original head aac03388283a5ac316f6a19f6e3754a7435b6511 still lacks the Event/Unit preference XML data files and Unit preference schema required by its loaders. This scoped record correction does not supply invented profiles or bypass that integration gate. Current dll-build f77f8a67cd17fdfa9d1c3f443d49005cee04421e was read; source and report publications use [skip ci].

Next eligible scopes: owning-info copying/default inheritance/cache, actual category-aware parser integration, save reconstruction and percentage arithmetic. Full overlay preparation remains deferred until the missing user-authored assets/schema details are supplied. Original branches and 1.14 were not edited; no PR, merge or branch deletion occurred.

## Coverage rotation note

GenderSpecificDiplomacy source 80e6ec595041cf335d5437b7bedea4fcaa61622b and current assistant db3c3e16dfcc892222559ff2b7c28e9d39a5ed40 were inspected without edits. Its README explicitly describes manual merging of tagged DLL/XML fragments, so the root XML directory alone was not classified as an installation defect. CIV4GenderInfos.xml references CIV4BasicInfoSchema.xml, which is absent from both supplied feature and pinned repository baseline and therefore depends on inherited game assets. Actual schema/runtime compatibility cannot be certified from this repository snapshot. No guessed replacement game schema or extra DLL build was introduced, and no new whole-branch skip was asserted.
