# Failure-log workflow validation — 2026-10-31

Workflow source: dll-build 1cbd526fddeec564231958870aeab3f2be187a4e.
Read-only baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Selected source snapshot: 484ab0fca026c3b11e8975cb6c71499a2a8b685d (HatedDiplomacyDraft-ChatGPT).
DLL files exactly match the pinned baseline plus corrected feature snapshot e3887b18825dc14d026a0d8fb5f7a6b58a5c7484: 362 DLL-tree blobs, including baseline-only files. The same DLL code previously passed at 2f37cbcc50427fbf0b81a4c8e6a30270f5af35cd; that historical result is not a result for this workflow.

The source workflow's unguarded log-copy step and failure upload condition lacked a status function, leaving default success() gating after build failure. Explicit always()/build_started guards are added. Fresh remote logs are tied to run ID, attempt, configuration and commit through a token written only after previous logs are removed; mismatched tokens refuse collection. Optional logs are attempted independently, while Build.log remains required.

Local actual-block tests pass four fake-SSH/SCP cases and six manifest-gate cases. No network/Actions expression/native result is implied by those local tests.

This temporary validation revision adds an explicit Bash exit 1 only after the MSBuild SSH command succeeds. Its notice is CHATGPT_CONTROLLED_BUILD_STEP_FAILURE_AFTER_MSBUILD_SUCCESS. It is intended to test failure-log artifact publication while leaving all DLL source files unchanged. This probe must be removed after its run, then the normal workflow validated. Results and artifact evidence will be recorded after observation.
