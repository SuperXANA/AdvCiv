# CvPartyGroup wrapper draft — 2026-10-27

## Scope and pins

Source: [CvPartyGroup at c6b1b14](https://github.com/SuperXANA/AdvCiv/tree/c6b1b14d0263196c497d8dcf85da41982d5ec7af).
Read-only baseline: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
All 54 source blobs were retrieved; all XANA-bracketed blocks were read across the 13 marked DLL files. This pass repairs only the Python-facing party wrapper. Other party integration remains partial coverage.

Current branch inventory matched the previous coverage snapshot; the apparent GenderCounterDraft head difference was its already-delivered documentation commit. No original feature head changed. This target had pending coverage; no unchanged failed target was rebuilt.

## PARTY-20261027-01 — wrapper definitions do not match their declarations

[Header declarations](https://github.com/SuperXANA/AdvCiv/blob/c6b1b14d0263196c497d8dcf85da41982d5ec7af/CvGameCoreDLL/CySelectionGroup.h#L98) accept CvPartyGroup pointers/references. [Definitions](https://github.com/SuperXANA/AdvCiv/blob/c6b1b14d0263196c497d8dcf85da41982d5ec7af/CvGameCoreDLL/CySelectionGroup.cpp#L334) instead accept CyPartyGroup and try to store a wrapper pointer as an engine pointer. The reference definition also conflicts with the ordinary wrapper copy constructor.

Four methods below those constructors still access m_pSelectionGroup, which is not a member of CyPartyGroup: pushMoveToMission, popMission, lastMissionPlot, and canStartMission. They cannot compile as declared. Correct the constructor parameter/cast types and dispatch every party method through m_pPartyGroup. Preserve normal wrapper copy construction and the original XANA dates/boundaries.

## PARTY-20261027-02 — null mission arguments dereferenced at the boundary

[pushMission](https://github.com/SuperXANA/AdvCiv/blob/c6b1b14d0263196c497d8dcf85da41982d5ec7af/CvGameCoreDLL/CySelectionGroup.cpp#L338) dereferences both context wrappers, and canStartMission dereferences its plot wrapper. A valid party with an absent context wrapper would crash before reaching the engine.

Forward NULL when the wrapper itself is NULL; otherwise forward its contained pointer, including an explicitly empty wrapper. This matches the nullable plot/unit convention of [1.14 selection-group mission declarations](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvSelectionGroup.h#L61). The eventual party engine must retain this contract or reject absent context explicitly before executing a mission. No orders are generated or executed by this draft.

## Changes and verification

Only the XANA wrapper block in CySelectionGroup.cpp and a parameter-name typo in its corresponding header block changed. Removing the XANA blocks leaves those two files equal to pinned 1.14 ignoring whitespace. Other source files are preserved exactly from the feature head.

Run:

```
python3 tests/party-wrapper/check.py
```

The test compiles the actual complete CyPartyGroup declaration and method bodies, extracted from the changed files, against instrumented engine API stubs. It passes g++ -std=c++03 -Wall -Wextra -Werror -pedantic with AddressSanitizer and UndefinedBehaviorSanitizer. Checks cover pointer/reference/copy construction; two-party dispatch isolation; movement, pop and last-plot forwarding; present and absent mission context; empty wrappers; and negative/upper-bound unit indices. LeakSanitizer is disabled for host compatibility. This test is an interface regression check, not an implementation of CvPartyGroup.

## Integration and verification limits

The source tree contains forward declarations of CvPartyGroup/CvPartyGroupAI but no class definitions. The complete 1.14 snapshot does not supply these new classes either. Therefore this sparse draft is intentionally not a complete-base build branch, has no copied workflow, and triggers no DLL build. No native DLL result or artifact is claimed.

Unit membership, party creation/deletion, freelist instantiation, save versioning, lifecycle reconstruction and Python binding ownership still need implementation/review before a useful native build. In particular, do not infer functioning party behavior from the wrapper fixture. Existing source outside the wrapper remains an unfinished draft and is not certified by these checks. Runtime Boost.Python conversions, mission-data ownership, game startup, saves and multiplayer were not tested.

The next coherent integration step is to define the party model and its lifetime/ownership contract, then finish membership and persistence against pinned 1.14 on this same isolated branch. Whether a strategic party should issue movement missions or coordinate existing selection groups remains a mechanics decision; this draft preserves the currently declared mission facade.

## Coverage continuation

The companion coverage JSON carries the prior ledger forward, changes CvPartyGroup from pending to partial, and records this scoped draft separately from the unchanged source. Eleven first-pass source targets remain pending. The user's stop gate is not satisfied.

Code revision: [a62534896395531bde41fca2ab1b880e5d203706](https://github.com/SuperXANA/AdvCiv/commit/a62534896395531bde41fca2ab1b880e5d203706). This ledger/documentation update does not change code.
