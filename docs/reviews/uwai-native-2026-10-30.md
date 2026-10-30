# UWAI leader-weight metadata and native validation — 2026-10-30

UWAI-20261030-04/05. Original LeaderSpecificUWAIAspectWeights d38c565a981984a7c34417a9d9529fec2bcd7165 unchanged; reused UWAIWeightsDraft-ChatGPT parent 86358f64e315b76323bb351840521821fd7e6b69. Complete 75-branch inventory found no changed original heads against latest global ledger 484ab0fca026c3b11e8975cb6c71499a2a8b685d.

UWAI-04: CvInfo_Civilization.h:346 declares m_prWarUtilityAspects as scaled*, inconsistent with CvLeaderHeadInfo::read cache allocation new int[...] at CvInfo_Civilization.cpp:815, integer cache stream payload, supplied iWeightModifier XML int schema, and getWarUtilityAspect:661–664 applying per100. Change the pointer to int* so constructor/copy/destructor/cache/XML/getter agree on stored integer percentages. Existing member name preserved; public getter still returns scaled. No weight or zero-override policy changed.

UWAI-05: CvLeaderHeadInfo::read(XML), CvInfo_Civilization.cpp:1093, calls nonexistent SetVariableTagListPair. Use actual baseline SetVariableListTagPair declared in CvXMLLoadUtility.h:265. Preserve source tag WarAspectWeightModifiers and count.

Scoped source correction committed as 5b31c0e22761d051eb9cdbf9dbe65d6e43ee5ff0. Existing earlier class declaration, enum ID and reporting fixes retained.

Prepared full native validation from complete read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6 with all 11 feature DLL files overlaid, retaining baseline-only files and all existing assistant XML/reports/tests. Actual workflow copied from dll-build 9f62e13990b39a8c16e8c6dd404c6aca995e53f3 with three provenance SHA inputs filled. Original branches remain unchanged. Release/Debug native result pending; previous standalone fixtures are not a full build claim.

Runtime XML installation, full schema/loading/cache compatibility, zero override policy, missing-ID release safety and game behavior remain unverified.
