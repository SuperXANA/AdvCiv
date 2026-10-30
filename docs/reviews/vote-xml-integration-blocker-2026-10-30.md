# Vote XML integration blocker — 2026-10-30

VOTE-20261030-06. Source LeaderSpecificVoteActionDiplomacy at 4f2e7c2ea110e7859fbab1bdac32a02a27f5bb30. Existing assistant VoteCounterDraft-ChatGPT at 5b177667e39f6b878d42af0afb3be89979d3c513 reused for documentation; prior code refinements retained. Current 75-branch inventory checked. No original feature source changed; dll-build alone advanced to 5a10c31e398d444d3840c213a017e49994036b7d.

## Blocked integration

CvXMLLoadUtility::LoadPostMenuGlobals, CvGameCoreDLL/CvXMLLoadUtilitySet.cpp:803–807 loads CIV4VoteInfo and then calls GC.getInfo(eLoopLeaderHead).readPass3() for each leader.

CvLeaderHeadInfo::readPass3, CvInfo_Civilization.h:239 and CvInfo_Civilization.cpp:1107–1109 requires CvXMLLoadUtility* and searches VoteDecisionAttitudes under the utility's current node. The caller supplies no argument. A strict C++03 syntax check of the actual declaration and actual call, with only GC/class scaffolding, reproduces: no matching function for call to CvLeaderHeadInfo::readPass3(); candidate expects 1 argument, 0 provided. This is not a full engine or MSVC build result.

Adding this at the call does not provide the missing per-leader XML cursor: the preceding loader is for vote infos, and the loop supplies neither leader document loading nor leader-node selection. It also discards readPass3's bool result. The supplied feature tree contains seven DLL files and README, with no XML schema or example VoteDecisionAttitudes data. There is no supplied routine mapping each leader to its XML node for this later pass. The existing positional reader is insufficient evidence to invent a replacement keyed schema, module/default merging policy or new metadata content.

Record this exact original head as skipped for further integration/native build attempts until user source work supplies the missing XML routing/data. Do not fabricate XML or simply pass a utility at the wrong cursor to obtain a compiler result. Existing counter/reader fixes remain useful isolated drafts and are not rolled back. No production edit can resolve this boundary without adding the currently missing integration. A resumed review must check both cursor selection and failure propagation, then real schema/data loading.

## Additional lifecycle inspection

The three player arrays are initialized/allocated in constructor/AI_reset and deleted in AI_uninit (CvPlayerAI.cpp:92–96,179–183,323–342). Metadata arrays have null initialization, deep-copy and destruction (CvInfo_Civilization.cpp:501–505,541–545,563–567). No new defect is claimed in those inspected blocks.

Baseline CvXMLLoadUtility::InitList at CvXMLLoadUtility.h:502–511 returns immediately for an existing array, preserving defaults. Thus a suspected unconditional allocation leak was ruled out. The older vote-loader fixture's InitList stand-in does not model that path, and repeated loading/default inheritance was already expressly unverified; do not use its 55 fresh-object cases as evidence for that scope.

## Workflow and verification limits

Reviewed exact dll-build delta 6343afabdc57996ea875b6e8541b69ad333d0686 to 5a10c31e398d444d3840c213a017e49994036b7d: only runs-on changed from self-hosted to civ4-dll-build. Future prepared builds must copy the latter workflow. Runner-label availability was not tested by this documentation pass. The current workflow still uploads Build.log on its successful copy path; failure artifacts are not guaranteed because that step is gated on earlier success. For any future triggered run, inspect downloadable artifacts and their actual MSBuild Build.log as requested, state missing artifacts accurately and use runner logs only when needed.

No DLL run triggered; no compiler errors attributed to MSVC; no artifact or gameplay result claimed. Documentation uses [skip ci].
