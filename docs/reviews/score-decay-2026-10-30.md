# Explicit alignment and reputation decay rounding — 2026-10-30

Finding SCORE-DECAY-20261030-01. Read-only source RealisticAIDecisions f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e, baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Reused ReputationWindowDraft-ChatGPT at parent 46e32b64df7a7e098f6ec7f39f340910ac28806b; prior fixes retained. Complete 75-branch inventory found no changed original heads against the latest global ledger at 86358f64e315b76323bb351840521821fd7e6b69. No consolidation or new branch needed.

## Committed correction

AlignmentScore::decay, CvGameCoreDLL/AlignmentScore.cpp:88–89: replace both int *= scaled expressions with explicit (int * scaled).round() assignments.

ReputationScore::decay, CvGameCoreDLL/ReputationScore.cpp:62–63: likewise explicitly round the age-weighted product before assigning it to the integer score.

Both expressions exist unchanged in the pinned original source. Actual baseline ScaledNum.h:235 disables implicit operator int, and 1191–1197 comments out int& operator*=(int&, ScaledNum). Thus these original expressions cannot compile against that baseline contract. Its lines 231–236 explicitly recommend rounding; the old commented getInt implementation at 233 delegates to round. The implemented round at 864–877 rounds signed halves away from zero. This patch chooses that explicit policy, rather than adding conversion operators to the shared numeric type.

New changes are enclosed in dated XANA markers. Decay percentages, ring traversal, reputation ages/window, mutation order and serialization are unchanged.

## Verification

tests/score-decay/check.cpp contains the actual revised decay method bodies, reduced score containers and an explicitly labelled floating-point scaled contract stub. It exposes multiplication, pow and round but no implicit integer conversion or int compound multiplication. Strict C++03 -Wall -Wextra -Werror -pedantic plus ASan/UBSan passed:

- 1,925 alignment configurations: seven positive/negative/zero score seeds, all pairs of 0/25/50/75/100 percent retention, counts 0–10 and varied ring heads; three consecutive decays, all slots checked, including inactive slots.
- 728 reputation configurations: seven score seeds, lengths 0–12 and sample windows 1–8; three consecutive decays checking the entire vector, including unchanged newest/older entries and empty/short windows.

Restoring the original method bodies reproduces three no-match-for-operator*= compiler diagnostics. No warnings suppressed. Leak detection disabled as unsupported; no leak claim.

These are interface/control-flow tests, not execution of the actual ScaledNum arithmetic, pow tables, full score classes, MSVC 7.1, DLL, savegames or gameplay. In particular floating-point stub results do not certify game's 1/2048 quantization or large-score numeric range. Baseline ScaledNum has a narrower representable range than int; out-of-range products/decay metadata remain separate review work.

## Remaining mechanics and integration

Nearest rounding can retain small values: 1 at 95 percent retention rounds to 1. If gradual decay to zero is desired, a different policy or fractional carry must be designed explicitly; this patch does not invent one. Negative and above-100 decay metadata, persistent head/count validation, call frequency/turn integration, and complete metadata/build integration remain unverified. No new serialization or feature implementation was invented.

This remains a partial draft and uses [skip ci]. No native DLL run was triggered, retried or claimed.
