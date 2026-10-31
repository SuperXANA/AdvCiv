# Conditional source-diagnostics upload review — 2026-10-31

Read-only dll-build source `07133f27906c364b266043a1788ec0eacd2e8b3b`, compared with previously hash-validated workflow `9f62e13990b39a8c16e8c6dd404c6aca995e53f3`. Fresh 75-branch inventory found this workflow and RealisticAIDecisions changed; both deltas were reviewed first. No workflow code was changed or published by this review.

## Changed behavior

The sole changed line is [auto-dll-build.yml:213](https://github.com/SuperXANA/AdvCiv/blob/07133f27906c364b266043a1788ec0eacd2e8b3b/.github/workflows/auto-dll-build.yml#L213): diagnostic artifact upload now requires `always() && steps.build.outputs.source_verification_started == 'true'`, rather than always() alone.

The existing build step has id build. Its Bash script creates source-verification.txt with status=collecting, then writes source_verification_started=true to GITHUB_OUTPUT, before collecting either hash manifest or invoking the compiler. Thus the guard is tied to entry into source verification, not successful verification/build. It permits diagnostic upload after later failures, while earlier checkout/rsync failures have no new source-verification output to upload.

The comparison proves that the SHA256 scripts/gate, synchronization, compiler probe/build, matrix, provenance generation, DLL artifact paths and cleanup are byte-for-byte unchanged. No production correction is warranted for this one-line condition.

## Verification and limits

Parsed the actual current YAML locally and checked:
- build step ID matches the condition reference;
- the exact marker occurs once, after status-file creation and before manifest/hash/compiler work;
- replacing only the old upload condition with the new condition reproduces the complete current workflow exactly.

Ran the existing tests/build-workflow/hash-guard-check.py fixture against this workflow's actual extracted Bash hash gate using the previously downloaded 349-file manifest as test input. All six local cases passed: matching accepted; changed hash, missing source, extra source, filename case change and empty remote manifest rejected before the simulated compiler marker. The historical manifest is fixture input only, not a fresh remote Windows measurement.

No GitHub Actions expression engine or new self-hosted Windows run was executed. Historical Release/Debug successes validate their pinned older workflow sources, not this new upload condition. Actual conditional artifact publication remains unobserved. No new Build.log or DLL artifact is claimed.

Use this exact current workflow for the next otherwise warranted complete pinned-base/feature overlay. A repeated DLL build solely for this artifact condition is not required while other source coverage remains open. The review/ledger commit uses [skip ci].
