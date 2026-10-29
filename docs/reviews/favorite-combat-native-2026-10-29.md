# Favorite combat native validation — 2026-10-29

Exact tested overlay53e3fb35bddc9c2bf67acc7a8d3b3254df5e0003, feature snapshotb031f2f2fb23fd7de7aed3901692f52753e4cd00, original799082c323ea44335c66b9714e1a9bb365c12095.
Baseline5970334b64a875b5cdb370c94fc9a98db4eacda6 unchanged/read-only. Complete baseline root plus feature files, retaining every baseline DLL path; recursive-tree verification zero missing base DLL paths and zero feature DLL SHA mismatches.
Actual workflow source6343afabdc57996ea875b6e8541b69ad333d0686, provenance placeholders filled. Existing FavoriteUnitCombatDraft-ChatGPT reused.

Run https://github.com/SuperXANA/AdvCiv/actions/runs/40968286063 completed successfully.
Release job123778264073 and Debug123778263843 both logs confirm _MSC_VER1310/MSVC7.1 and 0 warnings,0 errors.
Release artifact12939700982 size2352948; Debug artifact12939093068 size18563304. Successful DLL copy, nonempty check and upload observed. Artifact metadata verified; ZIP contents not independently downloaded/disassembled.

This validates existing scoped unit-value guard, combat-key lookup/bounds, missing semicolon and destructor ownership corrections in full native DLL context. Original unchanged branch is not certified by this derivative build. No engine XML/schema/cache runtime or gameplay test claimed. Especially note source XML is under XML/ rather than installed Assets/XML; build success alone does not install custom leader metadata.

No additional compiler fix needed in this run. Documentation-only followup [skip ci].
