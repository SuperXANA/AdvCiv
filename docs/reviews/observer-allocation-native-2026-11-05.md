# Observer allocation correction — November 5, 2026

OBS-POLICY-20261104-01 is fixed on ObserverMCP-ChatGPT. [Code commit 0574f4962f28ee02bc5ee9975bda36d45b84827c](https://github.com/SuperXANA/AdvCiv/commit/0574f4962f28ee02bc5ee9975bda36d45b84827c) changes CvObserver.cpp, start(), lines 71–86: use std::nothrow, test NULL, assert/log and return; preserve deletion/nulling when transport start() fails. The explicit try/catch (...) block is removed. Existing XANA annotations and newer receiver/smoke tooling remain.

The previous review draft is superseded by this applied correction. No CriticalSection wrapper or Win32 initialization semantics were changed; the null guard addresses allocation failure, not a claim that every OS resource failure is now tested or recoverable. No allocation-failure injection or actual game execution was performed.

## Pinned native validation

- Tested commit: 33d1ee1d4ffccb0e012487027a8cd67bc831fea7
- Selected corrected source: 0574f4962f28ee02bc5ee9975bda36d45b84827c
- Complete baseline: 5970334b64a875b5cdb370c94fc9a98db4eacda6; all 872 baseline blobs have retained paths, 372 DLL blobs.
- Workflow source: cf9b2a7fe6b9be2581f46a67a84944c35536d046. Its only new source delta reduces actions permission to read; adopted in the existing observer four-job matrix and native-test adaptation.
- [Run 42155681291](https://github.com/SuperXANA/AdvCiv/actions/runs/42155681291): completed successfully.

| Configuration / gate | Warnings / errors | Windows standalone observer tests | DLL/log artifact | Source diagnostics |
| --- | --- | --- | --- | --- |
| Release-disabled | 0 / 0 | Disabled | [13475080921](https://github.com/SuperXANA/AdvCiv/actions/runs/42155681291/artifacts/13475080921) | 13475375280 |
| Debug-enabled | 0 / 0 | Passed | [13474692965](https://github.com/SuperXANA/AdvCiv/actions/runs/42155681291/artifacts/13474692965) | 13474892449 |
| Release-enabled | 0 / 0 | Passed | [13474348057](https://github.com/SuperXANA/AdvCiv/actions/runs/42155681291/artifacts/13474348057) | 13474397866 |
| Debug-disabled | 0 / 0 | Disabled | [13474184414](https://github.com/SuperXANA/AdvCiv/actions/runs/42155681291/artifacts/13474184414) | 13474049826 |

All eight ZIPs were downloaded, checked against API size/SHA256, extracted, and every extracted member compared with its archive bytes. Actual MSBuild Build.log and BuildTiming.log were inspected in all four binary artifacts. Both enabled ObserverTests.log files contain PASS for snapshot/JSON/queue/concurrency/Windows loopback/disconnect/shutdown.

All four expected/actual 361-entry source/test manifests match with empty hash differences and exact tested/source/baseline/workflow/configuration pins, _MSC_VER_1310 provenance, and tested-tree source names. Twelve observer source/test files were independently checked against Git blob SHA1 and native SHA256, accounting for the workflow's enabled config-header transformation. All four DLLs are PE32 x86; both Debug PDB GUID/age records match their DLLs. Disabled Debug/Release manifests share digest ffe441c721febfd4d80e384b22bff4b1a530404eb266df74083bd7ab92bf14c5; enabled manifests share c9134c072f9e9b6891a56219a16b64a5d69027484b9fd5802ce5df807cb65286.

Full binary hashes, PDB identities, timing and artifact IDs are retained in [machine-readable evidence](observer-allocation-native-2026-11-05.json).

Actual Civ4 observations, callback threading, fresh-game several-turn save/reload, runtime VM SSH forwarding and normal game exit remain unverified. The enabled standalone suites validate a narrower Windows harness and do not certify the game bridge's allocation-failure branch.
