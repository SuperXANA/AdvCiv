# Preference record XML cursor ownership — 2026-10-30

PREFERENCE-20261030-05. Read-only source LeaderCivilizationDecisionPreferences aac03388283a5ac316f6a19f6e3754a7435b6511; reused PreferenceFrameworkDraft-ChatGPT parent 166d6a47995801991f147b6f7154eda1b241892b. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against the latest global ledger at bfcc3e0c5dd41a9888397f4256f4242b425fb949.

## Committed correction

All five CvXMLStructs.cpp record readers descended one level with SetToChild before requesting fields by name, then moved back with SetToParent. The callers already enter each record before invoking read. Thus the extra descent positions the cursor on the first field (e.g. TechType), and GetChildXmlValByName/SetInfoIDFromChildXmlVal search for fields underneath a leaf. Required IDs remain absent/default, causing callers to skip the records.

Read named fields directly from the current record and retain the cursor there. Removed only the redundant descent/parent movement and associated conditional nesting. Existing return-true behavior, tag names, field types, defaults supplied by XML utilities and preference scoring are unchanged. Original XANA marker blocks and prior assistant fixes are retained.

| Function | Revised CvXMLStructs.cpp line |
| --- | ---: |
| TechPreferenceData::read | 27 |
| EventPreferenceData::read | 60 |
| UnitCombatPreferenceData::read | 93 |
| UnitClassPreferenceData::read | 123 |
| UnitPreferenceData::read | 153 |

Evidence read: complete CvXMLStructs.h/.cpp; CvTechPreferenceInfo::read in CvInfo_Civilization.cpp:1600–1650; CvEventPreferenceInfo::read in CvInfo_RandomEvent.cpp:2135–2179; all three list loops in CvUnitPreferenceInfo::read, CvInfo_Unit.cpp:2619 onward. Each caller enters the list, then a record, invokes read, then advances with NextSibling. Actual pinned baseline CvXMLLoadUtilityGet.cpp:683 onward shows named-child lookup descends to the named child and restores its parent itself.

The supplied CIV4TechPreferenceInfos.xml has three TechPreference records with direct TechType/modifier/preferred/not-preferred children. Its actual rows are ROCKETRY/33/false/false, COMPUTERS/50/false/false and MUSIC/0/true/false. Python ElementTree confirmed that direct-child structure. The technology and event schemas also describe fields directly under records; no wrapper tag or missing schema was invented for unit preferences.

## Verification

tests/preference-cursor/check.cpp embeds all actual preference struct declarations and complete revised implementation (only include/pragma lines omitted for embedding), with reduced node/cursor/lookup/XML interfaces.

Strict C++03 -Wall -Wextra -Werror -pedantic, ASan and UBSan passed 2,880 record configurations: five types, all 16 field-presence masks, three modifiers, four flag combinations and known/NONE/unknown ID values. Every case checks cursor identity and a second empty-record read on the same object to check utility-default behavior. Three separately reconstructed rows using the exact supplied technology XML names/values also pass; numeric IDs are stub lookup IDs, not actual engine IDs.

Restoring the original implementation fails the technology-ID assertion when a known ID field is present. Leak detection disabled as unsupported; no leak claim.

This tests the interface and cursor contract, not the real Firaxis XML parser, actual CvXMLLoadUtility implementation, full enclosing preference-info loaders/index-map insertion, engine registration/default inheritance, MSVC 7.1, DLL or gameplay. The fixture's XML helpers preserve the observed named-child cursor contract but are stubs. Caller list cleanup, empty/repeated reads, invalid ID range handling and complete native integration remain separate scopes.

This partial integration draft uses [skip ci]. No native build triggered or claimed; no original branch changed.
