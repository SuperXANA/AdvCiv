# Versioned AI gender-counter persistence — 2026-10-31

GENDER-20261031-09. Read-only GenderSpecificDiplomacy source `80e6ec595041cf335d5437b7bedea4fcaa61622b`; reused GenderCounterDraft-ChatGPT parent `6aea3099138d7d00bbb260d540d81ac67caff6d8`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no original-head changes against global ledger 1ae7ec40153adafffa54d07ca325f059db3dff49. Unchanged implementation skips are retained. Prior gender-counter/read/UI reports were read before addressing their outstanding version-22 compatibility boundary.

[Correction and fixture c0de081419894dddd83e78d45169f03dc8635d95](https://github.com/SuperXANA/AdvCiv/commit/c0de081419894dddd83e78d45169f03dc8635d95).

## Defect and correction

Baseline CvPlayerAI writes version 22 without favorite/hated gender arrays. The feature inserts both MAX_PLAYERS arrays after m_aiFavoriteCivicCounter but still writes 22, and its reader unconditionally consumes them. Reading a baseline-format AI player therefore takes bonus-trade and subsequent state as gender counters, displacing all following data.

CvGameCoreDLL/CvPlayerAI.cpp:
- At 23150, read the two gender arrays only if uiFlag>=23.
- For older versions, explicitly zero both arrays (23157–23161), including existing destination state, matching the actual constructor/AI_reset zero initialization.
- At 23336, emit version 23, preserving the historical version-22 comment. Existing writes, array order and expansionist-hate serialization are unchanged.
- Both original XANA marker pairs remain, including the writer's historically mislabeled feature marker; new version/reader annotations identify this refinement.

The surrounding baseline eight-array/expansionist-hate reader block matches the pinned baseline once the gender-specific block is excluded. Its existing uiFlag>=22 expansionist-hate gate remains unchanged. This is an independent version increment within the gender feature branch, not integration with any other feature branch.

## Verification

Run `python tests/gender-save/version-check.py`. It extracts the actual writer version statements and the actual counter/expansionist-hate read/write region. Engine streams, array ownership/class construction and the expansionist-hate map serializer are stand-ins.

252 C++03/ASan/UBSan cases passed: versions 21–23, seven value seeds, three entry patterns and MAX_PLAYERS sizes 1,2,4,19. Cases check every existing neighboring array, distinct favorite/hated values, explicit old-version zeroing over stale state, unchanged expansionist-hate version dispatch, following-object sentinels, and exact rewritten version-23 host bytes. Original arrays are int[MAX_PLAYERS] in the fixture; real constructor allocation/ownership and real map encoding are not validated.

Three independent negative controls restore ungated reads, restore emitted version 22, or remove old-version zeroing. They respectively reproduce stream-position, version and stale-counter assertions. The earlier typo-only read fixture remains separate; it never established old-save compatibility.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Compatibility limits and next scope

Earlier feature saves marked version 22 already contain these arrays but cannot be distinguished from baseline version 22 through that flag. They are not migrated or supported by a heuristic decoder. New version-23 saves require this gender reader; unchanged baseline DLLs cannot read the added fields. This is a structural correction toward baseline-save loading, not certification of complete engine save compatibility.

No complete CvPlayerAI read/write, real binary engine stream/EnumMap, MSVC7.1/DLL, basic-info XML/schema/installation, cache, UI/gameplay or multiplayer validation. Full surrounding player state and other independent branches are not combined or certified. Runtime metadata and native integration remain queued.

Partial scoped work uses [skip ci]; no DLL workflow triggered. Original branches, baseline and newer edits remain untouched.
