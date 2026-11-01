# Assertion build artifact verification — 2026-10-31

This follow-up closes the explicit artifact-download gap in the changed SidSaysDiscoveryBuild-ChatGPT head 0b5a7dc869a5f7e2967ac073ca42071dbe707dd7. The new automatic-debugging implementation and its original report were read before work. Current 75-branch inventory differs from the preceding global ledger 5012475e85a727dd0417bbb1249fe845a3b9d321 only in the last preference report and this changed assertion-debugging branch.

No production correction or rebuild was needed. The scope is changed-code review and independent verification of the existing current build, not a repeat of an unrelated historical result.

## Exact input and observed run

- Original SidSaysPatch: read-only 8c52c7e7b85cb574ee0494611a8931efb3b20d01.
- Read-only baseline 1.14: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
- Selected assistant source: cefc020169ab8ac8938c58b5580ce97829c6fd58.
- Actual workflow source: dll-build f77f8a67cd17fdfa9d1c3f443d49005cee04421e.
- Exact tested commit: 26692191a21c50317245db3191ce7d4b47c2644d.
- Observed completed-success run: https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797.
- Release job124676200129 and Debug job124676200037 are both terminal success. Freshly retrieved actual probe output in each confirms _MSC_VER == 1310 (MSVC 7.1).

Complete-tree checks find no missing baseline files, 362 DLL blobs and changes relative to the baseline only in FAssert.cpp and the previously reviewed SelfMod.cpp/.h. SelfMod files are unchanged from the prior assistant head 507912e1f5bc2002b876789bc02d62eff6c0ac05. Every current-head DLL blob matches the exact tested commit. Workflow text matches f77f8a67cd17fdfa9d1c3f443d49005cee04421e after normalizing only its three pinned inputs.

## Actual downloaded artifacts

All four ZIP archives were downloaded and extracted. Their exact byte sizes and SHA256 archive digests match GitHub's artifact metadata.

| Configuration | DLL/log ZIP | ZIP bytes | Source diagnostics ZIP | ZIP bytes |
| --- | ---: | ---: | ---: | ---: |
| Release | 13059718649 | 2,349,259 | 13060142718 | 31,077 |
| Debug | 13060402551 | 18,577,826 | 13060781543 | 31,076 |

Actual MSBuild Build.log in both binary artifacts reports Build succeeded, 0 Warning(s), 0 Error(s), and explicitly lists FAssert.cpp among compiled translation units. BuildTiming.log was inspected in both; these are the collected MSBuild files, not merely the Actions runner summary.

Expected and actual root source manifests match byte-for-byte in each configuration. Source diff files are empty and verification status is passed. The Release and Debug manifests are identical, containing 349 root .c/.cpp/.h/.inl entries. Independently recomputed digest 1fde96efe70489a820c77f7c2331fa41121a84115f1a80a976320eaebf0fdbfb matches both digest fields in both provenance files.

The tested commit, configuration, compiler, baseline, selected source and workflow pins all match in each provenance file. FAssert.cpp was independently hashed from the actual published current source and matches its manifest entry. This establishes that the inspected new debugger block is the source recorded by this build.

## DLL and matching symbol identity

Both binaries validate as PE32 x86 DLLs.

| Configuration | DLL bytes | DLL SHA256 |
| --- | ---: | --- |
| Release | 6,565,888 | 6fd670557cdbdb367a832b77ebf27cc0b9c3db05d39d072ef6b7638757370f88 |
| Debug | 25,202,688 | 3df668159f209950aa9a958eede217835364875190a1adf88c77dd1124c482da |

The Debug PDB is 70,642,688 bytes, SHA256 b5ec001d2bb9994c57087caa9da6062641d42998965142d6150149d218f205a5.

Presence/nonempty checks alone do not establish that a PDB matches a DLL. The Debug DLL's PE debug directory was parsed to locate its CodeView RSDS record; the PDB's MSF 7 directory and PDB information stream were parsed separately. Both have GUID de264c73-57d6-41a5-8407-ec644e2b7834 and age 1. That verifies the supplied Debug DLL/PDB pairing.

[Verified Debug DLL/PDB artifact](https://github.com/SuperXANA/AdvCiv/actions/runs/41248273797/artifacts/13060402551).

## Changed-code review and limits

FAssert.cpp:175–192 adds the IsDebuggerPresent check and OutputDebugStringA output inside the existing FASSERT_ENABLE && WIN32 scope. Returning true requests the baseline assertion macro's existing breakpoint at the caller. FAssert.h:33–51 checks bIgnoreAlways before entering FAssertDlg. With no debugger attached, the new block falls through to the existing dialog. Null expressions and null/empty messages are guarded for debugger output. No C++ exception-recovery syntax or independent Sid-label invocation is added. No new actionable defect was found in this scoped source review.

The source/compile/artifact checks do not execute BtS, attach a debugger, load symbols into a live session, trigger an assertion, validate breakpoint policy or establish the earlier Sid-label locator's runtime behavior. A matching PDB does not prove that a live debugger has loaded it. These remain runtime work.

This publication adds evidence and updates coverage only, uses [skip ci] and triggers no new DLL run. Original branches, baseline, current workflow and all DLL files remain unchanged. No binary archive, signed download URL, credentials or full Actions runner log is published.


## CvGame discovery follow-up — 2026-11-01

The authorized [CvGame hook integration](sid-game-hook-2026-11-01.md) supersedes earlier no-automatic-invocation statements: discovery now runs once on the first eligible initialized, nonempty-map update after a runtime reset. The read-only locator and automatic assertion debugger remain unchanged. Candidate/UI validation and live game/debugger execution remain untested.
