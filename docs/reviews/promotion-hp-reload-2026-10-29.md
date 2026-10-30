# Promotion HP reconstruction — 2026-10-29

HP-20261029-02. Read-only source PromotionAltersUnitHPValues at d64fade8bb53d8c4bd92521c6a606b323af91025; reused PromotionHPDraft-ChatGPT parent f48011d732458189a54aa1d810fb7549fcd3378a. All 75 current branches inventoried; no original source-head delta against the latest ledger. Baseline remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Earlier HP-01 declaration fixes retained.

## Defect and committed correction

CvUnit::read, CvGameCoreDLL/CvUnit.cpp:10669–10677 (new block).
The feature initializes m_iMaxHPValueModifier only in the constructor (110) and adjusts it in setHasPromotion (10420) through changeMaxHPValueModifier (10492). Inspection of all four supplied DLL files found no other production writes to the modifier. read restores m_abHasPromotion directly (10635–10648), bypassing setHasPromotion, while write never serializes the modifier. Thus a fresh loaded unit retains its promotion flags but loses their maximum-HP effect. Removing a promotion afterward can then subtract an effect that was never restored.

After the complete promotion/map load, reset this derived modifier and sum getMaxHPValueChange for every held promotion. Use the existing mutator and metadata accessor. Do not call setHasPromotion, which would incorrectly replay the other already serialized promotion effects. Existing XANA date/tag text encloses the added block. No serialized field, version flag or byte order changes.

This restores current-metadata-derived behavior; it does not preserve an historical modifier value if XML metadata changes between saving and loading. The supplied implementation exposes no other adjustment source beyond promotion changes. External/native consumers outside the supplied files remain unverified.

## Verification and limits

tests/promotion-hp/reload-check.cpp embeds the actual getter, mutator, inline maxHitPoints, actual promotion delta statement and new reconstruction block. A minimal four-promotion stream/interface stand-in checks all 16 ownership masks across five metadata rotations, twice-loaded state, a following stream sentinel and removal after reload. All 160 reload cases passed strict C++03 (-Wall -Wextra -Werror -pedantic), ASan and UBSan. Negative control omitting the reconstruction fails the restored-modifier assertion. Leak detection disabled as unsupported in this environment.

The fixture does not compile the full read/write or engine metadata loader, nor verify actual legacy save bytes. No MSVC7.1, full DLL or gameplay validation claimed. Draft uses [skip ci]. Remaining review includes nonpositive maximum HP/division assumptions, accumulator and base-plus-modifier overflow, metadata/schema/cache/text integration, and engine save/load behavior. No arbitrary new HP minimum or cap was introduced.
