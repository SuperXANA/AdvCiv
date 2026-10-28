# Equipment acquisition gate draft — 2026-10-27

## Scope and inputs

Source: [FFHEquipmentTypes at d585bfd6a9a3315a0eb351d73d78c84d37cc37f5](https://github.com/SuperXANA/AdvCiv/tree/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5), root tree 6a1ff3ffbb499f96368c5e939d5801f41a118345.
Read-only baseline: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

All 29 source blobs were retrieved; XANA blocks in the eight marked DLL files and the supplied equipment/holding XML and schema additions were read. The current branch heads did not introduce new original-source changes; the RaceDemographicsDraft documentation head is already delivered evidence. This pass continues the pending first-pass rotation.

Only CvUnit::canAcquireEquipment and CvUnit::isEquipmentValid are changed, inside the original XANA 08-26-2025 equipment block. All original XANA boundaries/dates and unrelated code are preserved. Tests and this review are additive. This sparse source draft is not a complete-base build overlay and is not an install-ready equipment system.

## EQUIPMENT-20261027-01 — maximum level compares against the minimum

The [upper-level gate](https://github.com/SuperXANA/AdvCiv/blob/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5/CvGameCoreDLL/CvUnit.cpp#L10607) checks whether a maximum exists, then compares the unit's equipment level with getEquipmentLowestLevelRequired. The supplied [Alicorn Amulet XML](https://github.com/SuperXANA/AdvCiv/blob/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5/XML/Units/CIV4EquipmentInfos.xml) defines minimum 1 and maximum 9. Once the surrounding compile gaps are resolved, that condition would reject levels 2–9 even though they fall within the declared interval.

Use the actual maximum for the ceiling and cache both bounds and the level locally. Positive bounds remain inclusive; a nonpositive bound remains unset. A class-indexed level is queried only when a positive level bound requires it, and a missing equipment class returns false before that query.

## EQUIPMENT-20261027-02 — absent optional prerequisites reject equipment

The [unit validity wrapper](https://github.com/SuperXANA/AdvCiv/blob/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5/CvGameCoreDLL/CvUnit.cpp#L10726) rejects NO_PROMOTION and NO_EQUIPMENT prerequisites. That would require both optional AND prerequisite fields to be populated, independently of the acquisition method's existing conditional ownership checks. The provided metadata class does not yet expose those prerequisite methods, so this is a source-logic diagnosis rather than an observed in-game outcome.

Delegate unit-type feasibility to the existing unit-info interface. Keep current promotion/equipment ownership checks in canAcquireEquipment, where absent prerequisites impose no requirement. Preserve independent AND requirements and each three-way OR group. This follows the separation between feasibility and current ownership in the pinned [1.14 promotion gate](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvUnit.cpp).

The underlying CvUnitInfo::isEquipmentValid implementation is not rewritten or certified by this draft.

## EQUIPMENT-20261027-03 — invalid syntax and wrong metadata identifier

The [legendary gate](https://github.com/SuperXANA/AdvCiv/blob/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5/CvGameCoreDLL/CvUnit.cpp#L10622) uses invalid if !(...) syntax. The [promotion OR group](https://github.com/SuperXANA/AdvCiv/blob/d585bfd6a9a3315a0eb351d73d78c84d37cc37f5/CvGameCoreDLL/CvUnit.cpp#L10653) refers to ePromotion, which is not a parameter/local in this method, instead of the candidate equipment. Those are compiler blockers in the selected method.

Rewrite the predicates around one CvEquipmentInfo const reference for the candidate. Add release-mode candidate bounds checks before metadata or ownership lookup; invalid candidate IDs return false in both methods. Preserve team technology, magic technology class and magic technology requirements as separate conditions. These interfaces are simulated in the fixture because the complete equipment metadata/magic integration is still unfinished.

## Mechanics preserved and integration decisions

Heroes bypass only a legendary item's enchantment requirement, as the source note specifies. They still obey level bounds, personal-unit identity, ordinary promotion/equipment prerequisites, and team technology requirements. Nonlegendary items retain the source behavior of not applying the legendary enchantment clause. Personal equipment with no explicit unit prerequisite retains the source's unrestricted identity behavior.

An item with no positive level bounds does not require a level lookup. This does not grant universal class eligibility: the unit-info feasibility interface still decides that first. The draft preserves the existing true argument to that interface, matching the source's promotion-style delegation; it does not invent a different leader-only policy.

Slot capacity, holding anatomy, timed promotion changes, item removal/transfer and dependency-cycle policy need their own coherent integration. In particular, current inventory ownership and type feasibility should remain distinct from whether an item is currently equipped in an available slot. No slot/effect rules or lore data are invented here.

## Verification

Run:

```
python3 tests/equipment-gates/check.py
```

The actual revised two methods and unchanged canAcquireEquipmentAny method are extracted from CvUnit.cpp and compiled against instrumented metadata/unit/team stubs using strict g++ C++03, -Wall -Wextra -Werror -pedantic, ASan and UBSan. LeakSanitizer is disabled for host compatibility.

Passed checks include:

- The supplied Alicorn Amulet XML values 1 and 9, levels 0 through 10, and a small independent inclusive-bound truth table with unset bounds.
- Absent prerequisites, separate AND requirements, all three OR slots, and combinations of promotion/equipment requirements.
- Legendary enchanted/non-enchanted/hero cases; hero rejection for excessive level, wrong personal identity, or unmet ordinary technology.
- Ordinary technology and both magic requirement categories.
- Already-owned items, rejected static feasibility, invalid candidate IDs without metadata queries, and missing class without sentinel level lookup.
- Any-acquirable iteration and unchanged unit ownership/promotion/level state.

The first record's level values come from the actual XML; other test metadata are synthetic interface fixtures, not added live game balance data. The fixture's static unit-info feasibility predicate and magic interfaces are stubs. It does not compile or execute CvUnitInfo::isEquipmentValid, the full equipment info class, EnumMap storage, or the XML reader. This is not a whole-file or DLL compiler test.

## DLL and runtime limits

No DLL build is triggered and no workflow is added. The source is not yet a coherent native integration: for example, the supplied CvEquipmentInfo declaration lacks prerequisite/technology accessors used by the acquisition gate, and the underlying unit-info equipment feasibility code remains unfinished. Info ownership/loading, slot metadata/effects, XP/level lifecycle and versioned persistence still need work.

No native DLL artifact, in-game equipment acquisition, XDR schema loading, promotion mutation/removal, save/load or multiplayer result is claimed. When the feature is coherent enough for useful native validation, reuse this isolated branch for a pinned complete 1.14 overlay retaining base-only files and the named dll-build workflow; a standalone fixture must not substitute for that build.

The original branch and 1.14 snapshot remain unchanged. The companion ledger records a partial scoped review and the exact draft code commit; nine first-pass targets remain pending. The stopping condition is not met.
