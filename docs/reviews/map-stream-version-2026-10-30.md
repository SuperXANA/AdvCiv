# Temporary plot map stream version — 2026-10-30

PLOTTIMER-20261030-06. Read-only source LeaderCivilizationVariantMechanics at 39edf4ca659e806b6fb4bb2de4ab280756829a99; reused PlotTimerDraft-ChatGPT parent 811dc16daa7766051f540422f63830f2196e4038. Current 75 branches inventoried. No original feature changed; dll-build advanced from 5a10c31e398d444d3840c213a017e49994036b7d to af5c2f130e195c23a011a5aed35fcff212389f2e. Baseline remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Committed correction

CvMap::read, CvGameCoreDLL/CvMap.cpp:1339–1342: gate m_pTempChangesMap->read on uiFlag >= 8. CvMap::write:1354–1359: retain the version-7 history comment and emit version 8 for the appended temporary-map payload. Existing write tail is unchanged except for shifted line numbers. XANA tag/date markers retained and enclose the new version assignment.

Actual baseline CvMap.cpp:1331 emits version 7 and contains no temporary-map payload. The feature's prior writer also emitted version 7 but appended 17 enum maps. Its reader consumed those maps unconditionally, including baseline saves with no such data: the next serialized object could be interpreted as temporary-map contents. The existing reset allocation constructs empty temporary storage before reading, so legacy versions need no additional payload read.

This is a format discriminator for new saves, not an automatic migration of the branch's already-written unversioned feature saves. Old feature-version-7 saves and baseline-version-7 saves share their flag while differing in layout; there is no reliable discriminator in the supplied format. This refinement treats versions <=7 as baseline layouts. Such unversioned feature saves require an explicitly identified external conversion or matching old reader; they are not supported here. No heuristic consumes following object bytes. Baseline DLL readers are not forward-compatible readers for the new version-8 payload.

## Verification and limits

tests/map-lifecycle/version-check.cpp embeds the actual revised flag assignment/read-tail guard/write-tail call and complete actual PlotTempChangeMap inline read/write bodies. A bounded word-stream stand-in and 17 individual map stand-ins expose order and boundary errors; they are not engine FDataStreamBase or ArrayEnumMap.

24 cases passed g++ -std=c++03 -Wall -Wextra -Werror -pedantic, ASan and UBSan: each legacy version 0–7 consumes no payload words, followed by 16 distinct version-8 payload patterns checking all 17 channels and a following sentinel. Original read/write snippets fail the legacy cursor assertion (negative control suppresses only the unused uiFlag warning introduced by the wrapper). Leak detection disabled as unsupported. The earlier reset/turn/component fixtures remain scoped evidence, not whole-map compilation.

No MSVC7.1, real-save, full DLL or game result. Partial draft uses [skip ci]. Remaining: complete legacy map layouts, enum-map encoding/metadata changes, restoration edge policies, whole-feature XML/player/yield integration and native validation. No other branch was integrated or modified.

## Workflow inventory

The inspected latest dll-build delta replaces wildcard Debug PDB copying/upload with the exact CvGameCoreDLL.pdb filename. The runner label remains civ4-dll-build. Record af5c2f130e195c23a011a5aed35fcff212389f2e as the current workflow source; no build was triggered to exercise that artifact-path change.
