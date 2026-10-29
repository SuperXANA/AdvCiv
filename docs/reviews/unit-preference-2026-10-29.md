# Unit preference typed snapshots — 2026-10-29

Existing PreferenceFrameworkDraft-ChatGPT 6346e4173974a1c0a5854f6d941f3c0cfe29fd46 reused. Original source remains aac03388283a5ac316f6a19f6e3754a7435b6511.
PREFERENCE-20261029-04: AI_unitValue, original CvPlayerAI.cpp:13952–14017, assigns const UnitPreferenceData&, UnitClassPreferenceData& and UnitCombatPreferenceData& results to UnitPreferenceData*. The record types are distinct, not subclasses. Both const loss and class/combat conversions are invalid.

Add a C++03 template copying shared choice fields into two local UnitPreferenceData snapshots. Point const consumer pointers at these local records. Original metadata remains unchanged. Unit ID in snapshots remains NO_UNIT and is not consumed by the choice logic. Existing unit-first, then class only if neither leader nor civilization matched, then combat fallback is preserved; both preferred/not-preferred flags and percentage copied without changing precedence. No fallback-policy redesign.

All supplied DLL files searched; record definitions and accessors actually exist in CvXMLStructs.h/.cpp. Initial suspicion of missing definitions was ruled out by the complete search, not recorded as a skip.

Verification: actual three record declarations/accessors and new conversion helper compiled under strict C++03 with ASan/UBSan. Forty-eight configurations (three types, four flag combinations, four percentages) checked, including unchanged NO_UNIT snapshot ID. Full AI_unitValue/lookup branches are not compiled in this fixture; XML/cache/whole-feature/MSVC7.1/DLL/game not verified. Partial draft [skip ci].

Existing first-impression run 40894673380 for c4a2140493fb083bbde5af52bfb80caaf01af2ca checked: Release123520407304 and Debug123520407159 both remain queued, no compiler result. No duplicate triggered. Overall review is not blocked; source scopes remain.
