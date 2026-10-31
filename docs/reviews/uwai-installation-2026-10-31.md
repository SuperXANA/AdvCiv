# UWAI aspect XML installation and registration — 2026-10-31

UWAI-20261031-06 and UWAI-20261031-07. Read-only source LeaderSpecificUWAIAspectWeights d38c565a981984a7c34417a9d9529fec2bcd7165. Existing UWAIWeightsDraft-ChatGPT reused from dafd2bb0294d822a51e3d3dd13c81e9946fae67f after consulting its prior declaration, enum, reporting and native-build reports. Current 75-branch inventory has no new original source heads against the preceding global ledger d9571efb9cfb42f856b4b5a5543b0fda16c07291. This covers new XML installation/loading scope; prior compile findings are not repeated.

[Correction 0e6c8622c4dc219196fa9afd79a5046ca2f811f5](https://github.com/SuperXANA/AdvCiv/commit/0e6c8622c4dc219196fa9afd79a5046ca2f811f5).

## Installation defect

The original feature supplies CIV4WarUtilityAspectAIInfos.xml and its extended CIV4GameInfoSchema.xml under Assets/XML/GameInfos (plural). CvXMLLoadUtility::LoadPreMenuGlobals calls LoadGlobalClassInfo with the directory GameInfo (singular), matching the baseline's installed directory. LoadGlobalClassInfo constructs the actual path from that directory at CvXMLLoadUtilitySet.cpp:1375 in the corrected file; it does not search the plural sibling. Thus the table is absent from the requested installation location, and the baseline schema at the active location lacks the new table declarations.

On the assistant branch, relocate the table and schema to Assets/XML/GameInfo. The plural schema differs from the existing singular schema only by the XANA-tagged tail defining WarUtilityAspectAIInfo, WarUtilityAspectAIInfos and Civ4WarUtilityAspectAIInfos. Replacing the singular schema therefore preserves every prior baseline schema declaration and adds exactly that feature extension. The old plural copies are removed from the assistant tree. The table is byte-for-byte unchanged, including all 29 Type/Description entries, integer weights of 100, comments and the ILL_WIL spelling expected by the actual lookup strings. Its relative x-schema reference now finds the extended schema beside it.

## Registration-order defect

In the supplied CvXMLLoadUtilitySet.cpp, the aspect table is loaded after leader metadata. CvLeaderHeadInfo::read(XML), CvInfo_Civilization.cpp:1093, immediately calls SetVariableListTagPair with GC.getNumWarUtilityAspectAIInfos(). Its copy/cache paths also use that count. At initial leader loading, neither the aspect count nor its global type registrations are ready.

The baseline template CvXMLLoadUtility.h:265–301 explicitly reports an error for zero/nonpositive lengths. An override also requires its key to have been registered before the XML iterator converts it. This is a real dependency, even though the supplied leader XML currently contains no WarAspectWeightModifiers blocks.

Move the existing, otherwise unchanged aspect LoadGlobalClassInfo block to immediately before the leader call: corrected CvXMLLoadUtilitySet.cpp:695–698. Both enclosing XANA markers and all other XANA lines remain in their original order. Existing earlier assistant fixes, independent feature boundaries, C++03 interfaces and weight semantics remain. No exception syntax is introduced.

## Focused verification

Run python3 tests/uwai-install/check.py from the repository root. It reads the actual production loader call and consumer header, resolves the requested XML and relative XDR schema, checks registration precedes leader loading, checks the schema's table/row field declarations, and compares all 29 distinct XML keys and default weights against all 29 consumer lookup strings. It passes.

Two separately applied negative controls fail with the expected diagnostic: move registration back after leaders; remove the XML from the requested installation path. The check uses Python XML parsing and XDR structural inspection, not Microsoft's XDR validator or Civ4's parser. It does not claim in-game metadata initialization.

## Native validation preparation

Complete read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6 plus the corrected feature source 0e6c8622c4dc219196fa9afd79a5046ca2f811f5; tested commit 341124017d7e5374b9948b0198364a4a702c6db2. The existing assistant tree already contains the complete baseline. Tree checks found zero missing baseline files and zero modifications in DLL files outside the original feature's 11 supplied paths; the two additional DLL files belong to this feature. All source paths and earlier assistant corrections are retained.

Actual workflow copied from dll-build f77f8a67cd17fdfa9d1c3f443d49005cee04421e, changed only in its three exact provenance pins. Code-only publication uses [skip ci]; the separate prepared publication triggers Release/Debug. Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41235655264

Both matrix jobs completed successfully in run 41235655264:
- Release job 124638777711; actual MSVC probe output confirms _MSC_VER == 1310.
- Debug job 124638777799; actual MSVC probe output confirms _MSC_VER == 1310.

All four ZIP archives were downloaded and extracted. Actual MSBuild Build.log files report Build succeeded, 0 Warning(s), 0 Error(s), with elapsed times 00:02:28.06 (Release) and 00:02:06.32 (Debug). BuildTiming.log was inspected in both artifacts. Diagnostic companion logs contain no compiler/MSBuild warning/error diagnostics; their nonempty command/status content is not treated as warnings.

| Configuration | DLL/log artifact | Source diagnostics | DLL size | Debug PDB size |
| --- | ---: | ---: | ---: | ---: |
| Release | 13055501284 | 13055371434 | 6,569,984 | — |
| Debug | 13055476742 | 13055331991 | 25,206,784 | 70,618,112 |

Both DLLs verify as PE32 x86 DLLs. SHA256:
- Release: ce2e857e9f055f8f10ed0a99aa82e8ddbe8896c330efbd265abd666f1e29c3b3
- Debug: 1d6b7043f8485e4a08a9db9c2c92f977fcdadf02d5fa53ce2a2f7282dabda42e

Expected and actual 351-file root source manifests match byte-for-byte, their diff files are empty, status is passed, and Release/Debug manifests are identical. Recomputed manifest digest 5fa4c983e354af68549bde211c2c4fe8534a88aa99baa1a69427fdca73c612fa matches every expected/actual provenance digest. The actual edited CvXMLLoadUtilitySet.cpp hash was independently recomputed from the local published source and matched its manifest entry. Exact tested/source/baseline/workflow pins and configurations were verified in both diagnostic artifacts.

This validates compilation/linking of the corrected full overlay, not the unchanged original head or actual XML execution. The XML files are repository installation assets; the workflow's root DLL source hashing does not hash/validate those XML assets. The separate structural check supplies their limited verification.

## Remaining scope

Compilation and source hashes cannot prove that Civ4 successfully loads these XML files. Actual parser/schema/runtime execution, warm and stale leader-info cache behavior, optional/default inheritance, malformed metadata and missing-ID release protection remain unverified. The existing zero leader weight still selects global fallback; this correction does not decide whether explicit zero should disable an aspect. Real XML/game execution and localized reporting remain separate tasks.

No original branch or baseline was changed, no cross-feature merge occurred, and no binaries or full runner logs are committed. The coverage ledger preserves historical native results as historical, with this exact tested commit recorded separately.
