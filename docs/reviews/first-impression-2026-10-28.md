# First-impression debug loader repair — 2026-10-28

Source: FirstImpressionDiplomacyModifiers at cc764ad80e89f751f809998a61a23225254109f2.
Refinement: FirstImpressionDraft-ChatGPT, code 971d63a53deb940f7af13ce6bbe408c8559fb1b2.

## FIRST-20261028-01

CvLeaderHeadInfo::readPass2 begins at CvInfo_Civilization.cpp:1097.
Original lines 1101–1110 contained a FASSERT_ENABLE-only block whose
if (!isDefaultsType()) opening brace was never closed. The following function
brace therefore closed that conditional instead, leaving the function open
when assertions were enabled. The original compiled in the fixture with that
macro absent, but failed compilation with it defined.

The loop asserted value >= 0 || value <= 0, true for every int. It supplied
no valid constraint on the signed modifier. The repair removes this entire
malformed, ineffective debug block. The existing SetVariableListTagPair call
at line 1099 and unconditional true return remain; no XML mapping, default,
leader-personality identity or diplomacy rule changes.

## Verification and limits

python tests/first-impression/check.py extracts the actual method and compiles
it under C++03, -Wall -Wextra -Werror -pedantic, ASan/UBSan, once with
FASSERT_ENABLE and once without. Both passed. A stub verifies one loader call,
the literal tag FirstImpressionChanges, dynamic count 149 and preservation of
149 negative/zero/positive values. Engine XML loading is stubbed, not validated.
ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1.

Negative control with original source passed the first configuration and failed
the FASSERT_ENABLE compilation with an unmatched function brace. This confirms
a debug-configuration-specific defect, not an all-configurations failure.

No DLL workflow was added or triggered; no MSVC 7.1, whole-class, XML/schema,
cache ABI or gameplay result is claimed. Other earlier partial observations
remain outside this repair and are not re-reported as new findings.
The four missing-implementation source skip gates remain unchanged. Original
branches and XANA 05-31-2025 markers are preserved. AdvCiv 1.14 remains read-only.
