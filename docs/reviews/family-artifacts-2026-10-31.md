# Family-relations historical artifact inspection — 2026-10-31

Reviewed assistant head: `f07cf78b4afea17cef1514a1960890ab709c6e3d`; original LeaderFamilyRelations remains read-only at `ba88a0e713fb21fccff9ae2469164af78544bc2b`. Baseline remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`.

## Scope and result

The [earlier review](family-relations-2026-10-27.md) expressly left downloaded-binary inspection undone. This follow-up closes that limited gap. It proposes no new C++ correction and does not repeat the four previously reported findings.

The actual relationship metadata read/clamp/mapping code, player reset/reconstruction/personality hooks, first-impression consumer and loader ordering were revisited against the existing report. No new actionable source defect was established in that scope. This does not certify unspecified XML/schema/default inheritance or real engine execution.

The exact historical [run 40564726051](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051) completed successfully for `5b41bb1d9598a514c99f8fe8e59333a884f56c0b`. Its complete 362-blob CvGameCoreDLL tree is identical to the current assistant head. All baseline DLL files remain present; the seven differing baseline files are unchanged from that tested commit. No unrelated historical run is substituted.

Both ZIPs were downloaded, their archive byte sizes and SHA-256 digests checked against GitHub metadata, and their contents extracted:

| Configuration | Verified artifact | DLL size | Format |
| --- | --- | --- | --- |
| Release | [12762701765](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051/artifacts/12762701765) | 6,574,080 bytes | PE32 x86 DLL |
| Debug | [12763151213](https://github.com/SuperXANA/AdvCiv/actions/runs/40564726051/artifacts/12763151213) | 25,239,552 bytes | PE32 x86 DLL |

The Debug PDB is 70,716,416 bytes. Its MSF stream identity matches the DLL CodeView RSDS record: GUID `75940495-4598-47b4-ad0a-38700f811659`, age 1. This verifies the supplied symbol/binary pair, not debugger attachment or symbol loading in a running game.

Both provenance files identify the exact commit, configuration, compiler, baseline, original feature source and historical workflow source `058e4d0e1760f76195071823d3e2dc85c81b7285`. Both 349-name source lists match one another and the root C/C++/header/inl filenames in the tested Git tree. DLL/PDB SHA-256 digests and all verification fields are recorded in [machine-readable evidence](family-artifacts-2026-10-31.json).

## Verification limit: historical diagnostics were not archived

Neither ZIP contains MSBuild's actual Build.log, BuildTiming.log, an actual-source manifest, or source-content hashes. The source manifest lists names only. The old job outputs report Build succeeded, zero warnings/errors and the selected _MSC_VER == 1310 probe in both configurations, but those runner outputs do not replace an independently accessed Build.log.

Accordingly this is **partial historical artifact verification**, not a new DLL build or full validation under the current procedure. The Git-tree comparison establishes that checked-in DLL sources did not change after the tested commit; the historical filename list/provenance cannot establish byte-for-byte contents of the old Windows build workspace. The missing historical Build.log and source hashes remain unavailable from these artifacts.

The current dll-build source remains `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`; no older workflow was restored and no unchanged build was triggered. A future relevant source change can use the current procedure to produce the required evidence. No game launch, actual XDR/XML load, save load, attitude-cache behavior or multiplayer result is claimed. Missing authored relation/relationship XML and schemas remain as described in the earlier report; none were invented.

This publication changes only review documentation and the coverage ledger, using [skip ci].
