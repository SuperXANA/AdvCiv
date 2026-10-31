# Automatic assertion debugging — 2026-10-31

## Scope

Implemented an automatic Debug-button path in `SidSaysDiscoveryBuild-ChatGPT`. No branch named exactly `SidSaysDiscovery` existed at the request-time inventory; the existing isolated build branch is the current discovery implementation.

The only DLL-source change is an 18-line XANA-marked insertion in `CvGameCoreDLL/FAssert.cpp`, after `g_AssertInfo.line = line` and before `DisplayAssertDialog()`. When `IsDebuggerPresent()` is true, it sends the failed expression and any nonempty message through `OutputDebugStringA` and returns true. `FAssert` / `FAssertMsg` then execute their existing breakpoint at the assertion call site. No additional breakpoint is introduced in the handler.

The block is within the existing `FASSERT_ENABLE && WIN32` guard. Without an attached debugger, control reaches the original dialog. The existing ignore state and dialog choices are unchanged. Assertions must be enabled; the Debug build defines `FASSERT_ENABLE` through `_DEBUG`.

## Provenance

- Original isolated branch head: `507912e1f5bc2002b876789bc02d62eff6c0ac05`.
- Read-only AdvCiv 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
- Existing SidSaysPatch source: `8c52c7e7b85cb574ee0494611a8931efb3b20d01`.
- Assertion source commit: `cefc020169ab8ac8938c58b5580ce97829c6fd58`.
- Workflow source: `dll-build` at `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`.
- Full build commit: `26692191a21c50317245db3191ce7d4b47c2644d`.
- Build run: [41248273797](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797).

Every baseline file remains present. The pre-existing `SelfMod.cpp` / `SelfMod.h` discovery implementation is retained byte-for-byte. Removing the new marked block restores the previous `FAssert.cpp` byte-for-byte, and published/local Git blob hashes match. The build commit changes only `FAssert.cpp` and the isolated branch's workflow. The current workflow was copied from the named workflow source with only its three provenance placeholders replaced by pinned commit SHAs.

The workflow serializes shared-workspace builds, verifies root-source SHA-256 hashes after transfer, preserves the VM's machine-local Project configuration, clears stale build outputs/logs, probes `_MSC_VER == 1310`, and rebuilds Release and Debug. Release and Debug results are recorded below.

## Remote game use

Install the new Debug DLL into the mod and load its matching PDB in the CDB/WinDbg session. When CDB launches or attaches to BtS, a failed enabled assertion sends text to that debugger and requests the normal assertion breakpoint automatically. The debugger's exception handling determines whether it stops at that breakpoint.

Native compilation and linking do not establish live-game behavior. Live debugger attachment, symbol loading, and assertion handling in BtS were not exercised. The earlier Sid-label diagnostic limitations remain: no UI renaming or automatic invocation of that locator is introduced.

## Native validation result

The full build at `26692191a21c50317245db3191ce7d4b47c2644d` completed successfully in [run 41248273797](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797). Both job logs confirm `_MSC_VER == 1310` and zero warnings/errors; FAssert.cpp appears in each compilation log. Source-verification, artifact upload, and cleanup steps passed.

| Configuration | Job | Warnings / errors | Artifact |
| --- | --- | --- | --- |
| Release | [124676200129](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797/job/124676200129) | 0 / 0 | [13059718649](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797/artifacts/13059718649), 2,349,259 bytes |
| Debug | [124676200037](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797/job/124676200037) | 0 / 0 | [13060402551](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797/artifacts/13060402551), 18,577,826 bytes |

The Debug artifact includes the compiled DLL and matching PDB; the copy step requires both files to exist and be nonempty. At initial publication, binary archives had not been independently downloaded or run. A documentation/coverage follow-up does not change the tested source or retrigger the DLL build.


## Artifact verification follow-up

The independent [artifact verification report](assertion-artifacts-2026-10-31.md) closes the initial download gap: all four ZIPs, actual MSBuild logs, source manifests/provenance, x86 binaries and matching Debug DLL/PDB identity were checked. Live-game/debugger execution remains untested. No DLL source or workflow was changed by this follow-up.
