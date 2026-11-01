# CvGame-controlled Sid attribution discovery — 2026-11-01

## Scope and pins

User source: SidSaysPatch `3171a91bd8b595781f624d94ee14d3f2552ac9e7`, compared with prior reviewed source `8c52c7e7b85cb574ee0494611a8931efb3b20d01`. Assistant parent: SidSaysDiscoveryBuild-ChatGPT `d307c2ba103c8d53d23a668c218fd66cc464dafa`. Baseline: 1.14 `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Actual build workflow: dll-build `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`.

Only the assistant branch was changed. The user source adds CvGame.cpp/h; its unmarked CvGame.cpp content matches the pinned baseline/assistant parent. Its older SelfMod blind-write code was not overlaid onto the existing read-only diagnostic locator. Existing automatic assertion debugging in FAssert.cpp and the locator body were preserved byte-for-byte against the assistant parent.

## SID-20261101-01 — preserve CvGame layout while adding the hook

At user source CvGame.h, the new m_bSidSaysPatchTestDone follows an existing contiguous block of 16 bool members, before HandicapTypes m_eHandicap. Adding a seventeenth bool pushes the following four-byte fields by four bytes under the target layout. This is unnecessary ABI movement in an executable-facing object.

The assistant refinement retains the original CvGame members and keeps discovery-attempt state in DLL-owned smc::Civ4BeyondSwordPatches (SelfMod.h:19–20,26,34). The user's enclosing XANA markers and inline notes remain. CvGame.cpp:629–632 resets the attempt only on runtime reset (!bConstructorCall); the SelfMod constructor initializes first use. CvGame::read calls reset, so loading another game allows a new attempt without adding a serialized field.

CvGame::update at CvGame.cpp:2871–2879 invokes the existing diagnostic entry after updateUnprofiled, gated by isFinalInitialized(), a nonempty map, and an unused attempt. This implements the requested game-controlled evaluation point. Readiness here is a scheduling gate; it does not prove a literal is the active UI string.

SelfMod.cpp:658–673 claims the attempt before scanning or showing UI, preventing recursive update callbacks from repeating the scan. DISABLE_EXE_RUNTIME_MODS is honored. An attempted call consumes the attempt even when disabled or when discovery fails; another runtime reset permits another attempt. The existing patch-success flag remains false.

Source links for the committed correction: [CvGame reset](https://github.com/SuperXANA/AdvCiv/blob/a994b2ed9db89aac098b2b0a640146e7688a017f/CvGameCoreDLL/CvGame.cpp#L629), [update hook](https://github.com/SuperXANA/AdvCiv/blob/a994b2ed9db89aac098b2b0a640146e7688a017f/CvGameCoreDLL/CvGame.cpp#L2871), [unchanged CvGame member layout](https://github.com/SuperXANA/AdvCiv/blob/a994b2ed9db89aac098b2b0a640146e7688a017f/CvGameCoreDLL/CvGame.h#L1063), [attempt state](https://github.com/SuperXANA/AdvCiv/blob/a994b2ed9db89aac098b2b0a640146e7688a017f/CvGameCoreDLL/SelfMod.h#L17), [guarded diagnostic entry](https://github.com/SuperXANA/AdvCiv/blob/a994b2ed9db89aac098b2b0a640146e7688a017f/CvGameCoreDLL/SelfMod.cpp#L658). Initial integration: [16682e7](https://github.com/SuperXANA/AdvCiv/commit/16682e75237ca7bc1e93eb555ea7a6b4d8a8febb); constructor-reset refinement: [a994b2e](https://github.com/SuperXANA/AdvCiv/commit/a994b2ed9db89aac098b2b0a640146e7688a017f).

## Verification and limits

Focused scheduling harness: 33 readiness/map/disable/module-failure/reset/reentry configurations, including 100 repeated frames per case, later transition to readiness, constructor reset preserving an existing attempt, and runtime reset permitting another pass. Removing the readiness gate is detected by a negative control. The original locator and entry harness passes C++03, -fno-exceptions, ASan/UBSan, malformed PE/unreadable-memory checks and image-byte preservation. These are targeted modeled checks, separate from full native DLL validation.

The complete 362-blob baseline DLL tree is retained. Only CvGame.cpp, CvGame.h, FAssert.cpp, SelfMod.cpp and SelfMod.h differ from baseline; FAssert.cpp is unchanged from the assistant parent. The final prepared tree uses the actual pinned workflow with only its three source pins changed.

Final tested commit: [770e9e4f0984f3099b7eaa8c261bbaa51a1e0756](https://github.com/SuperXANA/AdvCiv/commit/770e9e4f0984f3099b7eaa8c261bbaa51a1e0756), selecting corrected source `a994b2ed9db89aac098b2b0a640146e7688a017f`. [Final run 41255403884](https://github.com/SuperXANA/AdvCiv/actions/runs/41255403884) succeeded in both configurations. Both job logs confirm the selected compiler is _MSC_VER == 1310 (MSVC 7.1).

| Configuration | Actual Build.log | Verified DLL artifact | Source-hash diagnostics |
| --- | --- | --- | --- |
| Release | 0 warnings, 0 errors | [13063650159](https://github.com/SuperXANA/AdvCiv/actions/runs/41255403884/artifacts/13063650159) | 13063370685 |
| Debug | 0 warnings, 0 errors | [13063140677](https://github.com/SuperXANA/AdvCiv/actions/runs/41255403884/artifacts/13063140677), including matching PDB | 13063575086 |

All four final ZIPs were downloaded, archive byte sizes/SHA-256 checked against GitHub metadata, and extracted. Actual MSBuild Build.log and BuildTiming.log were accessed. Both 349-file actual-source manifests exactly equal expected-source manifests, with empty hash diffs, passed status and exact baseline/source/workflow/commit/configuration pins. The five final modified-baseline source files were independently hashed against the manifests. Both DLLs are PE32 x86 DLLs. The Debug DLL CodeView RSDS identity matches the PDB: `b975ad0b-b5a4-4b25-a0a4-b538a06f51de`, age 1. DLL/PDB hashes, sizes, manifest hashes and timing records are recorded in [machine-readable evidence](sid-game-hook-2026-11-01.json).

The initial integration was also fully followed: tested `933107cb6fb9edd6005b6aeb9e95db6f1c910316`, selected source `16682e75237ca7bc1e93eb555ea7a6b4d8a8febb`, [run 41255085515](https://github.com/SuperXANA/AdvCiv/actions/runs/41255085515). Release and Debug passed with 0 warnings/errors; all four ZIPs, actual logs, manifests, pins, binaries and matching Debug symbols were independently verified. The final run above supersedes it for installation.

This remains discovery-only: it writes no executable bytes and does not rename the displayed attribution. SidSaysCandidates.log records unverified EXE literal candidates and the discovery summary. The existing Release information message says that no strings changed; Debug suppresses that message through the existing FASSERT_ENABLE path. No live BtS run, candidate/UI attribution validation, debugger attachment, or scan-pause measurement was performed. The existing PE/image/section bounds and 128 logged-candidate cap remain unchanged; the cap bounds logged candidates, not scan duration. The synchronous scan occurs on the first eligible update after each runtime reset, so a live session is still needed to assess timing.

The earlier reports' statement that discovery has no automatic invocation is historical and superseded by this authorized CvGame hook. Their restrictions against treating candidate addresses as verified UI sites remain applicable.
