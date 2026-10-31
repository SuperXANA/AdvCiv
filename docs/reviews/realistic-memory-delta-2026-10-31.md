# Realistic AI memory correction delta — 2026-10-31

Original RealisticAIDecisions changed from `8383ce62fd67f00d399c937867828dd456915e43` to `372d64549f70884fbc86cec7bfbee0a9778bd948`. The new commit was read before further unchanged-branch review. Reuse ReputationWindowDraft-ChatGPT at `89903b02c0c7ace0524a789de3426cd4cc4fe704` for review documentation only. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Prior readiness finding REALISM-20261031-01 is updated, not presented as a new discovery.

## Confirmed user corrections

The four-file delta closes the vector header's outer template and removes its extra trailing class terminator. Vector-memory public APIs and getLSHHash now use AIMemoryContextTypes. GameStateMemory::write now writes eSubject, iOutcome and bObsolete, and the malformed PlayerTypes cast syntax was repaired. These are user-authored changes; no attempt was made to overwrite them or apply an older assistant snapshot to the original branch.

## Exact-head skip remains necessary

Skip `372d64549f70884fbc86cec7bfbee0a9778bd948` for full DLL preparation until user implementation supplies the missing behavior. The commit changes names/header/serializer lines, not recording, prediction, social-memory or persistence method implementations. The commented global insertion TODO and the future feature-vector/prediction design remain unresolved. No missing evaluator, memory rules or save contract was invented.

Remaining declaration/stream inconsistencies were checked against actual current files:
- [CvStructs.h:646](https://github.com/SuperXANA/AdvCiv/blob/372d64549f70884fbc86cec7bfbee0a9778bd948/CvGameCoreDLL/CvStructs.h#L646) still uses MemoryContext for the record, while vector-memory APIs now use AIMemoryContextTypes.
- [CvStructs.cpp:818–834](https://github.com/SuperXANA/AdvCiv/blob/372d64549f70884fbc86cec7bfbee0a9778bd948/CvGameCoreDLL/CvStructs.cpp#L818) still assigns ePlayer instead of declared eSubject, casts through MemoryContext, and uses features instead of rFeatures. Newly changed Read(iOutcome)/Read(bObsolete) pass scalar values rather than their addresses.
- CvAIVectorMemory.cpp's mismatched include quotes and runtime integer-expression fixp initializer are unchanged. CvGlobals.h's same-signature const getGameMemory overloads and incomplete insertion remain unchanged. See the previous readiness report for exact evidence; the prior diagnostic is not rerun or presented as new validation.

These are source observations, not newly observed native compiler errors.

The exact-head skip advances to this new SHA and records the older skip historically. Earlier score fixes/fixtures remain preserved in the assistant branch against f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e; the new incomplete delta is not overlaid or merged there. No source production changes, native DLL run, real RNG/fixed-point/save/game validation occurred. Publication is [skip ci].
