# Hated diplomacy native validation — 2026-10-30

Read-only original a9c1a754b5e9b64e10ceaa22fd02fa78f3718785; baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6; workflow dll-build af5c2f130e195c23a011a5aed35fcff212389f2e. Existing HatedDiplomacyDraft-ChatGPT reused. Complete baseline plus all 11 source DLL files and existing reports/tests retained; 349 root source files. No original branches modified or merged.

First tested overlay bf6a52508ea56ead4393276271abba5d1aa48cbd; run https://github.com/SuperXANA/AdvCiv/actions/runs/41125771533. Both Release job 124303777200 and Debug job 124303776712 failed compiling CvPlayerAI.cpp. Zero artifacts, so no artifact Build.log existed to download; targeted decoded runner compiler diagnostics were inspected instead.

Repairs committed in e3887b18825dc14d026a0d8fb5f7a6b58a5c7484:
- HATED-20261030-04: AI_religionTrade:13491 and AI_updateStrategyHash:25647 replace nonexistent player isHasReligion with getHasReligionCount(religion)>0. Actual CvPlayer.h:415–417 uses precisely this presence predicate in canDoReligion. City isHasReligion calls are valid and untouched. Initial errors C2039/C3861.
- HATED-20261030-05: AI_ideologyAttitudeChange:19041–19061 scopes ENEMY_RELIGION/ENEMY_CIVIC declarations inside braces so later case labels cannot skip initialization. Initial error C2360.
- HATED-20261030-06: AI_updateStrategyHash:25777–25800 uses eCivic for the hated-civic membership check instead of out-of-scope eReligion, and itRival->isCivic / itRival->getStateReligion. Initial C2065/C2039. Existing +10 paranoia values/iteration remain unchanged.

First-run exact compiler error locations: 13491 C2039; 19050/19059/19066/19074 C2360; 25643 C3861; 25775 C2065; 25780/25793 C2039; consequent NMAKE U1077. No CvPlot size-limit failure observed.

## Corrected native result

Tested commit 2f37cbcc50427fbf0b81a4c8e6a30270f5af35cd, source snapshot e3887b18825dc14d026a0d8fb5f7a6b58a5c7484. Successful run https://github.com/SuperXANA/AdvCiv/actions/runs/41126096699 completed both configurations:
- Release job 124304904569; artifact 13011635160, ZIP 2,352,514 bytes.
- Debug job 124304905149; artifact 13009659769, ZIP 18,555,397 bytes.

Both artifacts were downloaded as ZIPs and extracted. Their actual Build.log files each report Rebuild succeeded, 0 Warning(s), 0 Error(s). Both runner toolset probes report _MSC_VER == 1310 (MSVC 7.1), independently of the filled provenance text. Each archive's provenance matches exact tested commit, configuration, compiler, base, source snapshot and workflow. actual-sources.txt equals expected-sources.txt, 349 root source files per configuration.

Verified both binaries have MZ/PE headers, x86 machine 0x14c, PE32 optional header 0x10b and DLL characteristics:
- Release DLL 6,565,888 bytes, SHA256 076e84bf641539fc2d58da2c1562d2f6334cdb0a8fddea03f0522c6bd2e4d993.
- Debug DLL 25,186,304 bytes, SHA256 5c5d52ae41b39e7b31a062b0ce12e6aaf7e18337b9ea35ac2caab0c2a7e861c1. Debug PDB also present, 70,585,344 bytes.

No binary artifacts or full runner logs committed to the source repository. This evidence-report update uses [skip ci] and leaves tested production sources/workflow unchanged.

## Verification limits

The corrected isolated overlay compiled and linked; the unchanged original head did not receive a successful build claim. Native validation does not certify save/cache layout compatibility, religion/paranoia scoring policy, event/turn execution, actual game XML/UI or multiplayer behavior. Prior scoped fixtures remain separate evidence. User save version 22 and cache format migration require further review; no format or mechanics were invented merely to build.
