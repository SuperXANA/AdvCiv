# Checked headered-array allocation bytes — 2026-10-30

STORAGE-20261030-09. Read-only source FSimpleDataStorage `1b7de3bc31268786c341238ff9ecc2e25640f27e`; reused SimpleStorageChangeDraft-ChatGPT at `7959c9f435da6dd47a7b863b6928c6d12a5675a2`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory found no changed original heads versus global ledger bdeb212cc0f21d71b3509cc21c9fa96539f88f21. Prior storage allocation/flat/dimension/const reviews were read before this follow-up.

## Correction

[Code and fixture 07f6e24a84c4f9755b1fc68e31992788a2246163](https://github.com/SuperXANA/AdvCiv/commit/07f6e24a84c4f9755b1fc68e31992788a2246163).

In FSimpleDataStorage.h, FDynamicArray::init and FDynamic2DArray::init previously allocate `new char[iHEADERSIZE + sizeof(T) * iSize]`. Checking a positive int element count (and the previously fixed X*Y count) does not prove that the byte count fits the target's 32-bit size_t. Unsigned arithmetic wraps: with four-byte int, INT_MAX elements request only 4 bytes; with eight-byte double, 536870911 elements request 0 bytes. The header/data initialization then exceeds that allocation.

Add FStorageAllocationSize at revised lines 14–22. It compares the count with `(max_size_t - iHEADERSIZE) / element_size` before any multiplication or addition, throwing std::bad_alloc when unrepresentable. Both actual allocation expressions use it at revised lines 57 and 244. The standard allocation-failure exception prevents reset/load/Read callers from continuing with absent or undersized storage; a silent return from init would not provide that guarantee. Direct <cstddef> and <new> includes supply the C++03 types/exception. Parenthesized numeric_limits::max avoids Windows max macros.

Existing nonpositive/existing-array init guards, eight-byte header, stored count, storage class layout, encoding and original XANA notes remain. New helper has paired dated XANA markers. Valid representable allocations retain their behavior. Huge representable allocations can still fail normally. As before, reset clears old storage before allocation; this does not add strong exception safety or promise to retain managed data after allocation failure. A rejected load leaves the caller's raw allocation owned by that caller because deletion is never reached.

## Verification

Run `python tests/storage-bytes/check.py`. The fixture includes the complete actual revised header with engine stream/XML/delete/assert stand-ins. It passed strict C++03/ASan/UBSan in two modes:

- 72 native-size_t arithmetic boundary cases.
- 90 simulated unsigned-32 boundary cases, generated from Python arbitrary-precision expected byte counts. The identical helper/body and class callers are compiled after substituting only the helper's std::size_t type with unsigned int. This is explicit arithmetic simulation, not a native 32-bit ABI result.

The class checks cover small default values, copies and raw-array load/ownership; simulated-32 checks also exercise fresh oversized 1D/2D init, existing-init no-op, oversized reset, raw ownership on rejected 1D/2D loads, rejection before stream payload reads, and subsequent recovery with small allocations. No huge allocation is attempted.

A separate negative probe extracted both original allocation expressions and evaluated them with unsigned-32 sizeof arithmetic: INT_MAX ints produces 4 bytes; 536870911 doubles produces 0. The revised boundary cases reject those requests. The prior complete-header 120 dimension/allocation/load cases also passed unchanged.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim. A real `g++ -m32` probe is blocked by missing 32-bit C++ headers (bits/c++config.h); no native 32-bit/compiler claim is made.

## Remaining scope

No full MSVC7.1/DLL/engine allocator/XML/stream/game validation. Arbitrary T lifetime/alignment, allocation exceptions beyond this overflow check, caller exception handling and consuming-engine integration remain open. No user feature implementation or serialization policy invented. This unused-template/header scope uses [skip ci]; no DLL workflow is triggered.
