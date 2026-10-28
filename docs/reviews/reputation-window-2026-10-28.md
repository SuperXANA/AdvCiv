# Reputation window review — 2026-10-28

Source: RealisticAIDecisions at f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e.
Code: https://github.com/SuperXANA/AdvCiv/commit/3e1cadff15d0d8741a40bb83b5760c389b087a22
Read-only AdvCiv 1.14 pin: 5970334b64a875b5cdb370c94fc9a98db4eacda6 (unchanged in branch inventory).

Scope: ReputationScore header and implementation, with actual XANA 11-15-2025 reputation callers in CvPlayer.cpp and CvPlayerAI.cpp read for context. Supporting score files originally have note markers rather than full delimiters; new edited constructor/get blocks carry the same original feature date. No other feature branch is imported. This is a source-based draft; unmarked historical upstream differences are not reconciled for a native overlay.

## REPUTATION-20261028-01 — completed-turn window

Original get: https://github.com/SuperXANA/AdvCiv/blob/f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e/CvGameCoreDLL/ReputationScore.cpp#L14
Repaired get: https://github.com/SuperXANA/AdvCiv/blob/3e1cadff15d0d8741a40bb83b5760c389b087a22/CvGameCoreDLL/ReputationScore.cpp#L17

The original computes sample count from configured samples minus one and rejects iTurn >= size(). With current-turn storage present, a four-sample query at turn 4 over history 10,20,30,40 returns 30 (20,30,40 only), rather than 25. Turn 1 returns zero; a single-sample configuration never returns a score. Querying the first turn immediately after the stored history also returns zero.

Proposed policy: exclude the queried turn, include up to the configured number of preceding completed turns, normalize by available early-game samples, accept iTurn == size(), and return zero for nonpositive or beyond-history queries. This explicitly documents timing; same-turn reputation changes remain excluded. It does not establish whether all gameplay callers should use completed-turn rather than immediate scores.

The original int sum can overflow for legal int samples. The replacement accumulates in double and rounds half away from zero. Up to 100 32-bit int samples sum exactly within the target double precision; the mean stays within the int sample bounds. Positive/negative half cases and extreme samples are checked. No modern C++ syntax is introduced.

## REPUTATION-20261028-02 — default window and setter compilation

Original header: https://github.com/SuperXANA/AdvCiv/blob/f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e/CvGameCoreDLL/ReputationScore.h#L9
Repaired header: https://github.com/SuperXANA/AdvCiv/blob/3e1cadff15d0d8741a40bb83b5760c389b087a22/CvGameCoreDLL/ReputationScore.h#L10

ReputationScore::ReputationScore initializes the sample count to zero while reset initializes it to four. Fresh instances now use four consistently. CvPlayer's explicit reset initialization already supplies four; this finding does not imply that every existing gameplay object starts with zero.

setSampleSize (original line 29; repaired line 31) uses a conditional operator with a void reset call and a non-void assignment expression. Replaced with if/else retaining the existing 1..100 validation and reset-to-four policy. Storage remains char; this draft does not redesign sample adjustment or deserialization.

## Verification

python tests/reputation-window/check.py passed under g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. LeakSanitizer disabled. It compiles the actual full header and extracted actual grow/get/set bodies with standard containers, assertions, and only a forward-declared engine stream type. Tests cover negative/empty/future queries, initial one/two samples, four completed turns with current-turn exclusion, iTurn == size(), configured sample size one and 100, reset/clear, negative ties and INT_MIN/INT_MAX histories.

No full translation-unit, MSVC 7.1, DLL, decay, stream, engine, save or multiplayer validation is claimed. No workflow was added or DLL build triggered. Remaining alignment, reputation metadata, persistence and AI call integration require separate coverage; reuse this branch for further work. All original source files are retained; only the two score files are modified.

## Additional coverage and inventory

LeaderSpecificMultilayeredAIDecisionEval at 484412d0de7e42e2d310bb39e75340fc5307f597 has only README.md in its complete recursive tree. No implementation exists to evaluate at that head. Revisit when source is added.

Fresh branch inventory showed no changed source heads; the prior PlotTimerDraft head difference is its already-delivered documentation commit. Three first-pass branches remain: UniqueCivicsReligions, UnitStatusEffects, alert-autofix-1. Partial/unverified scopes remain, so the stop gate is false.
