#!/usr/bin/env python3
"""Audit this XML overlay without invoking Civ4 or changing an installation."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


FEATURE = "UpgradeCostModifierUnitCombats"
COMBAT = "UNITCOMBAT_GUN"
DT_TYPE = "{urn:schemas-microsoft-com:datatypes}type"
ARCHIVE = Path("docs/integration/unit-combat-upgrade-2026-11-02")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def text(node, name):
    return node.findtext("{*}" + name)


def records(path, name):
    root = ET.parse(path).getroot()
    result = {}
    for node in root.iter():
        if local(node.tag) == name:
            key = text(node, "Type")
            assert key and key not in result, "Missing or duplicate identifier: " + str(key)
            result[key] = node
    return result


def semantic(node, exclude_feature=False):
    return (local(node.tag), (node.text or "").strip(), dict(node.attrib),
            [semantic(child, exclude_feature) for child in node
             if not (exclude_feature and local(child.tag) == FEATURE)])


def modifiers(trait):
    result = {}
    for pair in trait.findall("{*}" + FEATURE + "/{*}UpgradeCostModifierUnitCombat"):
        key = text(pair, "UnitCombatType")
        assert key and key not in result, "Missing or duplicate combat modifier: " + str(key)
        raw = text(pair, "iUpgradeCostUnitCombat") or ""
        assert re.fullmatch(r"[+-]?[0-9]+", raw), "Modifier is not a signed integer: " + raw
        value = int(raw)
        assert -2147483648 <= value <= 2147483647, "Modifier exceeds XDR int range"
        result[key] = value
    return result


def schema_check(node, definitions):
    """Check declared sequence, occurrences and scalar types, not the MSXML engine."""
    name = local(node.tag)
    definition = definitions[name]
    if definition.get("content") == "textOnly":
        assert not list(node), "Unexpected child in " + name
        raw = (node.text or "").strip()
        kind = definition.get(DT_TYPE)
        if kind == "int":
            assert re.fullmatch(r"[+-]?[0-9]+", raw), "Invalid XDR integer: " + name
            assert -2147483648 <= int(raw) <= 2147483647, "XDR integer overflow: " + name
        elif kind == "boolean":
            assert raw in ("0", "1", "false", "true"), "Invalid XDR boolean: " + name
        return
    children = list(node)
    index = 0
    for field in definition.findall("{*}element"):
        count = 0
        maximum = field.get("maxOccurs", "1")
        while index < len(children) and local(children[index].tag) == field.get("type"):
            schema_check(children[index], definitions)
            index += 1
            count += 1
        assert count >= int(field.get("minOccurs", "1")), "Missing field in " + name
        assert maximum == "*" or count <= int(maximum), "Duplicate field in " + name
    assert index == len(children), "Unknown or out-of-order field in " + name


def blob_sha(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def audit(repo, installation):
    trait_path = Path("Assets/XML/Civilizations/CIV4TraitInfos.xml")
    schema_path = Path("Assets/XML/Civilizations/CIV4CivilizationsSchema.xml")
    baseline = records(repo / ARCHIVE / "baseline-CIV4TraitInfos.xml", "TraitInfo")
    source = records(repo / ARCHIVE / "source-CIV4TraitInfos.xml", "TraitInfo")
    staged = records(repo / trait_path, "TraitInfo")
    schema = ET.parse(repo / schema_path).getroot()
    definitions = {x.get("name"): x for x in schema.findall("{*}ElementType")}
    assert definitions["iUpgradeCostUnitCombat"].get(DT_TYPE) == "int"
    feature_field = definitions["TraitInfo"].find("{*}element[@type='" + FEATURE + "']")
    assert feature_field is not None and feature_field.get("minOccurs") == "0"
    schema_check(ET.parse(repo / trait_path).getroot(), definitions)
    assert modifiers(source["TRAIT_AGGRESSIVE"]) == {COMBAT: -50}
    assert modifiers(staged["TRAIT_AGGRESSIVE"]) == {COMBAT: -50}
    for key, original in baseline.items():
        assert semantic(original, True) == semantic(staged[key], True), "Changed baseline trait: " + key
    extras = [key for key in source if key not in baseline]
    for key in extras:
        assert semantic(source[key]) == semantic(staged[key]), "Changed authored trait: " + key
    assert set(staged) == set(source), "Source trait records were lost or new ones invented"
    assert all(not modifiers(node) for key, node in staged.items() if key != "TRAIT_AGGRESSIVE")

    users = {}
    leaders = records(installation / "Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml", "LeaderHeadInfo")
    for key, leader in leaders.items():
        for trait in leader.findall("{*}Traits/{*}Trait"):
            assert text(trait, "bTrait") in ("0", "1"), "Invalid trait flag: " + key
            identifier = text(trait, "TraitType")
            assert identifier, "Empty trait reference: " + key
            # Even a disabled reference should resolve to an identifier.
            assert identifier in staged, "Unknown leader trait: " + identifier
            if text(trait, "bTrait") == "1":
                users.setdefault(identifier, []).append(key)
    assert all(key in users for key in extras), "Unreferenced source traits must be retained outside Assets"
    for trait in staged.values():
        modifiers(trait)

    # Both repos inherit the UnitCombatInfo definition table from BtS. These
    # checks establish consistency with unit XML, not direct table loading.
    units_path = Path("Assets/XML/Units/CIV4UnitInfos.xml")
    units = records(installation / units_path if (installation / units_path).exists() else repo / units_path, "UnitInfo")
    combat_refs = {text(unit, "Combat") for unit in units.values()}
    trait_combat_refs = {node.text for trait in staged.values() for node in trait.iter()
                        if local(node.tag) == "UnitCombatType"}
    assert trait_combat_refs <= combat_refs, "Unknown unit-combat reference in trait data"
    promotions_path = Path("Assets/XML/Units/CIV4PromotionInfos.xml")
    promotions = records(installation / promotions_path if (installation / promotions_path).exists() else repo / promotions_path, "PromotionInfo")
    promotion_refs = {node.text for trait in staged.values() for node in trait.iter()
                      if local(node.tag) == "PromotionType"}
    missing_promotions = sorted(promotion_refs - set(promotions))
    related_schema_issues = []
    for filename, record_type in (("CIV4LeaderHeadInfos.xml", "LeaderHeadInfo"),
                                  ("CIV4CivilizationInfos.xml", "CivilizationInfo")):
        path = Path("Assets/XML/Civilizations") / filename
        for key, node in records(installation / path, record_type).items():
            try:
                schema_check(node, definitions)
            except (AssertionError, KeyError) as error:
                related_schema_issues.append({"path": str(path), "identifier": key,
                                             "reason": str(error)})
    return {
        "structural_configuration_checks": "pass",
        "baseline_traits_preserved": len(baseline),
        "staged_traits": len(staged),
        "installed_leader_records": len(leaders),
        "installed_trait_identifiers_resolved": sorted(users),
        "additional_source_traits": {key: users.get(key, []) for key in extras},
        "unmatched_trait_records": [key for key in extras if key not in users],
        "aggressive_upgrade_cost_modifiers": modifiers(staged["TRAIT_AGGRESSIVE"]),
        "unit_combat_references_consistent_with_unit_XML": sorted(trait_combat_refs),
        "direct_UnitCombatInfo_table_validation": "not available in inspected repositories",
        "unresolved_promotion_dependencies": missing_promotions,
        "trait_promotion_dependencies_complete": not missing_promotions,
        "installed_leader_civilization_schema_issues": related_schema_issues,
        "known_installation_blockers_resolved": not (missing_promotions or related_schema_issues),
        "staged_traits_git_blob": blob_sha(repo / trait_path),
        "staged_schema_git_blob": blob_sha(repo / schema_path),
        "engine_XML_initialization": "not run",
        "in_game_upgrade_pricing": "not run",
        "save_reload": "not run",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mlpciv-dir", type=Path, required=True)
    parser.add_argument("--repo-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--strict-dependencies", action="store_true")
    args = parser.parse_args()
    result = audit(args.repo_dir, args.mlpciv_dir)
    print(json.dumps(result, indent=2))
    return int(args.strict_dependencies and not result["known_installation_blockers_resolved"])


if __name__ == "__main__":
    raise SystemExit(main())
