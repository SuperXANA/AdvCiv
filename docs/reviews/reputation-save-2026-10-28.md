# Reputation serialization follow-up — 2026-10-28

Source feature: RealisticAIDecisions f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e.
Previous draft head: 3beb7b9b413e321fb93f93c92ded6b66af352dd9.
New code: https://github.com/SuperXANA/AdvCiv/commit/ab9846a637dfc2847349cb63d398017f7d8d4c3a
Read-only 1.14 remains pinned at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

This follow-up reuses ReputationWindowDraft-ChatGPT. Earlier window/default/setter findings REPUTATION-20261028-01 and -02 remain recorded and are not new findings here. The fresh branch inventory had no changed source heads; the CivicScroll difference was already-delivered ceiling-assessment documentation. This pass deepens previously partial reputation persistence coverage.

## REPUTATION-20261028-03 — loaded score histories shift behind empty entries

[CvPlayer::read score block, lines 14535–14544](https://github.com/SuperXANA/AdvCiv/blob/ab9846a637dfc2847349cb63d398017f7d8d4c3a/CvGameCoreDLL/CvPlayer.cpp#L14535).

Original sequence: clear vector, read count N, resize(N), then push_back each of N loaded ReputationScore objects. resize constructs N default scores; push_back adds another N. The loaded histories occupy indices N..2N-1 while the expected lookup indices address the first N empty entries. A later save also writes the doubled count.

The repair changes resize to reserve at line 14539. Capacity is prepared without creating elements; each parsed score is appended once, retaining serialized order. Existing XANA 11-15-2025 block markers and all unrelated code remain unchanged. Zero count clears the destination as before. This is an index/count repair; it does not migrate previously written malformed doubled vectors or add historical schema/version handling.

## REPUTATION-20261028-04 — const writer call cannot compile

[ReputationScore::write implementation](https://github.com/SuperXANA/AdvCiv/blob/ab9846a637dfc2847349cb63d398017f7d8d4c3a/CvGameCoreDLL/ReputationScore.cpp#L96) and [declaration, line 22](https://github.com/SuperXANA/AdvCiv/blob/ab9846a637dfc2847349cb63d398017f7d8d4c3a/CvGameCoreDLL/ReputationScore.h#L22).

CvPlayer::write uses std::vector<ReputationScore>::const_iterator at lines 15069–15072 and calls (*it).write(pStream). A const_iterator yields a const score, but the source declares write as non-const. The repair adds const to both declaration and definition. The writer only reads size, sample count and score elements; it mutates the stream, not the score. Serialized field order, types and count encoding do not change. The pinned FDataStreamBase header was read to confirm scalar/const-array write support.

## Verification

python tests/reputation-save/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined; LeakSanitizer disabled.

The fixture compiles the actual ReputationScore header, actual grow/get/set/read/write methods and the actual extracted CvPlayer score reader/writer blocks. A byte-buffer stub implements the stream methods those blocks use. Assertions cover:
- three distinct histories restored to exactly three entries in order, replacing an already populated destination;
- a writer called through a const player fixture and the source const-iterator loop;
- byte-identical score round-trip and correct position at an appended sentinel;
- loading a zero count into a previously populated destination;
- legacy sparse score records with the source's uiFlag < 13 selection and host-encoded size_t.

Negative controls restore each old defect independently: resize plus append fails the count assertion; non-const write fails compilation with discarded qualifiers. The repaired code passes both conditions.

The fixture uses the host ABI for bytes and size_t; it does not certify Windows/MSVC stream binary compatibility. Actual CvPlayer::read/write outside these extracted blocks, engine streams, old saved-game versions, preexisting malformed saves, alignment persistence, metadata, decay, multiplayer and gameplay remain unvalidated. No full DLL/MSVC 7.1 result is claimed. No workflow was added or DLL build triggered. A future useful native build must still use the authorized complete pinned-base overlay and named dll-build workflow.

Exactly three source files change relative to the previous draft, plus the regression fixture. The original feature branch and 1.14 are preserved. Further reputation/alignment integration work should continue on this assistant branch.

## Coverage state

UnitStatusEffects remains deferred, and the Copilot ceiling assessment remains closed without a proposed production fix. No initial pending branch rows remain. Partial scopes and unverified native states still require deeper review; the stop gate is false.
