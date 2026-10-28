# ScaledNum ceiling alert assessment — 2026-10-28

Verdict: no correctness defect established by cpp/unsigned-difference-expression-compared-zero in the inspected ceil expression. No production-code revision or native DLL build is warranted for this alert alone. The modulo expression is a reasonable optional clarity rewrite, already present on the Copilot branch.

Pins:
- Read-only 1.14: 5970334b64a875b5cdb370c94fc9a98db4eacda6
- Copilot alert-autofix-1: f52ced74c31bdbd9696c37b00b73ce12b99f5d1b
- UnitStatusEffects: 1dd3fea3cda92dbce247b5bdfda0c93e6ccfd7ed (complete recursive tree contains only README.md).

## Actual functions and types

[ScaledNum::ceil, baseline lines 245–249](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/ScaledNum.h#L245):
return iR + ((m_i >= 0 && m_i - iR * SCALE > 0) ? 1 : 0);

[Copilot line 248](https://github.com/SuperXANA/AdvCiv/blob/f52ced74c31bdbd9696c37b00b73ce12b99f5d1b/CvGameCoreDLL/ScaledNum.h#L248) replaces the subtraction test with m_i % SCALE != 0. Comparing the complete headers confirms this is their only textual difference. The autofix commit itself changes one line in this file.

[Template declaration and storage, lines 109–124](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/ScaledNum.h#L109): IntType defaults to int; SCALE is also IntType. The template supports signed and unsigned integer storage up to four bytes. [Default aliases, lines 1272–1273](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/ScaledNum.h#L1272) are ScaledNum<2048,int> scaled and ScaledNum<2048,uint> uscaled. [floor, lines 241–244](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/ScaledNum.h#L241) returns the integer quotient as int. Its name should not be used to assume mathematical downward rounding for negative values.

For positive valid SCALE and a nonnegative raw value n, quotient q = n / SCALE satisfies 0 <= q*SCALE <= n. Thus n-q*SCALE is the remainder and cannot underflow. Testing that remainder > 0 intentionally detects a fractional part. The rule's generic unsigned-subtraction warning does not establish an error in this specific quotient/remainder identity. No signed cast is needed.

For negative signed values on truncation-toward-zero implementations such as the target compiler, the existing m_i >= 0 guard suppresses the increment; the truncated quotient already equals the ceiling. Both expressions retain that behavior. No C++11 facility or modern library feature is involved.

The supported comparison domain here requires a positive scale represented correctly by IntType and a mathematical ceiling that fits the int return type. Neither expression adds support for unrepresentable int results. The test excludes unsigned scale-1 values above INT_MAX and unsigned scale-2 UINT_MAX for that reason. This assessment does not certify all ScaledNum arithmetic, its callers' range discipline, or malformed/unsupported instantiations.

The internal nature of game values is not itself a proof of arithmetic safety: internally generated values can expose numeric defects too. Here the quotient/remainder reasoning explains why this particular comparison works. No exploit or externally controllable input path was established or claimed.

## Verification

Committed fixture: tests/scaled-ceil/check.py. Obtain both pinned ScaledNum.h files above, then run:
python tests/scaled-ceil/check.py BASELINE_ScaledNum.h AUTOFIX_ScaledNum.h

The fixture extracts the actual floor and ceil method bodies from each input and places them in minimal integer-storage templates with the same typed SCALE. It does not compile the complete engine header.

1,986,550 comparisons passed under g++ -std=c++03 -Wall -Wextra -Werror -pedantic -Wno-type-limits -fsanitize=address,undefined (LeakSanitizer disabled). Coverage includes exhaustive signed/unsigned 16-bit raw values at scales 1,2,3,10,100,2048; signed 32-bit extremes and integer/fraction boundaries; deterministic unsigned/positive signed 32-bit samples; UINT_MAX where its ceiling fits int. The reference uses division/remainder without subtraction/product. Actual header construction, MSVC 7.1, DLL, all downstream callers and gameplay were not tested. No new DLL workflow was added or triggered.

## Coverage decision

UnitStatusEffects is deferred until implementation exists; do not invent status mechanics or queue a build for its README-only head. alert-autofix-1 is recorded as Copilot-generated upstream arithmetic work, assessed explicitly rather than attributed to XANA-bracketed feature code. No production edit is proposed for the alert.

Both final pending inventory rows are resolved as deferred/no-change assessments. Initial scoped rotation has no pending branch rows, but many partial source scopes and unverified native states remain. The global stop gate remains false; initial scoped coverage does not mean exhaustive code review or a successful DLL build for every branch. This report and fixture reuse an existing assistant documentation branch to avoid creating another feature branch.
