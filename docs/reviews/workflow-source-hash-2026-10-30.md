# Source hashing workflow validation — 2026-10-30

Validated submitted dll-build workflow 9f62e13990b39a8c16e8c6dd404c6aca995e53f3 using known-passing hated-diplomacy snapshot 2f37cbcc50427fbf0b81a4c8e6a30270f5af35cd, previously successful Release/Debug run https://github.com/SuperXANA/AdvCiv/actions/runs/41126096699. Reused HatedDiplomacyDraft-ChatGPT parent 533a1b6ad1ff00e1f7637e49849647df827e84a0; no branch created. Parent differs from the passing commit only in documentation.

## Exact test and outcome

Tested commit 52875b0b3b93ee49408d94cf983d59cf13956014; successful run https://github.com/SuperXANA/AdvCiv/actions/runs/41128696560.
- Release job 124313753468: success; MSVC 7.1 toolset probe passed.
- Debug job 124313753016: success; MSVC 7.1 toolset probe passed.

No DLL source changes. Complete passing 1.14 overlay retained, with baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6. Actual workflow copied from dll-build; only BASE_COMMIT_SHA, FEATURE_COMMIT_SHA and WORKFLOW_COMMIT_SHA populated with baseline, passing source snapshot and workflow source respectively. Main dll-build and 1.14 remain read-only. No hashing implementation correction was needed on this environment.

YAML parsing and Bash syntax checking of the submitted build step also passed locally. This does not substitute for the actual Windows/Linux run above.

## Downloaded artifact evidence

All four artifact ZIPs downloaded and extracted:

| Configuration | Source-verification diagnostics | DLL artifact |
| --- | --- | --- |
| Release | 13011264262 (31,091 bytes) | 13012616456 (2,348,551 bytes) |
| Debug | 13013200055 (31,090 bytes) | 13013085398 (18,551,455 bytes) |

Both diagnostics contain expected-sources.txt, actual-sources.txt, empty source-hashes.diff, source-verification.txt ending status=passed and build-provenance.txt. Each manifest has 349 records in lowercase SHA256 + two spaces + ./filename form. Independently collected Windows and Linux manifest bytes are identical, and Debug/Release input manifests are also identical. Their file-name sets equal those from the earlier passing filename-only artifact.

Independently recomputed SHA256 for all four manifest files:
b1ea9061f07bf130e6965cda3e0df31f2c48ad559bf5e8fd8ce5b73317edf995

This equals both expected_sources_manifest_sha256 and actual_sources_manifest_sha256 in each provenance file. Also verified exact tested commit/configuration/base/feature/workflow pins, source_hash_algorithm=SHA256, source_scope=root:.c,.cpp,.h,.inl, source_manifest_format=sha256sum-v1 and source_hash_verification=passed.

Both actual artifact Build.log files report Rebuild succeeded, 0 Warning(s), 0 Error(s). Both DLLs verified as PE32 x86 with DLL characteristics:
- Release: 6,565,888 bytes; SHA256 9fabd09624eae8407de5b4cf385118cf887fec85531eb8780d492c39049ff63e.
- Debug: 25,186,304 bytes; SHA256 8eac879035461dcb54877e69a8a0f148e1a769503f386cd36c3cb51c86d66cc3.
- Debug PDB present: 70,585,344 bytes.

The new workflow intentionally splits source diagnostics/provenance from compiled binaries; inspect both artifact types together. Source-verification status progresses from collecting to passed on success. This test did not produce a failure requiring builder MSBuild diagnostics.

## Comparison failure controls

tests/build-workflow/hash-guard-check.py extracts the exact current Bash block from test -s actual-sources.txt through the status=passed write, ending before provenance/compilation. It runs in temporary local directories and checks an added compiler-reached marker:
- Matching manifest accepted and continues.
- Changed hash, missing file, extra file, changed filename case and empty remote manifest all rejected before continuation.

All six cases pass using the actual downloaded 349-file Release manifest. They also pass with the script's default small fixture. These are local comparison/exit-status tests, not a deliberate tampering experiment on the Windows builder or negative full-DLL runs. No remote source altered for fault injection.

Run: python3 tests/build-workflow/hash-guard-check.py
Optional: --manifest /path/to/expected-sources.txt --workflow /path/to/auto-dll-build.yml

## Limits and publication

The submitted scope hashes root .c/.cpp/.h/.inl files only, matching the previous root-name check; nested headers/libraries and machine-local Project configuration are outside it. Exact byte synchronization, independent manifest agreement, provenance digest consistency, compiler probe and positive full builds are observed. No broader source-integrity scope, save/cache compatibility or gameplay validation is claimed.

Evidence/test-only follow-up uses [skip ci] and leaves tested DLL sources and workflow unchanged. Original branches preserved; no merge, force push, settings change or new assistant branch.
