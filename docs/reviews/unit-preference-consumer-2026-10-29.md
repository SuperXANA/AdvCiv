# Unit preference consumer coverage — 2026-10-29

Reviewed source 4ae2aca39f3d9400d2fa56713bfc2291ed6da1a7. No new production defect found in the scoped selection block.
Extended helper-only checks to the actual complete AI_unitValue XANA lookup/fallback/choice block, retaining actual three data declarations/accessors and snapshot helper. Stub metadata returns distinct record types; lookups and unit/global interfaces are controlled stand-ins.

Strict C++03 (-Wall -Wextra -Werror -pedantic), ASan/UBSan passed 4,096 configurations: 64 unit/class/combat presence combinations across leader/civilization; 16 combinations of preferred/not-preferred flags; four leader/civilization preference selection-presence states. Verified exact original shared-level fallback semantics: class is considered only if neither side has a unit entry; combat only if neither side has a class entry. Preferred flag retains precedence when both flags are set; leader scoring precedes civilization scoring. Not a redesign or engine integration proof.

Tests/unit-preference/consumer.cpp contains actual extracted consumer with fixture interfaces. Full AI_unitValue, real metadata lookup/load, all percent consumers, RNG/game/save and DLL remain unverified. No native run triggered.

Ledger reconciliation retains PREFERENCE-20261029-04 from the feature branch and imports verified first-impression overlay result (de9caca8cd6afc6e85309b51496a29da2e258e44, run40908991199, both configurations passed) from completed native report. Complete current inventory has75 branches and no changed non-assistant source heads. Existing skipped source heads remain skipped. Review/validation gaps remain, so stop gate is false. Documentation/tests only; [skip ci].
