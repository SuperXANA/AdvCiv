# Adopted workflow native validation — 2026-10-28

Tested commit: [cb8335e59cba9ed5e3b767e6f301ae4b2664f631](https://github.com/SuperXANA/AdvCiv/commit/cb8335e59cba9ed5e3b767e6f301ae4b2664f631)
on reused PartnerDiplomacyBuild-ChatGPT.
[Run 40783621740](https://github.com/SuperXANA/AdvCiv/actions/runs/40783621740): completed, success.

## Current source reconciliation

dll-build advanced from 33b1f40e1ba564ab88950b3688425efb334126d1 to
4c135e68711a43f0e96c726a56610ea08094ba24. Read the actual diff and full workflow.
It adopts the prior single-invocation, scoped sync, distinct artifact-name and
log-path fixes (WORKFLOW-20261028-01 through -04), changes go to Rebuild,
and improves cleanup. The commit message records user-local log-path verification.
No earlier findings are reopened. All newer edits were retained.

Copied this named source workflow to the existing complete build branch,
replacing only provenance placeholders and recording feature_overlay explicitly.
No C++ file changed. The complete CvGameCoreDLL subtree is
1b1ffe40096e92a42cee0442a8f36d5b3cf644c9, identical to earlier validated
0b80d617ec269caff3241245ea7af1eb285d4c38. Current read-only 1.14 remains
5970334b64a875b5cdb370c94fc9a98db4eacda6. Recursive comparison found zero
missing baseline file paths in the overlay. Base-only files remain.
Original feature source is d37d0ca0adcaef748e0c7b32ccd90568dbee05e0.

## Exact results

| Configuration | Job | Compiler summary | Artifact |
|---|---|---|---|
| Release | 123151205799 | 0 Warning(s), 0 Error(s) | [12858660962](https://github.com/SuperXANA/AdvCiv/actions/runs/40783621740/artifacts/12858660962) |
| Debug | 123151206111 | 0 Warning(s), 0 Error(s) | [12858277899](https://github.com/SuperXANA/AdvCiv/actions/runs/40783621740/artifacts/12858277899) |

Both logs show Build succeeded and the completed compiler probe confirmation:
_MSC_VER == 1310 (MSVC 7.1).
Release build succeeded at 2026-10-28T22:58:24Z; Debug at 23:00:49Z.
Both jobs, artifact uploads and cleanup completed successfully.

Release artifact: 2,351,939 bytes,
sha256 f1f4226b61707fb244dde6a690ed640bc398f49a0a399fa3ce05211a76b66a20.
Debug artifact: 18,579,176 bytes,
sha256 cc77964d4c64a155ed53092d1f905179c4a0c8c740452381f38f9b3970994053.
The successful copy/upload steps cover the nonempty DLL, three logs, provenance,
source manifest, and Debug PDB. Debug uploader reports seven files.
Artifact service reports expiry 2026-11-04T22:55:36Z.

The workflow used shared workspace concurrency, sequential configurations,
machine-local Project configuration, stale-source cleanup, remote source
manifest check, fresh outputs and Rebuild. Both compiler summaries are clean;
a separate Actions runtime deprecation warning is not a compiler warning.

## Verification limits and coverage

This is a real full DLL build through the authorized isolated Windows workflow,
not a standalone C++03 fixture or historical result substituted for current work.
It verifies this exact complete PartnerDiplomacy overlay and workflow derivative.
It does not certify all original feature branches, in-game DLL loading,
XML/cache integration or runtime gameplay. Binary ZIP contents were not
independently downloaded/disassembled; artifact metadata and successful
copy/nonempty-file/upload steps provide the artifact evidence.

No settings changed, no original branches edited, no new branch created.
Documentation commit includes [skip ci] to avoid repeating the build.
Other partial reviews and unresolved feature-build work remain; stop gate false.
