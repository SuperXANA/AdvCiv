# Vote attitude XML loader refinement — 2026-10-28

Source branch: LeaderSpecificVoteActionDiplomacy at 4f2e7c2ea110e7859fbab1bdac32a02a27f5bb30.
Previous isolated draft: b3df449e475b9603566ceebc5a49ede9c42e8ca6.
Code commit: [45de0c4d322d916e2bafe8a250457d263d3808d2](https://github.com/SuperXANA/AdvCiv/commit/45de0c4d322d916e2bafe8a250457d263d3808d2).
Read-only baseline: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## VOTE-20261028-04: decision field was read at the wrong cursor depth

CvLeaderHeadInfo::readPass3, CvInfo_Civilization.cpp line 1130 in the revised commit
(original line 1124), contained an invalid if statement without parentheses.
After syntax-only correction it still called GetChildXmlVal after SetToChild had
already entered the decision field. For the positional entry structure assumed
by this loader, that attempts to descend into the decision text field rather
than reading its value. The ballot preference remains at NO_PLAYER_VOTE.

The repair reads the current node with GetXmlVal and restores valid if syntax.
The actual pinned CvXMLLoadUtility.h declares GetXmlVal(std::string&) and the
baseline CvXMLLoadUtilityGet.cpp describes/implements its current-node behavior;
GetChildXmlVal explicitly moves to a child. Existing parent/sibling navigation,
four supported ballot strings and unknown-string assertion/default remain intact.
No XML schema or new ballot mechanics are introduced.

## VOTE-20261028-05: excess rows can index beyond vote arrays

The loop uses the XML child count while all three arrays use getNumVoteInfos().
Once the decision read is corrected, a longer list can write out of bounds.
At lines 1114–1119, the loader now rejects an oversized positional list before
allocation or writes, restores the enclosing leader cursor and returns false.
It does not silently truncate the list. Whether the global pass-3 caller
propagates this false result remains outside the verified scope.

This retains positional row-to-vote mapping. Deciding a new keyed format would
require source/schema work; the review does not supply one.

## Verification

python tests/vote-loader/check.py compiles the actual readPass3 body using
g++ -std=c++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan and
UBSAN_OPTIONS=halt_on_error=1. The XML interface is a minimal tree/cursor stub,
not the engine parser. 55 cases passed: absent/empty/short/exact/oversized lists
for zero through five votes, four recognized decisions and unknown strings,
missing numeric siblings, array defaults, and return cursor position.
The existing vote-counter regression also passed.

Independent negative controls:
- Restoring only GetChildXmlVal fails the expected preference assertion.
- Disabling only the size guard produces an ASan heap-buffer-overflow in
  readPass3 for an oversized list.
- The syntax-only original fails the oversized-list return check.

An initial suspected uninitialized integer read was ruled out by reading
the actual baseline GetNextXmlVal(int&, int): assignDefault initializes its
output before traversal, including failed reads. No change was needed there.

## Limits and remaining work

Only the marked loader changed. Original source, 1.14 and XANA date markers
are preserved. Reused VoteCounterDraft-ChatGPT; no new branch.
No DLL workflow exists on this sparse draft and no DLL build was triggered.
This is not MSVC 7.1, real XML/schema, cache, save/load, attitude-cache or gameplay
validation. Repeated loader invocation/ownership and malformed/comment nodes are
not covered. Existing full-feature lifecycle/persistence and integration work
remains unresolved; no missing gameplay rules were invented.
