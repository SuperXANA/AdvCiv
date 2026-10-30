# Checked 2D storage dimensions — 2026-10-30

STORAGE-20261030-07. Read-only FSimpleDataStorage at 1b7de3bc31268786c341238ff9ecc2e25640f27e; reused SimpleStorageChangeDraft-ChatGPT parent 82b05f776a57fc95cd9ddbd773eddcd23710471e. Complete 75-branch inventory found no changed original heads; prior ledger and storage reports checked. Baseline remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Completed correction

CvGameCoreDLL/FSimpleDataStorage.h:
- New inline FStorage2DSize at 204–211 checks each dimension >0, then verifies X <= INT_MAX/Y before multiplication.
- FDynamic2DArray::init uses it at revised line 226 (original 214).
- FDynamic2DArray::load uses it at revised line 284 (original 272).

The old init/load guards evaluate signed X*Y before checking the result. INT_MAX*2 invokes signed-overflow undefined behavior before the guard; negative pairs such as (-1,-1) produce a positive count and are incorrectly accepted. For load this also permits reset/copy/ownership processing based on invalid dimensions.

Use a shared checked count, returning zero for invalid dimensions or a count beyond the existing int size representation. Valid positive dimensions preserve allocation, flat indexing, defaults and raw-array ownership transfer. Invalid init remains a no-op; invalid load retains the caller's raw pointer and existing managed values. reset retains its existing clear-then-init behavior, so invalid reset leaves the managed object empty. The limits header is included directly; parenthesized numeric_limits<int>::max avoids Windows max macro interference. C++03 syntax only; new block carries paired XANA date markers.

## Verification

tests/storage-dimensions/check.cpp includes the actual complete revised header. Compile from repository root:
g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ICvGameCoreDLL tests/storage-dimensions/check.cpp -o dimension-check
Run with ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1.

120 dimension/allocation/load cases passed for int, double and bool. Small valid grids check filled storage, null rows and raw-array ownership transfer. Invalid/zero/negative/INT_MIN/overflow pairs check fresh/existing init, no-transfer load and reset. Helper-only checks exercise representable INT_MAX products and exact square overflow boundaries without allocating huge arrays.

Original-header negative controls reproduce both the negative-dimension acceptance assertion and UBSan signed overflow for 2147483647*2. Stream/XML and deletion macros are stand-ins; numeric allocation/index/load code is actual. Leak detection disabled as unsupported.

No MSVC7.1/full DLL/game result; no build triggered. Partial header-only draft uses [skip ci]. This covers element-count multiplication, not byte-count overflow in iHEADERSIZE + sizeof(T)*count on 32-bit targets, huge allocation failure, arbitrary T object lifetime/alignment, null caller row-table validity or const static accessor behavior. Those remain separate scopes. No allocation limits or new serialization format invented.
