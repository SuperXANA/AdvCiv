# Historical DLL artifact inspection — 2026-11-01

This pass downloads and inspects previously uninspected artifacts from five exact historical build commits. It does not rebuild source, change gameplay or certify a fresh full DLL build under the current procedure. User-owned branch heads remain unchanged.

| Assistant branch | Exact historical tested commit | Run | Verified artifact |
|---|---|---|---|
| CityBonusDiplomacyBuild-ChatGPT | [60d88bfa0edf155d542cd24cb4853b2651897b0f](https://github.com/SuperXANA/AdvCiv/commit/60d88bfa0edf155d542cd24cb4853b2651897b0f) | [40575245169](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169) | [Release](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169/artifacts/12767885725); [Debug + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169/artifacts/12766979488) |
| LLMDiplomacyTextBuild-ChatGPT | [6d106160bfc778b47274ef2025f02e68d183f3af](https://github.com/SuperXANA/AdvCiv/commit/6d106160bfc778b47274ef2025f02e68d183f3af) | [40548144176](https://github.com/SuperXANA/AdvCiv/actions/runs/40548144176) | [Debug + matching PDB](https://github.com/SuperXANA/AdvCiv/actions/runs/40548144176/artifacts/12753299260); [Release](https://github.com/SuperXANA/AdvCiv/actions/runs/40548144176/artifacts/12753094174) |
| LeaderTeamSizeBuild-ChatGPT | [23b8e74ea630209d67deaa53475d31113bd614b1](https://github.com/SuperXANA/AdvCiv/commit/23b8e74ea630209d67deaa53475d31113bd614b1) | [40448128843](https://github.com/SuperXANA/AdvCiv/actions/runs/40448128843) | [Release](https://github.com/SuperXANA/AdvCiv/actions/runs/40448128843/artifacts/12709332075) |
| UnitCombatUpgradeBuild-ChatGPT | [e1f41d9bed34d4035fa09b506c9e14d377268fbb](https://github.com/SuperXANA/AdvCiv/commit/e1f41d9bed34d4035fa09b506c9e14d377268fbb) | [40456936509](https://github.com/SuperXANA/AdvCiv/actions/runs/40456936509) | [Release](https://github.com/SuperXANA/AdvCiv/actions/runs/40456936509/artifacts/12713071194) |
| PromotionXPBuild-ChatGPT | [7394c4d68628bbfac61ec1366c2c2f52284c35a2](https://github.com/SuperXANA/AdvCiv/commit/7394c4d68628bbfac61ec1366c2c2f52284c35a2) | [40518367294](https://github.com/SuperXANA/AdvCiv/actions/runs/40518367294) | [Release](https://github.com/SuperXANA/AdvCiv/actions/runs/40518367294/artifacts/12741530101) |

## What was checked

All seven ZIPs were downloaded; their API-reported byte sizes and SHA256 digests match. Every ZIP entry was extracted and compared with its archived bytes. All seven DLLs have PE32 x86 DLL headers. The City Bonus and LLM Debug DLLs' CodeView RSDS identities match their extracted PDBs, including GUID and age. Binary/PDB sizes and SHA256 hashes are retained in [historical-artifacts-2026-11-01.json](historical-artifacts-2026-11-01.json).

Both City Bonus provenance records match its exact tested commit, baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6, source 084726f21f44dda2f1e8b4e3906da7ae66ce4759 and workflow 058e4d0e1760f76195071823d3e2dc85c81b7285. Its two 349-entry filename lists match the tested tree. LLM's two provenance records similarly name its tested commit, the same baseline/workflow, and source 5d12da1af2d4e6f9048d02f7e79eccb66c39051e; its 352-entry filename lists match its tested tree.

Every inspected run and job completed successfully, and retrieved runner logs report zero warnings and zero errors. City Bonus and LLM include observed MSVC 7.1 compiler probes (_MSC_VER == 1310). The three earlier single-job runs explicitly target Release but contain no such compiler probe in the retrieved logs; no fresh independent compiler-version verification is claimed for them.

Current assistant DLL/workflow blobs equal the corresponding tested tree exactly: 363 blobs for City Bonus, team size, upgrades and promotion XP; 366 for LLM. These comparisons cover repository blob identity, not the absent historical VM source-content evidence.

## Historical evidence limits

None of the seven archives contains actual MSBuild Build.log, BuildTiming.log, an actual-source content-hash manifest or a content-hash verification record. Runner totals and filename-only lists do not replace those records.

The team-size, unit-combat-upgrade and promotion-XP archives contain only CvGameCoreDLL.dll. They provide no embedded provenance, source manifest or PDB. GitHub's artifact metadata associates each archive with the exact tested commit and run above. This is a weaker association than the provenance and source-content checks available from the current workflow.

Those three runs provide Release evidence only. A Debug result is not inferred from the existence of their Release DLLs or from unrelated historical runs. Current-code XML/default/parser/UI/save/gameplay/multiplayer execution remains outside this pass.

## Publication and next work

This report, its JSON evidence and the coverage ledger are the only files published, on the existing LLMDiplomacyTextBuild-ChatGPT branch, with [skip ci]. Earlier source fixes and review reports remain unchanged. No feature code crosses branch boundaries, and no original branch is mutated.

Use the current dll-build workflow for a subsequent relevant native validation. Preserve these historical limits and the explicitly missing Debug coverage of the three single-configuration runs; do not promote this artifact inspection to current-procedure full DLL validation.
