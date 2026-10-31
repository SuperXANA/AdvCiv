# Alignment player stream references — 2026-10-31

Source: RealisticAIDecisions `f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e`.
Reused assistant branch: ReputationWindowDraft-ChatGPT; reviewed parent `7e1294956a9b3eaaf9f3d67b6172c4f57b9bdd1c`.
Correction and fixture: [f7b5d32cf1aa50a7dad7157d9d84420b18bb23d8](https://github.com/SuperXANA/AdvCiv/commit/f7b5d32cf1aa50a7dad7157d9d84420b18bb23d8).
Inventory: 75 branches; no original source-head changes against the latest global coverage ledger. Prior alignment/reputation reports read before this persistence follow-up. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`.

## ALIGNMENT-20261031-04 — player alignment stream blocks do not compile

In the original CvPlayer.cpp, CvPlayer::read line 14779 calls `stream->Read`, and CvPlayer::write line 15175 calls `stream->Write`. Both functions receive `pStream`; there is no `stream` variable. The score save loop at original line 15163 calls `it.write(pStream)` on a std::vector iterator rather than its AlignmentScore element.

Change the two stream references to `pStream` and the iterator call to `it->write(pStream)`. Corrected locations are [read line 14781](https://github.com/SuperXANA/AdvCiv/blob/f7b5d32cf1aa50a7dad7157d9d84420b18bb23d8/CvGameCoreDLL/CvPlayer.cpp#L14781), [score write line 15165](https://github.com/SuperXANA/AdvCiv/blob/f7b5d32cf1aa50a7dad7157d9d84420b18bb23d8/CvGameCoreDLL/CvPlayer.cpp#L15165), and [faction write line 15177](https://github.com/SuperXANA/AdvCiv/blob/f7b5d32cf1aa50a7dad7157d9d84420b18bb23d8/CvGameCoreDLL/CvPlayer.cpp#L15177). Only these three existing C++ lines change. Enclosing XANA markers, newer assistant changes, field order, counts, encoding and feature boundaries are preserved.

## Verification

Run `python tests/alignment-save/check.py` from a checkout of this assistant branch. The fixture extracts the actual marked alignment sections of CvPlayer::read/write, actual AlignmentScore::read/write, actual AlignmentValue declaration/read/write, and the actual AlignmentScore header. A reduced CvPlayer shell and byte-buffer FDataStreamBase stand-in replace the surrounding engine.

8,800 cases passed: 0–4 axes, 0–3 faction entries, absent/three selected factions, all ten valid ring heads and all counts 0–10. Cases include signed-int endpoint permanent values, distinct per-axis/per-slot samples, replacing populated destination vectors, exact record order/counts and rewritten bytes, and a trailing sentinel to detect stream displacement. This verifies serialization bytes only, not semantic restoration of score configuration.

The same fixture with the three original expressions fails compilation: two “stream was not declared” errors and one vector iterator “has no member named write”. g++ flags: `-std=c++03 -Wall -Wextra -Werror -Wno-reorder -pedantic -fsanitize=address,undefined`; leak detection disabled, UBSan halt_on_error enabled. The preexisting AlignmentScore constructor initializer-order warning is suppressed, as in the earlier constructor fixture; this is not a warning-free full-class/engine claim.

## Remaining limits

No full translation unit, MSVC7.1, native DLL, real engine stream, Windows ABI, versioned save compatibility, XML, gameplay or multiplayer validation. The stream stand-in uses host bytes. Constructor metadata on load, count/head validation, fixed-point range, first-sample visibility and actual nextTurn/decay scheduling remain separate review work. No feature behavior or recovery policy is invented here. Partial scoped work is committed with `[skip ci]`; no DLL workflow is triggered or observed for this correction.
