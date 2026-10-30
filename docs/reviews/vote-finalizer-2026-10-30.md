# Vote staging finalizer — 2026-10-30

Reviewed original LeaderSpecificVoteActionDiplomacy at 8fcfdd97329279393120aaab34c00dde84e729df; assistant parent 6c0caf2d993dfacab2778258f47241fd74dd1f03. All 75 branch heads refreshed, with no new original-head delta against the latest ledger. Existing VoteCounterDraft-ChatGPT reused; baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6 and user source remain untouched. Prior copy/counter refinements retained.

## Completed

VOTE-20261030-08 — CvLeaderHeadInfo::readPass3, CvGameCoreDLL/CvInfo_Civilization.cpp:1150–1212.
Complete the supplied no-argument second stage using GC.getNumVoteInfos(), available at the current post-vote load call. No CvXMLLoadUtility pointer is needed for ordinary new[] allocation. The old scaffold used undefined iNumPlayerVotes, had array initialization commented out before writes, and sent fixed negative ballot strings through the unrelated XML-info ID registry.

Validate nonnegative vote capacity, staged row capacity and both numeric vector lengths before indexing. Resolve only PLAYER_VOTE_YES, PLAYER_VOTE_NO, PLAYER_VOTE_ABSTAIN and PLAYER_VOTE_NEVER by exact string comparisons, preserving the established ballot domain. Reject other strings, including valid unrelated XML types, with assertion and false. Resolve every row before any destination write/allocation. Empty stage is a successful no-op retaining inherited or null defaults. Allocate missing arrays to full vote capacity and initialize decision/attitude defaults to NO_PLAYER_VOTE/0; preserve already allocated inherited arrays as baseline InitList does. Apply positional rows and clear staging on success. Validation failures preserve staged data and destination arrays for diagnosis.

This keeps the supplied positional format and existing four supported names. It introduces no new XML metadata, keyed schema, vote choices or vote-scoring mechanics. The obsolete source note requesting an unavailable pXML allocation route is replaced by concrete code. Enclosing XANA markers remain.

VOTE-20261030-09 — CvXMLLoadUtility::LoadPostMenuGlobals, CvGameCoreDLL/CvXMLLoadUtilitySet.cpp:806–814.
The existing caller discarded readPass3's result. Check it, stop processing later leaders on failure, destroy the parser and clear GC's current XML filename, then return false. These cleanup operations match the function's normal completion path. Previously the oversized/unknown/mismatched cases could report failure locally and still let the overall loader succeed.

## Verification

tests/vote-loader/finalize-check.cpp embeds the complete actual revised finalizer. 1,933 cases passed strict C++03 (-Wall -Wextra -Werror -pedantic), ASan and UBSan: capacities 0–5, rows 0–7, four ballot names plus UNIT_WARRIOR, all eight combinations of inherited array presence, trailing defaults, failure preserving state, repeat finalization, mismatched numeric lengths and negative capacity. XML info lookup is deliberately absent from the stub interface.

tests/vote-loader/finalize-caller-check.cpp embeds the actual revised call block. 21 cases check zero through five leaders, success or each failure position, early stop, exactly one parser cleanup and filename clearing. Surrounding loader/class/globals are stand-ins; this does not compile complete CvLeaderHeadInfo or LoadPostMenuGlobals. Leak detection disabled as unsupported. No MSVC7.1/full DLL/real XML/game result.

The historical XML-argument loader fixture remains historical and does not validate the moved early-read stage. Actual engine XML traversal/default merging, comments/malformed nodes, schema/example data, info cache and player counter save/load and attitude-cache behavior need further review. Existing arrays are assumed to have the current global vote capacity, as in the baseline allocation contract. No exception-safety claim is made for allocation failure.

No DLL build triggered; this remains a partial integration draft using [skip ci].
