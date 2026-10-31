# Headered dynamic-array element lifetime — 2026-10-31

STORAGE-20261031-10. Read-only FSimpleDataStorage source `1b7de3bc31268786c341238ff9ecc2e25640f27e`; reused SimpleStorageChangeDraft-ChatGPT parent `65aa3745ce458b6d2b6764cd2eddb8bd17b05f09`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no original-head changes against global ledger 07bf390e44fca4927d0043d73fa276d45d8aa782. Prior allocation/dimension/const records were consulted; their arbitrary-T lifetime gap is addressed here.

[Scoped correction and fixture 680f29b5edd3694a00cc2f281bc678ad74c7d6fd](https://github.com/SuperXANA/AdvCiv/commit/680f29b5edd3694a00cc2f281bc678ad74c7d6fd).

## Defect and correction

Both FDynamicArray<T> and FDynamic2DArray<T> allocated char buffers, cast the data region to T*, and assigned values without constructing T objects. clear deleted the char buffer without invoking T destructors. A resource-owning T can therefore receive assignment before its object lifetime begins and lose its resources on clear/destruction.

FSimpleDataStorage.h:
- New FStorageConstructArray at line 27 retains the checked byte allocation/eight-byte header and constructs each element with placement new T(defaultValue). The managed pointer is returned/published only after all elements are constructed.
- If copying an element throws during initialization, destroy the constructed prefix in reverse order and free the buffer, then rethrow.
- Both init methods use that helper, at lines 86 and 276.
- Both clear methods destroy live elements in reverse order before existing headered deletion, at lines 75–78 and 264–267.
- Both container copy constructors now clear their completed destination allocation if an element assignment in the copy body throws, at lines 211 onward and 400 onward. A constructor that throws does not otherwise run its container destructor.

The pointer-only storage class layout, count header, flat ordering, byte-overflow checks, dimensions, serialization entry points and primitive values remain. FStaticArray is unchanged. Existing XANA markers remain, and new blocks have dated annotations.

## Verification

Compile from the repository root:

g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -g -ICvGameCoreDLL tests/storage-lifetime/check.cpp -o storage-lifetime-check

Run with ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1.

202 tracked resource/lifetime cases passed against the complete actual header. The resource-owning test type records its live object addresses, owns an int allocation, detects assignment before construction, and injects throwing copy construction/assignment. Both dynamic classes are exercised across sizes 0–8 for init, reads through proxies, independent copying/assignment, reset, clear/repeated clear, failure at multiple initialization/copy positions, source preservation, and caller raw-array ownership handoff. Eight of the cases cover 1D/2D load transfers.

Four independent negative controls restore raw-storage assignment, omit element destruction, omit partial-construction cleanup, or omit failed container-copy cleanup. Each reproduces a lifetime/resource assertion. These are logical lifetime/resource counters, not LeakSanitizer results.

The prior complete-header 120 dimension/allocation/load cases also pass. Existing byte-allocation tests pass 72 native-size_t and 90 explicitly simulated unsigned-32 boundary cases plus their class callers against this revised header. Simulated arithmetic is not a native 32-bit ABI result. Engine stream/XML/delete interfaces remain stand-ins; the fixture's deletion macro frees the original char buffer and nulls the pointer.

## Remaining limits

No MSVC7.1/full DLL, actual engine allocator/delete hooks, actual stream/XML consumers, game or save validation. Arbitrary over-aligned types are not certified: the existing eight-byte header offset/alignment design is retained, not redesigned. Tested resource types fit that alignment. Types must still meet the operations used by a particular API (including copying/default construction where required); destructors are assumed not to throw.

This does not add a strong exception guarantee to reset, assignment or raw load: reset clears old data before allocation, and assignment/load may leave valid partially updated values if element assignment throws. Nontrivial engine stream serialization is not supplied by this patch. Constructor cleanup and tracked logical object lifetimes were verified, not every allocation failure or exception source.

Partial header/template work uses [skip ci]; no native DLL build triggered. Original branches, baseline and independent feature boundaries remain untouched.
