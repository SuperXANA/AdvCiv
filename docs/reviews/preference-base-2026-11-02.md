# Preference base initialization during default cloning — 2026-11-02

PREFERENCE-20261102-15. Source LeaderCivilizationDecisionPreferences remains read-only at aac03388283a5ac316f6a19f6e3754a7435b6511. Reused PreferenceFrameworkDraft-ChatGPT parent 5518502d36e4a180b1df6905ac91fffce42a4aaf. Corrected code 87a7aa044ea0ed52d304a0b3fbac9c15b5137962. Pinned read-only 1.14 baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory found no changed original heads. Prior ownership, repeated-load, cursor and record-copy reports were checked before this bounded follow-up.

## Defect and correction

The previous assistant copy-constructor repair explicitly initialized base_t(kOther) in all three preference info classes. Actual baseline CvInfo_Base.cpp:9–12 shows that CvInfoBase's copy constructor is deliberately unimplemented: its only statement is FErrorMsg("Copy-ctor not implemented"). It copies no base fields, and unlike the default constructor at line 6, does not initialize m_bGraphicalOnly. Calling it while cloning defaults therefore raises a Debug diagnostic; it does not perform the base metadata copy described by the previous report. The former fixture used an empty, implicitly copyable base and could not detect this mismatch.

Actual SetGlobalClassInfo at CvXMLLoadUtilitySet.cpp:1272–1276 constructs a default clone and immediately calls its read method. That method calls base_t::read before reading derived data. CvInfoBase::read at CvInfo_Base.cpp:148–164 explicitly populates the child's graphical flag and metadata strings from XML. Baseline CvLeaderHeadInfo's copy constructor at CvInfo_Civilization.cpp:517–522 intentionally default-constructs the base and copies only derived fields; its comment specifically excludes the base class from its memory copy.

Follow that baseline contract: change the three initializers from base_t(kOther) to base_t(). Keep all derived leader/civilization scalars, record vectors and five independent owning-map copies from the earlier fix. This avoids the unsupported base-copy diagnostic and initializes base state while the child's own metadata is read in the established loader sequence.

| Constructor | Corrected initializer |
| --- | ---: |
| CvTechPreferenceInfo, CvInfo_Civilization.cpp | 1575 |
| CvEventPreferenceInfo, CvInfo_RandomEvent.cpp | 2110 |
| CvUnitPreferenceInfo, CvInfo_Unit.cpp | 2568 |

Production changes are exactly three initializer lines with dated annotations. User XANA markers and the paired earlier assistant markers remain. No baseline file, default-list replacement rule, derived value, record read, index-map allocation, weight formula, XML asset or explicit exception construct changed.

## Verification

The existing tests/preference-copy/check.py now reproduces the actual pinned baseline default and unsupported-copy constructor bodies. The unused copy-parameter name is omitted only for the strict host unused-parameter warning. A diagnostic counter stands in for the engine FErrorMsg dialog; assertions require zero unsupported base copies after each child and copy-of-copy construction, and verify the normally initialized graphical flag.

The complete actual three preference class declarations and implementations are still extracted from the production files. Strict C++03 -fno-exceptions -Wall -Wextra -Werror -pedantic runs pass both normally and under ASan/UBSan: 160 ownership/copy-of-copy sequences and 960 repeated-load sequences. Three independent negative controls restore one previous base_t(kOther) initializer at a time; each fails the unsupportedBaseCopies == 0 assertion. The five-map ownership checks remain active. Leak detection disabled; no leak claim.

This executes the two small baseline constructor bodies and actual preference owners/loaders against reduced globals, record readers and XML/base-read interfaces. It does not compile all CvInfoBase fields/methods, execute the real Firaxis parser/default registration loop, or validate engine allocation/debug dialogs, MSVC7.1, DLL loading or gameplay.

## Build and remaining integration gate

No DLL workflow was triggered, and no full DLL result is claimed. The existing exact-head missing Event/Unit preference assets and Unit schema gate remains. No placeholder profiles, schema or feature implementation were invented for validation. Code and documentation commits use [skip ci].

Actual complete XML/default loading, base metadata population, player reconstruction and preference arithmetic still need their respective integration evidence. This closes the concrete unsupported-base-constructor path in the scoped ownership repair; it does not certify the whole preference feature. Original user branches and 1.14 remain unchanged.
