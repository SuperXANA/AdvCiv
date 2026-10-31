# Repeated early vote XML staging — 2026-10-31

VOTE-20261031-10. Original LeaderSpecificVoteActionDiplomacy `8fcfdd97329279393120aaab34c00dde84e729df`; reused VoteCounterDraft-ChatGPT parent `fc7f4a04f002a5bfe261aca49d8375fdbf03a946`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh inventory of 75 branches has no original-head changes against the global ledger at 89903b02c0c7ace0524a789de3426cd4cc4fe704. Unchanged RealisticAIDecisions implementation skip is retained. Prior counter, copy-ownership, moved-staging and finalizer reports were read before this pass.

[Correction and fixture 635242cfeb29ccbe49646f8f679fde7f4650771f](https://github.com/SuperXANA/AdvCiv/commit/635242cfeb29ccbe49646f8f679fde7f4650771f).

## Defect and completed correction

CvLeaderHeadInfo::read, CvGameCoreDLL/CvInfo_Civilization.cpp:1114–1118, stages positional VoteDecisionAttitudes rows. Before this correction, each read appended to all three vectors without replacing prior pending rows. Reading a valid two-row list twice before readPass3 produces four rows; with two votes the finalizer rejects an otherwise valid repeated read. A present empty list also left earlier pending rows untouched.

Clear the pending decision-name, favorite-attitude and hated-attitude vectors together after locating the list and passing SkipToNextVal, before counting/reading its entries. A repeated present list is now idempotent; a different present list replaces pending rows and an explicit empty list empties pending staging. An omitted tag retains inherited pending staging. This follows replacement of an explicitly supplied positional list rather than concatenation across read calls.

The existing finalizer remains unchanged. Empty staging is still a successful no-op for already allocated inherited arrays or null defaults; this patch does not make an empty XML list clear finalized arrays. Existing allocation/default semantics, four supported ballots, positional format, numeric utility defaults, invalid-ballot rejection and late capacity checking are preserved. Earlier XANA marker blocks and user edits remain; the three clears have a new paired date annotation.

## Verification

Run `python tests/vote-loader/staging-check.py`. It extracts the actual complete marked early-staging block and the complete current no-argument finalizer. A reduced leader class, globals and XML tree/cursor interfaces replace the engine. XML GetNextXmlVal behavior is modeled from the pinned baseline CvXMLLoadUtilityGet.cpp, which assigns numeric default zero before attempting traversal. Missing numeric siblings were already ruled safe in the prior report; no new fix is claimed for them.

2,184 strict C++03/ASan/UBSan cases passed: vote capacities 0–5, all first/second list lengths within capacity, four ballot offsets, zero/one/two numeric fields in the second list, and present/omitted second tags. Each case reads the first present list twice, checks vector cardinalities/content, reads the second present or omitted list, checks root cursor restoration, finalizes, checks every decision/attitude slot and trailing defaults, and repeats finalization without replay.

Three negative controls remove one newly added vector clear at a time. Each independently fails that vector's repeated-stage size assertion. This demonstrates that all three vectors must be replaced together to maintain positional alignment.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Remaining scope

No full CvLeaderHeadInfo::read/base/default-merging implementation, real Firaxis XML/parser/schema/example data, comment/malformed-node navigation, failed SkipToNextVal cleanup, allocated-array inheritance lifecycle, info cache, player counter persistence/attitude-cache invalidation, MSVC7.1/DLL or gameplay validation. The original source tree supplies no XML files; no schema or authoring data was fabricated. Existing finalizer/copy/counter fixtures remain separate evidence.

No DLL workflow triggered: partial scoped draft uses [skip ci]. Continue with remaining XML/counter/native integration on the same assistant branch.
