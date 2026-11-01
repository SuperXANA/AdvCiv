# Gender baseline header preparation — 2026-11-01

GENDER-PREP-20261101-11. Source GenderSpecificDiplomacy `80e6ec595041cf335d5437b7bedea4fcaa61622b`; assistant parent `1a97f9043f49ed3a4801b82b9eada126e9accef9`; read-only baseline `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Correction: `82eac4821fc90dcbb067dd7e1006cdfb72cad045`.

Compared all six supplied assistant headers against actual pinned baseline: CvEnumMacros.h, CvGameTextMgr.h, CvInfo_Civilization.h, CvPlayer.h, CvPlayerAI.h and CyPlayer.h. The enum extension/alias, gender query/declaration/storage additions and ideology marker extension are retained. Five headers have only feature-related differences.

CvPlayer.h:1651–1652 also carried unmarked differences: m_aiHasReligionCount and m_aiHasCorporationCount used ArrayEnumMap<...,int,char> while current baseline uses short. These are unrelated religion/corporation city-count containers; carrying the narrower encoding into the feature reduces their representable count range. They are not part of the enclosing Gender additions. Restore the two exact baseline declarations rather than attribute the drift to a new Gender mechanic.

Verified exactly two changed member-declaration lines and identical XANA marker lines/order before/after. Both revised declarations exactly match pinned baseline. No new behavioral test is added for this direct baseline restoration. No claim about actual engine count or save execution is made.

This is a header-reconciliation checkpoint, not a complete build overlay. The eight implementation files (CvGameTextMgr.cpp, CvInfo_Civilization.cpp, CvPlayer.cpp, CvPlayerAI.cpp, CvXMLLoadUtilitySet.cpp, CyInfoInterface3.cpp, CyPlayer.cpp and UWAI.cpp) still need comparison/reconciliation of unmarked older upstream copies while preserving marked user and newer assistant edits. Complete baseline-only files and the current pinned workflow must be added before publishing a build-triggering commit.

No DLL run triggered; no MSVC7.1/build/artifact result. This sparse preparation uses [skip ci]. Prior Gender info alias/counter/UI/save repairs remain. No original branch or baseline edit, feature merge, PR or force push.

## Completed native follow-up

The complete reconciled overlay `5b122549e6df54bc61bcfbb19b7482cc9bec756e` subsequently passed Release and Debug MSVC7.1 with zero warnings/errors in run 41328157020. All four archives, actual MSBuild logs, source hashes/provenance and DLL/PDB identity were verified. See [gender-native-2026-11-01.md](gender-native-2026-11-01.md) for the exact scope and runtime limits. The pending preparation/build statements above describe this earlier checkpoint.
