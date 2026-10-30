# Hated diplomacy native validation — 2026-10-30

Read-only original a9c1a754b5e9b64e10ceaa22fd02fa78f3718785; baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6; workflow dll-build af5c2f130e195c23a011a5aed35fcff212389f2e. Existing HatedDiplomacyDraft-ChatGPT reused. Complete baseline plus all 11 source DLL files and existing reports/tests retained; 349 root source files. No original branches modified or merged.

First tested overlay bf6a52508ea56ead4393276271abba5d1aa48cbd; run https://github.com/SuperXANA/AdvCiv/actions/runs/41125771533. Both Release job 124303777200 and Debug job 124303776712 failed compiling CvPlayerAI.cpp. Zero artifacts, so no artifact Build.log existed to download; targeted decoded runner compiler diagnostics were inspected instead.

Repairs committed in e3887b18825dc14d026a0d8fb5f7a6b58a5c7484:
- HATED-20261030-04: AI_religionTrade:13491 and AI_updateStrategyHash:25647 replace nonexistent player isHasReligion with getHasReligionCount(religion)>0. Actual CvPlayer.h:415–417 uses precisely this presence predicate in canDoReligion. City isHasReligion calls are valid and untouched. Initial errors C2039/C3861.
- HATED-20261030-05: AI_ideologyAttitudeChange:19041–19061 scopes ENEMY_RELIGION/ENEMY_CIVIC declarations inside braces so later case labels cannot skip initialization. Initial error C2360.
- HATED-20261030-06: AI_updateStrategyHash:25777–25800 uses eCivic for the hated-civic membership check instead of out-of-scope eReligion, and itRival->isCivic / itRival->getStateReligion. Initial C2065/C2039. Existing +10 paranoia values/iteration remain unchanged.

First-run exact compiler error locations: 13491 C2039; 19050/19059/19066/19074 C2360; 25643 C3861; 25775 C2065; 25780/25793 C2039; consequent NMAKE U1077. No CvPlot size-limit failure observed.

Corrected matrix prepared using feature snapshot e3887b18825dc14d026a0d8fb5f7a6b58a5c7484; provenance placeholders filled with exact baseline/feature/workflow. Result pending. No success/artifact claimed yet. Compile/link validation does not certify save/cache layout, game strategy behavior or actual XML/UI.
