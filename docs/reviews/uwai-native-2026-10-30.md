# UWAI leader-weight metadata and native validation — 2026-10-30

UWAI-20261030-04/05. Original LeaderSpecificUWAIAspectWeights d38c565a981984a7c34417a9d9529fec2bcd7165 unchanged; reused UWAIWeightsDraft-ChatGPT parent 86358f64e315b76323bb351840521821fd7e6b69. Complete 75-branch inventory found no changed original heads against latest global ledger 484ab0fca026c3b11e8975cb6c71499a2a8b685d.

UWAI-04: CvInfo_Civilization.h:346 declares m_prWarUtilityAspects as scaled*, inconsistent with CvLeaderHeadInfo::read cache allocation new int[...] at CvInfo_Civilization.cpp:815, integer cache stream payload, supplied iWeightModifier XML int schema, and getWarUtilityAspect:661–664 applying per100. Change the pointer to int* so constructor/copy/destructor/cache/XML/getter agree on stored integer percentages. Existing member name preserved; public getter still returns scaled. No weight or zero-override policy changed.

UWAI-05: CvLeaderHeadInfo::read(XML), CvInfo_Civilization.cpp:1093, calls nonexistent SetVariableTagListPair. Use actual baseline SetVariableListTagPair declared in CvXMLLoadUtility.h:265. Preserve source tag WarAspectWeightModifiers and count.

Scoped source correction committed as 5b31c0e22761d051eb9cdbf9dbe65d6e43ee5ff0. Existing earlier class declaration, enum ID and reporting fixes retained.

Prepared full native validation from complete read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6 with all 11 feature DLL files overlaid, retaining baseline-only files and all existing assistant XML/reports/tests. Actual workflow copied from dll-build 9f62e13990b39a8c16e8c6dd404c6aca995e53f3 with three provenance SHA inputs filled. Original branches remain unchanged. ## Native result

Tested commit 9c77b56688d500212386e272c563d43441232551; run https://github.com/SuperXANA/AdvCiv/actions/runs/41133624805 completed successfully:
- Release job 124330537055: success.
- Debug job 124330536704: success.
Both observed toolset probes report _MSC_VER == 1310 (MSVC 7.1). Actual full Rebuild compiled and linked the complete overlay. No additional compiler fixes were needed after the metadata corrections above.

All four artifact ZIPs downloaded and extracted:

| Configuration | Source verification | Compiled DLL |
| --- | --- | --- |
| Release | 13014576550 (31,259 bytes) | 13013624606 (2,349,725 bytes) |
| Debug | 13014881177 (31,258 bytes) | 13013794777 (18,570,083 bytes) |

Both actual Build.log files report Build succeeded, 0 Warning(s), 0 Error(s). Binary headers verify PE32 x86 DLLs:
- Release DLL: 6,569,984 bytes; SHA256 a8fa30d27fa96c1e5d088cdb03c5236a37bc53db2020a44d98e5bf97c055847c.
- Debug DLL: 25,206,784 bytes; SHA256 94aef4ec8de46e2dad1bda8bbe0bdbdfa03768a0b14894bb2f4792ceb7004e20.
- Debug PDB present: 70,618,112 bytes.

Expected/actual source manifests match byte-for-byte in both configurations, and the Release/Debug manifests are identical. All have 351 root source entries, explicitly including WarUtilityAspectAI.cpp/.h. Source diffs empty and verification status passed. Recomputed manifest SHA256 4a01e5f4e39e66b296b33e6ce305002c4f4073543f095395a3a8cbc5ad32cf65 equals both digest fields in each provenance file. Exact tested commit, configuration, compiler, baseline, feature snapshot 5b31c0e22761d051eb9cdbf9dbe65d6e43ee5ff0 and workflow 9f62e13990b39a8c16e8c6dd404c6aca995e53f3 verified.

This is a result for the corrected isolated overlay, not the unchanged original head. Previous class/enum/reporting fixtures remain separate evidence. No binary artifacts or complete runner logs committed to source control.

## Verification limits

Metadata class/consumer compilation now verified, but actual XML parser/installation behavior and engine execution are not. Native builds do not validate save/cache migration, invalid-ID runtime safety, localized report conversion or weighting design. The leader getter still applies per100 once to stored int percentages; existing zero values still select the global fallback in WarUtilityAspect::evaluate. No change to that policy is claimed.

Evidence-only follow-up uses [skip ci] and leaves tested DLL files/workflow unchanged.

Runtime XML installation, full schema/loading/cache compatibility, zero override policy, missing-ID release safety and game behavior remain unverified.
