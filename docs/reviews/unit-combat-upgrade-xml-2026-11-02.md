# Unit-combat upgrade trait XML integration — 2026-11-02

The staged configuration restores the authored `TRAIT_AGGRESSIVE` → `UNITCOMBAT_GUN` modifier of **-50**, preserves the 11 compiled baseline records, and adds the five source traits that are actually referenced by MLPCiv leaders. All 16 trait identifiers used by the inspected leader file now resolve. The full installation still has the two known asset issues described below; this report does not establish game initialization.

Integration branch: `UnitCombatUpgradeXML-ChatGPT`, based on compiled-branch head `6786d8d79fda34d6bfce45526ba6d489df916f35`. Original feature branch, verified build branch, `1.14`, and MLPCiv remain unchanged.

## Pinned inputs

| Input | Revision |
|---|---|
| [Original feature](https://github.com/SuperXANA/AdvCiv/tree/3e8418a1b6840192f21af4650dcfce89a8c557d1) | `3e8418a1b6840192f21af4650dcfce89a8c557d1` |
| Compiled feature head | `6786d8d79fda34d6bfce45526ba6d489df916f35` |
| Verified Release/Debug source commit | `d0ee554823f99f0d72a2c90a77463235e08c2fa6` |
| AdvCiv 1.14 baseline | `5970334b64a875b5cdb370c94fc9a98db4eacda6` |
| [MLPCiv installation assets](https://github.com/SuperXANA/MLPCiv/tree/7bd66c170c3689e0433cf9309554f609b4894ec9) | `7bd66c170c3689e0433cf9309554f609b4894ec9` |

MLPCiv's pinned tree contains neither a trait override nor a civilization schema override, and contains no `Assets/XML/Units` definitions. Its civilization folder contains the existing leader and civilization files. This is an inspection of the published tree, not of a private local installation.

## Trait reconciliation

| Additional authored trait | Active references in MLPCiv | Disposition |
|---|---|---|
| `TRAIT_MEDIC` | `LEADER_AMAI`, `LEADER_UHANE` | Preserve complete source record |
| `TRAIT_SEAFARING` | `LEADER_SEAPONY` | Preserve complete source record |
| `TRAIT_SPACEFARING` | `LEADER_DECA` | Preserve complete source record |
| `TRAIT_RANGER` | `LEADER_DARINGDO` | Preserve complete source record |
| `TRAIT_DIVINE_TYPE_IV` | `LEADER_SITELAE`, `LEADER_SOLAIS` | Preserve complete source record; Destiny dependency unresolved |

There are **no unmatched trait records** in this snapshot. All five belong to the inspected installation's leader configuration. Their values and comments are copied without reinterpretation; line endings follow the compiled file. The [complete original XML](../integration/unit-combat-upgrade-2026-11-02/source-CIV4TraitInfos.xml) is also retained byte for byte outside `Assets`, preserving every record for later selective integrations without creating another loadable trait file.

The 11 common records already have the same non-feature values in the source and compiled versions. Their existing compiled bytes remain unchanged outside the Aggressive modifier insertion and the appended custom-trait section. In particular, Ranger's authored wonder-production values, Divine's domestic-general value, and all original free promotions are retained. Original XANA markers surround the Gun modifier; the appended section has a dated XANA annotation. No trait is assigned to a new leader.

## Structural and calculation checks

- Sixteen unique staged trait identifiers cover every trait reference in the 146 inspected leader records. The five added records retain source order after the original 11.
- The shared schema is unchanged from the compiled branch. It declares `iUpgradeCostUnitCombat` as signed `int`, orders each pair as `UnitCombatType` then `iUpgradeCostUnitCombat`, and places the optional list after `FreePromotionUnitCombats`.
- Host XML checks accept absent and empty optional lists, signed negative/zero/positive values and the XDR integer endpoints. They reject boolean values, integer overflow and reversed pair/list ordering. Acceptance of the integer endpoints by the schema does not establish safe extreme gameplay arithmetic.
- The unchanged production loader defaults omitted lists and unlisted combats to zero; its getter also returns zero for a null modifier array. Source inspection establishes this default, not an executed engine-parser test.
- Trait contributions remain signed integer totals. The existing effective bounds leave -50 unchanged. `upgradePrice` selects the **destination** unit combat and applies this percentage after the existing AI/unit discounts. With no other combat-trait contribution, pre-modifier prices 100 and 101 become 50 and 51 under MSVC integer truncation. Python price overrides and barbarian early returns still bypass this path. These are arithmetic reference examples, not observed in-game prices.
- Every combat identifier in the staged traits is also used by the inspected baseline unit XML. The inherited BtS `CIV4UnitCombatInfos.xml` is not supplied in either inspected tree, so its actual loaded identifier table remains a runtime check.

The [read-only audit tool](../../tools/validate_unit_combat_upgrade_xml.py) reproduces the main configuration and related-asset checks:

```sh
python3 tools/validate_unit_combat_upgrade_xml.py --mlpciv-dir /path/to/MLPCiv
python3 tools/validate_unit_combat_upgrade_xml.py --mlpciv-dir /path/to/MLPCiv --strict-dependencies
```

The first command passes the staged trait checks while reporting existing related-asset issues. The strict command exits 1 on the inspected snapshot, as expected. The tool checks schema-declared sequences, occurrences and relevant scalar types with a host XML parser; it does not implement or execute the complete Civ4/MSXML XDR validation environment.

## Known installation issues

| ID | Evidence | Effect and disposition |
|---|---|---|
| `UCU-XML-001` | Compiled trait XML lacked the source Aggressive Gun list | Closed in the staged configuration by preserving the exact authored -50 entry |
| `UCU-XML-002` | Source `TRAIT_DIVINE_TYPE_IV` grants `PROMOTION_DESTINY`; neither the compiled promotion definitions nor published MLPCiv assets define it | Dependency remains unresolved. The authored trait is preserved, including that reference. A real promotion definition must be supplied before treating the complete configuration as ready; no substitute effect or placeholder is invented |
| `UCU-XML-003` | MLPCiv `LEADER_BARBARIAN` has three `DiploMusicWarEra` elements inside `DiplomacyMusicPeace` for Industrial/Modern/Future | Existing shared-schema mismatch, independent of the upgrade modifier. The unchanged schema permits `DiploMusicPeaceEra` there. The existing leader file is not rewritten by this integration |

The remaining 145 leader records and all 40 civilization records pass the same host sequence checks. This is not a complete dependency audit of the mod's art, text, audio, units, buildings or other features. Successful trait checks must not be presented as successful whole-mod startup.

## Installation staging

The two files needed by this feature's XML overlay are:

1. `Assets/XML/Civilizations/CIV4TraitInfos.xml` from this branch.
2. `Assets/XML/Civilizations/CIV4CivilizationsSchema.xml` from this branch, with its existing signed-int correction. Do not substitute the original feature's boolean schema.

These paths fit the published MLPCiv layout. The known dependency/schema issues above remain open; no files are installed into MLPCiv by this commit. Copying the whole AdvCiv `Assets` tree would overwrite unrelated MLPCiv data and is not the integration procedure.

For a local installation with additional trait edits, merge the Aggressive list and only missing trait records by `Type`, preserving its other fields and local records. The [discount-only patch](../integration/unit-combat-upgrade-2026-11-02/aggressive-only.patch) adds just the original Gun list to the compiled baseline layout; run `git apply --check` from the mod root before applying it. It was checked and applied to a CRLF copy with an unrelated customized Aggressive health value, which remained unchanged. A context mismatch requires a targeted merge, not replacement of the local XML. An existing customized schema similarly needs only the three feature element definitions and the optional `TraitInfo` list entry reconciled with signed `int` values. Any source records not referenced in a different installation remain available in the archive outside `Assets`.

## DLL evidence and runtime limits

The complete `CvGameCoreDLL` subtree remains `f2a5da8477c263aa2c5784c3a2ce68d9671430ac`, identical to the verified source commit. The workflow is also unchanged. Reuse [run 41390572710](https://github.com/SuperXANA/AdvCiv/actions/runs/41390572710) and its [native matrix review](upgrade-native-2026-11-01.md): both Release and Debug jobs completed successfully with MSVC 7.1. No new DLL build is requested for these XML/documentation/host-audit changes; AdvCiv 1.14 and the C++03/MSVC 7.1 implementation remain intact.

Civ4 XML initialization, active trait addition/removal, actual upgrade selection/prices and save/reload remain unexecuted. After resolving the installation dependencies, verification must use a new game with Aggressive and control leaders, upgrades into Gun and other combats, then save after several turns and reload to compare the same prices. Structural validation and reused compilation evidence do not establish those runtime results.
