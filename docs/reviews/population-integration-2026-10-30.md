# City population integration disposition — 2026-10-30

Coverage disposition POPULATION-20261030-02, refining the unresolved integration questions already recorded in population-owner-2026-10-28.md. This is a documented source-implementation skip, not a repeated claim of a newly discovered owner-context defect.

Original CityPopulationTrait: dd39c040ee3a25fc8463ad4c484b72bd5f0d8ab3.
Reused assistant branch CityPopulationDraft-ChatGPT parent: 54c845200c207cea5cab663df399ece52cc385ab.
Read-only 1.14 baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Complete current inventory: 75 branches; no original head changes against global ledger 7e1294956a9b3eaaf9f3d67b6172c4f57b9bdd1c.

## Actual source coverage and evidence

Read the complete metadata implementation/declaration, relevant player initialization/reset/trait processing/change-leader/load/write paths, city population helper and its consumers, plus the source README and complete recursive file inventory. Original tree contains six DLL .cpp/.h files and README only, no XML or schema. Both metadata files are byte-identical between the original source and assistant parent.

CvGameCoreDLL/CvInfo_Civilization.cpp:
- CvCivilizationInfo constructor line 28 initializes m_bExtraPopulation(false).
- CvTraitInfo constructor line 1102 initializes m_bExtraPopulation(false).
- These are the only two occurrences of that member in the entire implementation file.
- CvCivilizationInfo::read(XML) at 281, readPass2 at 399 and CvTraitInfo::read(XML) at 1219 contain no assignment/load for it.
- Conditional civilization metadata cache read at 202 and write at 250 also omit it.
The header exposes only getters (lines 62 and 393) and protected fields (90 and 427). No mutation interface provides an alternative configuration path.

CvGameCoreDLL/CvPlayer.cpp:
- reset zeros m_iExtraPopulation at 426.
- processTraits at 563 adds/removes kTrait.getExtraPopulation at 591, including the existing leader-change remove/apply calls at 715/725.
- changeExtraPopulation at 8371 merely adds its argument at 8373.
- CvPlayer::read at 14074 calls reset, then neither reads this field nor reconstructs it from traits. write likewise has no counterpart.
These are all counter references in the supplied implementation. No external setter call appears among the six supplied DLL files. This demonstrates a load-lifecycle gap once metadata becomes configurable; it does not prove the intended persistence policy for future external effects.

CvCity::initialPopulation at 13145–13157 consumes the civilization getter and player trait-derived counter. The earlier owner-context correction remains intact. With the supplied metadata initialization/loading paths, both new bonus sources remain zero. A compiler success alone would therefore not validate an operational extra-population feature.

## Why no speculative completion or build

The source does not supply the XML tag/schema/installation data for either flag, cache compatibility policy, or a persistence-versus-reconstruction contract for the mutable player counter. Do not select new authoring data or append a save/cache field merely to force a DLL result. No XML tags, schemas, save versions or gameplay values are invented here.

The original head is now marked skip_until_source_head_changes in the ledger, and assistant integration/build work is paused_with_missing_source_implementation. Resume when user source work supplies the missing integration details; inspect any new original-head delta before changing the disposition. Preserve the existing owner-aware helper refinement and its historical fixture evidence.

No production code changed in this disposition commit. It uses [skip ci]; no native build, engine XML test, save round trip, gameplay test or new fixture result is claimed. Once authoring/loading exists, verify both true and false metadata cases, cache cold/warm loads, save/reload bonus reconstruction, and leader changes without double counting.
