# Alignment arithmetic refinement — 2026-10-28

Source RealisticAIDecisions at f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e.
Reused ReputationWindowDraft-ChatGPT; code da3311fbba55d767538e424d4818e1ba9f5b6d7b.
No changed original heads found in this inventory. Existing skip gates retained.

## ALIGNMENT-20261028-01

AlignmentScore.cpp:
- changeAlignmentTowardsPositive, line 42: high addition, coupled low subtraction.
- changeAlignmentTowardsNegative, line 54: low addition, coupled high subtraction.
- changePermanentAlignmentTowardsPositive, line 66: permanent high addition.
- changePermanentAlignmentTowardsNegative, line 73: permanent low addition.

The temporary methods clamped the result of signed arithmetic after performing
the arithmetic. That cannot prevent undefined signed overflow. Permanent
methods used unchecked addition. E.g. INT_MIN + INT_MIN triggers UBSan in the
actual original positive-change method.

A local C++03 helper (line 7) checks overflow using representable boundary
differences/sums before computing the result. Addition and subtraction are
handled separately so INT_MIN is never negated. Temporary state retains the
existing upper m_iMaxDelta and lower MIN_INT limits. Permanent state saturates
at the int bounds instead of overflowing. Every previously representable
arithmetic result retains its behavior, including zero-change early returns,
negative deltas/caps and independent-axis behavior. No symmetric lower
m_iMaxDelta cap or new alignment gameplay rule is introduced.

An initialization concern was explicitly ruled out: actual CvStructs.h
AlignmentValue has a default constructor initializing both fields to zero.
The changes do not claim to repair uninitialized buffers.

## Checks and limits

python tests/alignment-arithmetic/check.py compiles the four actual methods
plus actual helper and class header using g++ -std=c++03 -Wall -Wextra -Werror
-pedantic with ASan/UBSan. -Wno-reorder suppresses the pre-existing header
constructor initializer-order warning; constructor order was not changed.
Minimal AlignmentValue and forward stream declarations stand in for surrounding
engine types. Test-only private access inspects mutation results directly.

810 combinations: nine starting values, nine changes, five caps, two axis modes.
The reference uses exact double arithmetic for these 32-bit int sums/differences.
Temporary and permanent results pass, including INT_MIN/INT_MAX boundaries.
UBSAN_OPTIONS=halt_on_error=1; ASAN_OPTIONS=detect_leaks=0.
Original-source negative control reports signed integer overflow.

No workflow added, no DLL build triggered, no MSVC 7.1 or gameplay result.
get() aggregation/base/permanent sums can still overflow independently;
decay, read/write validation and turn-window/count integration remain unverified.
These tests do not call get(), nextTurn(), decay() or persistence.
This is a scoped arithmetic repair, not a complete alignment implementation.
Original branches, read-only 1.14 and original date markers remain unchanged;
the helper carries new paired XANA annotations.
