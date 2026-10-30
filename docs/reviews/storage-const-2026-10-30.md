# Const static-array indexing — 2026-10-30

STORAGE-20261030-08. Completes the const-static-access scope previously queued in the ledger. Read-only source FSimpleDataStorage 1b7de3bc31268786c341238ff9ecc2e25640f27e; reused SimpleStorageChangeDraft-ChatGPT parent 7f71ac09a6eb9250f65500f137ee0a3e7f2ee64f. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against global ledger 8d6dc5585b79af44cdffc7ae4a3c22317d4e9361.

## Committed correction

CvGameCoreDLL/FSimpleDataStorage.h:418, FStaticArray<T,iSIZE>::operator[](int) const: return T const& instead of T&. The previous return type allows a caller with only a const array reference to mutate its elements. For example, a const reference c to an initialized FStaticArray<int,3> permits c[0]=7, changing the mutable source array. Returning a const reference enforces the intended distinction from the adjacent mutable operator[].

The mutable overload remains T&. Index assertions, storage layout, allocation/ownership, reference lifetime and element values are unchanged. A dated XANA marker identifies the refinement. This does not attempt to make shared underlying storage immutable through other mutable aliases.

## Verification

tests/storage-const/check.cpp includes the actual complete revised header. Build from the repository root:

g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -ICvGameCoreDLL tests/storage-const/check.cpp -o storage-const-check
ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 ./storage-const-check

Stream/XML interfaces and engine deletion/assertion macros are stubs. Nine type/size configurations (int, double, bool; sizes 1,3,8) check initialized mutable writes, const reads/reference identity, overload selection distinguishing const versus mutable references, copying, raw-array load/ownership handoff and reset. All pass strict C++03/ASan/UBSan without warning suppression.

A separate -DMUTATE_CONST build against the original header compiles/runs and changes the array through a const reference. Against the corrected header, it fails compilation with assignment of read-only location. That mode is an expected compile failure for the refined API, not a runnable positive test. Leak detection disabled as unsupported; no leak claim.

This verifies initialized-array access with supported primitive test types, not uninitialized/out-of-range access, arbitrary object lifetime/alignment, exception safety, real stream/XML implementations, native MSVC 7.1, DLL or gameplay. The const-reference overload cannot prevent mutable aliases elsewhere or extend element lifetime after clear/reset/destruction.

## Remaining scope

32-bit byte-allocation overflow and arbitrary element lifetime/alignment remain open in dynamic storage. Complete consuming-engine integration remains unverified. This header-only utility API refinement uses [skip ci]; no native DLL build was triggered or claimed, and no original branch changed. Earlier storage refinements remain intact.
