# Preference metadata cleanup review — 2026-10-28

Source LeaderCivilizationDecisionPreferences at aac03388283a5ac316f6a19f6e3754a7435b6511.
Isolated code 77e78b5538774f765ff6a0b9f6ad31527a4f63e3, PreferenceFrameworkDraft-ChatGPT.
Original source heads unchanged in this inventory.

## Readiness assessment

Read the XANA-marked metadata declarations/readers, preference data structs,
AI consumers and initialization methods, enum registration and loader calls.
Tech, event and unit preference classes and readers are implemented in the
source. This is not a README-only or absent-class feature and is not placed on
the missing-implementation skip list. Remaining implementation bugs must not be
confused with unspecified gameplay rules. The four existing source skip gates
remain unchanged.

## PREFERENCE-20261028-01 — illegal destructor initializer punctuation

Functions changed:
- CvTechPreferenceInfo::~CvTechPreferenceInfo, CvInfo_Civilization.cpp:1573.
- CvEventPreferenceInfo::~CvEventPreferenceInfo, CvInfo_RandomEvent.cpp:2108.
- CvUnitPreferenceInfo::~CvUnitPreferenceInfo, CvInfo_Unit.cpp:2566.

Each definition ended its signature with a colon immediately before the body.
A destructor cannot have a constructor-style member initializer list.
Removing those three colons permits these definitions to compile. Bodies and
allocation ownership remain unchanged: one map for tech, one for events,
three for unit-combat/unit-class/unit preferences. Existing XANA markers remain.

## Checks

python tests/preference-cleanup/check.py extracts all three actual complete
class declarations and their actual constructors/destructors. Surrounding
CvInfoBase and vector element types are stubs; no XML or AI methods are called.
A test friend matching the real XML utility name initializes the five map
pointers to stand-in allocations. Empty destruction frees nothing; 100 populated
cycles account for 500 array deletions.

Passed g++ -std=c++03 -Wall -Wextra -Werror -pedantic, ASan/UBSan;
UBSAN_OPTIONS=halt_on_error=1, ASAN_OPTIONS=detect_leaks=0.
Restoring original colons causes all three destructors to fail compilation
with only constructors take member initializers / expected identifier errors.
Published diff inspected: precisely three production punctuation changes.

## Limits / next coverage

No full DLL workflow was added or triggered. This is not MSVC 7.1, whole-class
linkage, real XML, engine memory macro, cache or gameplay verification.
Preference lookup/read behavior, repeated loading, copying of owning info
objects and const/type consistency of AI consumers remain unverified.
Earlier broad preference review observations are not presented as new discoveries.
The isolated draft supplies no missing preference rules or XML content.
Original branches and AdvCiv 1.14 remain unchanged/read-only respectively.
