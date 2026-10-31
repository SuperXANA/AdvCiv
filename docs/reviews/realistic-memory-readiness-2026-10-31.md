# Realistic AI memory delta readiness — 2026-10-31

REALISM-20261031-01. Changed read-only source RealisticAIDecisions `8383ce62fd67f00d399c937867828dd456915e43`, compared with previously reviewed `f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e`. Assistant branch reused for this report: ReputationWindowDraft-ChatGPT at `bdeb212cc0f21d71b3509cc21c9fa96539f88f21`. Its production code still refines the previous source snapshot; the new incomplete delta is not overlaid or merged into that branch.

Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh inventory: 75 branches, one changed original head (RealisticAIDecisions). This delta was prioritized before further unchanged-branch review. Previous global ledger at 0c3c76cf0374bb0e27ca3d2af30ea607bb0dbca8 and existing score/persistence findings were consulted; those earlier fixes are not new findings here.

## Exact-head skip

Skip original source `8383ce62fd67f00d399c937867828dd456915e43` and associated full-DLL preparation until user changes provide the missing implementation details. The new source commit explicitly describes the work as unfinished and leaves vector construction and predictOutcome behavior for future work. The existing insertion path in CvGlobals.h is a commented TODO; public recording/prediction/social/persistence methods have declarations but the supplied vector-memory implementation defines only init, uninit and getLSHHash. Do not invent a memory model, outcome mapping, feature normalization or persistence format to obtain a build.

Earlier alignment/reputation fixes, fixtures and reports remain unchanged on the assistant branch. New user files and the deliberately commented unfinished block in CvStructs.cpp are preserved on the original source branch. No source branch update, merge, DLL preparation, workflow trigger or new production implementation was performed for this readiness pass.

## Code evidence from the changed head

All six changed files were read at the exact source SHA: CvAIVectorMemory.h/.cpp, CvEnums.h, CvGlobals.h and CvStructs.h/.cpp. Existing CvGlobals.cpp, CvGame.cpp, CvPlayer.cpp, CvPlayerAI.cpp/.h and CvEnumMacros.h were read for integration/type context.

- [CvAIVectorMemory.h:23–31](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvAIVectorMemory.h#L23) declares recordMemory, predictOutcome, spreadGossip, forgetOldMemories and read/write. The supplied cpp contains no implementations of these operations. CvPlayerAI.cpp:87 already constructs the memory object, and CvGame.cpp:32 includes its header, so this is connected to engine compilation.
- [CvGlobals.h:717–722](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvGlobals.h#L717) leaves memory insertion as a commented incomplete signature/body. Recording ownership and stable global-memory indexing therefore remain unfinished.
- [CvStructs.h:643–656](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvStructs.h#L643) declares eSubject, iOutcome, bObsolete and vector<scaled> rFeatures, whereas [CvStructs.cpp:795–834](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvStructs.cpp#L795) reads/writes ePlayer, bWasBackstabbed and features as float-style data, omitting the new outcome/obsolete fields. The read method also contains malformed static_cast<PlayerTypes)>. Merely renaming fields would not specify how integer outcome, backstab state, obsolete state and fixed-point observations should be persisted.
- [CvAIVectorMemory.cpp:1](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvAIVectorMemory.cpp#L1) has mismatched include quotes. Header [line 40](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvAIVectorMemory.h#L40) lacks the outer hash_map template closing angle bracket and has an extra class terminator after #endif. Context names MemoryContext and MemoryContextTypes differ from the supplied ENUM_START(AIMemoryContext,...) declaration at CvEnums.h:2460; CvEnumMacros.h emits AIMemoryContextTypes.
- [CvGlobals.h:708–716](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvGlobals.h#L708) gives both getGameMemory overloads the same const-qualified parameter signature while changing the return type, which cannot distinguish C++ overloads. The first also attempts mutable access through a const vector and excludes index zero. These interfaces require correction when integration resumes.

These are source-read blockers, not errors observed in an MSVC build. No compiler-error count or full-DLL result is inferred.

## Deterministic hyperplane initializer diagnostic

[CvAIVectorMemory::init, cpp:15](https://github.com/SuperXANA/AdvCiv/blob/8383ce62fd67f00d399c937867828dd456915e43/CvGameCoreDLL/CvAIVectorMemory.cpp#L15) computes `(CvRandomHyperplane.get(2000, "LSH_INIT") - 1000) / 1000` with integer arithmetic before passing the result to fixp. Baseline CvRandom.h returns unsigned short, promoted to int for the subtraction. Exhaustively evaluating the expression over all 2000 input values in a strict C++03 diagnostic produces one -1 (input zero), 1999 zeros and no other value. It does not produce the commented range of fractional values.

Baseline ScaledNum.h:1313 expands fixp into a fromRational template requiring a constant expression. A runtime RNG expression is therefore also incompatible with that macro. This must be addressed together with the intended fixed-point vector/normalization contract; this pass does not choose a replacement distribution or implement the missing evaluator.

The small diagnostic used g++ -std=c++03 -Wall -Wextra -Werror -pedantic and asserts the complete integer-expression distribution. It does not execute the actual RNG, ScaledNum, memory object, engine or DLL. No test artifact is presented as native validation.

## Resumption conditions

New original-source work should specify/implement recording and global insertion, the six observation features and their scaling, outcome prediction, index ownership/cleanup and save/load format, with consistent context/record types. Then review that delta, preserve the earlier score fixes, and prepare a complete pinned-baseline overlay on an assistant branch if meaningful DLL validation becomes possible.

Until then, skip this exact source head rather than repeatedly rebuilding it or filling in missing behavior. This report/ledger publication uses [skip ci].
