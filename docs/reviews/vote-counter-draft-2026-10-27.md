# Vote counter refinement draft

Reviewed source: LeaderSpecificVoteActionDiplomacy at
4f2e7c2ea110e7859fbab1bdac32a02a27f5bb30.
Enum reference: read-only AdvCiv 1.14 at
5970334b64a875b5cdb370c94fc9a98db4eacda6, CvEnums.h PlayerVoteTypes.

## Scope and status

This is an intermediate source refinement of the XANA 01-24-2026 Leader Specific
Player Vote Diplomacy counter methods. It is not a complete-base build branch
or a finished implementation of the feature. It does not include a build
workflow and does not claim full DLL validation. Original branches are unchanged.

## Findings and code changes

### VOTE-20261027-01: logical OR does not combine case labels

The source uses case PLAYER_VOTE_ABSTAIN || PLAYER_VOTE_NEVER in four switches.
In pinned 1.14 those ballots are -4 and -5. Their logical OR evaluates to 1,
so neither ballot matches the case and team ID 1 does match it.

The extracted original method reproduced:
- A team-1 ballot with alignment 10 changes alignment to 9 and team preference
  to -1, where the valid team ballot should increase both.
- Election abstention changes alignment 10 to 11, increasing the counter
  instead of moving it toward zero.

The refinement separates abstention/never ballots from real team IDs, uses
separate case labels for ordinary and city ballots, and keeps saturation at
-100..100. Invalid vote IDs, team/player IDs and absent arrays return safely.

### VOTE-20261027-02: independent city history was skipped

After correcting only the source case labels, a city-assignment abstention with
overall alignment 0 and the affected owner's history 5 still leaves history 5:
the first zero-delta early return bypasses the second counter.

The refinement updates both histories independently. The same example leaves
overall alignment 0 and moves the owner's history to 4. Abstention/never still
decays toward zero; YES/NO retain the source's positive/negative direction.

### VOTE-20261027-03: counter declaration and lookup compilation defects

The AI_updateVoteCount declaration contained an extra closing parenthesis.
It is corrected and the state-changing method is explicitly non-const.
The election preference lookup assigned an int to the entire local iCount
array instead of an element. The refinement reads each candidate's score
directly. Both preferred-candidate getters preserve the source's positive-only
selection and first-index tie behavior, with null/bounds checks.

## Checks

Run: python tests/vote-counter/check.py
Optional:
VOTE_TEST_SANITIZE=1 ASAN_OPTIONS=detect_leaks=0 python tests/vote-counter/check.py

The harness compiles the three actual revised methods and their declarations
using C++03 and minimal Civ stubs. PlayerVoteTypes constants match the pinned
base. Normal and ASan/UBSan runs passed with no compiler warnings. Coverage
includes team IDs 0/1/17, abstention/never, positive/negative/neutral histories,
city counter independence, saturation, candidate selection, invalid IDs and
unavailable arrays.

The harness does not compile the rest of CvPlayerAI or the complete DLL.
Allocation/reset lifecycle, save/load persistence, XML-loader integration,
attitude-cache invalidation and actual Civ4 vote dispatch remain outside this
counter-only refinement. The source branch has additional unresolved integration
and compilation work; this draft is not a drop-in DLL release. A complete-base
DLL build must follow that work before declaring the full feature validated.
