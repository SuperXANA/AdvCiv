# GenderSpecificDiplomacy: counter-only draft

Reviewed feature head: `80e6ec595041cf335d5437b7bedea4fcaa61622b`.
Baseline reference: read-only 1.14 at
`5970334b64a875b5cdb370c94fc9a98db4eacda6`.
This is a scoped source proposal on an isolated branch, not a complete feature
overlay or install-ready DLL.

Published draft code: `96f7f865a9319903e317dfe596870d622f2d85fc` on
GenderCounterDraft-ChatGPT. The subsequent coverage update changes documentation
only. No workflow or native build was added.

## Findings implemented in this draft

**GENDER-20261027-01 — cross-wired history storage.**
Both gender counter mutators assign m_aiHateReligionCounter instead of their
respective gender arrays. Favorite-gender decay reads AI_getHateCivicCounter,
then writes that unrelated value into favorite-gender history. Thus fixing
only the syntax would leave the intended histories unchanged during accrual
and would couple decay to a separate civic history.

The refinement changes each mutator to its corresponding gender array and
changes favorite decay to AI_getFavoriteGenderCounter. For independent
histories of favorite=10 and hate=20, a 0.9 decay produces 9 and 18, regardless
of any civic/religion history. Matching favorite or hated identity increments
only its own history, preserving the existing update conditions and random
counter-change call sites.

**GENDER-20261027-02 — counter declarations do not match their implementation.**
The header repeats favorite-counter declarations instead of declaring hated
counter accessors. Its marked storage declares civic/religion pointer names
instead of the gender pointers allocated by the constructor. The favorite
mutator is spelled oid and the hated mutator calls a misspelled assertion
getter. The draft fixes the declarations, fields and method definitions.

The six scoped counter methods also check player bounds before access.
Setters prevent negative history, and mutators check bounds before arithmetic,
including INT_MIN decrements and increments at INT_MAX. Decrements floor at zero;
overflowing increments saturate at INT_MAX. A negative old value is normalized
before arithmetic. Existing debug index assertions remain alongside Release
guards. This documents the nonnegative counter invariant rather than allowing
signed overflow or a negative running history.

Original source:
[mutators](https://github.com/SuperXANA/AdvCiv/blob/80e6ec595041cf335d5437b7bedea4fcaa61622b/CvGameCoreDLL/CvPlayerAI.cpp#L18709),
[decay](https://github.com/SuperXANA/AdvCiv/blob/80e6ec595041cf335d5437b7bedea4fcaa61622b/CvGameCoreDLL/CvPlayerAI.cpp#L19527),
[declarations](https://github.com/SuperXANA/AdvCiv/blob/80e6ec595041cf335d5437b7bedea4fcaa61622b/CvGameCoreDLL/CvPlayerAI.h#L516),
[storage](https://github.com/SuperXANA/AdvCiv/blob/80e6ec595041cf335d5437b7bedea4fcaa61622b/CvGameCoreDLL/CvPlayerAI.h#L823).

**GENDER-20261027-03 — counter configuration has a malformed scalar and schema name.**
The marked LEADER_DEFAULTS divisor is written as -10-, which is not an integer.
The schema declares iHateGenderAttitudeLimit while its child reference and the
loader use iHateGenderAttitudeChangeLimit. The draft removes the trailing dash
from the negative divisor and aligns the definition with the existing reader.
The source's other values and leader roster remain intact. Structural checks
parse all supplied gender scalar fields; they are not Civ4 XML validation.

## Verification and limits

`python3 tests/gender-counters/check.py` compiles the actual six revised
methods, their declarations and the actual gender-history update block under
strict C++03 with warnings as errors. It checks independent accrual and decay,
unrelated history sentinels, invalid indices, negative assignments, signed
integer extrema, overflow saturation and untouched player slots.
The game objects and decay arithmetic are stubs. ASan/UBSan passed with
halt-on-error and `ASAN_OPTIONS=detect_leaks=0`; LeakSanitizer is unavailable
under this host's ptrace environment.

**No DLL build was triggered.** The feature still has compilation/integration
work outside these methods, including identity/info registration, attitude and
paranoia logic, XML/help bindings and save/load handling. This draft changes no
stream layout or stream version and makes no save-compatibility claim.
The original feature's save path must be reviewed and versioned before use.
No game, real save, multiplayer session or MSVC DLL validation was performed.
The focused checks must not be treated as any of those.

The draft descends from the selected sparse source branch and changes only
CvPlayerAI.cpp/.h, the two scalar/schema corrections, and review/test documentation.
It preserves its other source
and data, including the original XANA boundaries. It is not yet a complete
pinned-1.14 build overlay; before any future DLL validation, retain 1.14's
base-only files, reconcile older unmarked upstream copies, copy the current
dll-build workflow and follow the exact triggered commit to completion.
No original branch or the 1.14 snapshot was modified.

## Coverage and next work

The first pass read the XANA blocks in all fourteen supplied DLL files, the
gender info file, civilization schema and marked leader-data fields. It does
not establish whole-feature correctness. Only the counter subsystem is refined
here; keep this feature marked partial, with native validation outstanding.
UniqueCivicsReligions was inventoried but its code has not been reviewed in
this pass.

The accompanying coverage JSON inventories all observed branch heads, separates
completed native refinements from source-only drafts and pending review, and
records exact tested code commits rather than attributing a derivative build
result to the original branch head. Initial coverage is not complete, so the
stop gate has not been reached. After coverage completes, outstanding failed
or unverified builds remain work; a successful isolated refinement alone must
not be reported as a build of the unchanged original branch.
