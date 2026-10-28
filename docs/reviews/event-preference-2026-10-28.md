# Event preference consumer repair — 2026-10-28

Source aac03388283a5ac316f6a19f6e3754a7435b6511; reused
PreferenceFrameworkDraft-ChatGPT at a290ad622d68cb48c9b5c5562a6dcc60a1fc6d89. Commit uses [skip ci].
No original feature source changed.

## PREFERENCE-20261028-02

CvPlayerAI::AI_eventValue (CvPlayerAI.cpp):
- Lines 23514–23515: two EventPreferenceData pointers now point to const.
  CvEventPreferenceInfo::getEventPreference returns const EventPreferenceData&;
  taking its address into a mutable pointer discarded const and failed compilation.
  The consumer only reads the data, so preserving const is sufficient.
- Lines 24072 and 24074: leader multiplier now uses getEventValueModifierPercent,
  matching the actual EventPreferenceData declaration/definition and the
  civilization path. The old getAIWeightModifierPercent accessor did not exist.

No scoring policy changes: leader then civilization preferred/not-preferred
ordering remains; nonzero percentages multiply sequentially; zero still skips
multiplication. This does not redesign a zero-percent value to mean zero score.

## Checks

python tests/event-preference/check.py extracts the actual two marked blocks,
actual EventPreferenceData declaration and actual three read-only accessor
definitions. These execute in a fixture function with engine metadata lookups
stubbed. Passed strict C++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan;
ASAN_OPTIONS=detect_leaks=0; UBSAN_OPTIONS=halt_on_error=1.

1024 combinations cover absent/present leader/civilization preferences, four
boolean flag combinations per side and percentages 0/50/100/150. Missing map
entries are checked too. An original-reference negative control fails with
two const conversions and nonexistent accessor errors. Published diff inspected.

The intervening event evaluation body, RNG, real metadata loading, large-value
overflow, recursive evaluation and full DLL/MSVC/gameplay are not validated.
No build workflow added or triggered. Original branch and XANA markers retained.

## Changed workflow head reconciliation

dll-build e4e33b487d5f5805361f8938cf1491829f5ed923 changes only checkout and
upload-artifact pins from the previously tested workflow. The actual pinned
[action.yml for checkout](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/action.yml)
and [action.yml for upload](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/action.yml)
were read: both declare node24; upload retains name/path/if-no-files-found and
defaults archive to true. No issue established from this metadata check.
Preserve these newer user edits. No repeated DLL run was triggered merely for
pin reconciliation. Prior run 40783621740 verifies its exact old pins/commit,
not this new source head. No claim that the runtime deprecation warning is
confirmed removed until the new pins execute.
