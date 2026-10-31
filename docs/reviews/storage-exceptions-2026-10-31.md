# Static-copy and XML-staging exception cleanup — 2026-10-31

STORAGE-20261031-11 and STORAGE-20261031-12. Read-only FSimpleDataStorage source 1b7de3bc31268786c341238ff9ecc2e25640f27e; reused SimpleStorageChangeDraft-ChatGPT parent fdc705108af59618e0cf474c19222c0038574b9d. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh inventory of 75 branches found no changed original heads against global ledger 6173663f4e80b96817b6d0c59ef7692a64e01648. Existing storage lifetime, ownership and remaining-exception scopes read first. Actual original source blocks and current assistant blocks match for all three affected sites before this change.

[Scoped source and fixture commit 086f2deaf662be610b74ee113db0c92226e0b50a](https://github.com/SuperXANA/AdvCiv/commit/086f2deaf662be610b74ee113db0c92226e0b50a).

## Static-array constructor ownership

FStaticArray's copy constructor calls reset(), which allocates and publishes new T[iSIZE], then assigns default values; it subsequently assigns source values. If either assignment stage throws, the constructor fails and its container destructor does not run. The new array's live objects/resources therefore leak. The prior STORAGE-10 cleanup covered the two headered dynamic copy constructors, not this static-array constructor.

[FSimpleDataStorage.h:536](https://github.com/SuperXANA/AdvCiv/blob/086f2deaf662be610b74ee113db0c92226e0b50a/CvGameCoreDLL/FSimpleDataStorage.h#L536): enclose both reset and the source-copy loop in try/catch. On failure clear the completed allocation and rethrow the original exception. Keeping reset inside the catch boundary is necessary because FStaticArray::init assigns defaults after publishing its pointer. Partial new[] default construction remains handled by the language/runtime. No allocation layout, element values, defaulting or class data members changed.

## XML wrapper ownership

FDynamicArray::readArray and FStaticArray::readArray allocate a local tempArray through the XML interface, then call load. Public load consumes/deletes that raw pointer only on successful transfer. If load throws while creating/initializing/assigning destination elements, its caller still owns the raw array. The wrappers previously unwound and lost that local pointer, leaking every raw element.

[1D wrapper, line 173](https://github.com/SuperXANA/AdvCiv/blob/086f2deaf662be610b74ee113db0c92226e0b50a/CvGameCoreDLL/FSimpleDataStorage.h#L173) and [static wrapper, line 527](https://github.com/SuperXANA/AdvCiv/blob/086f2deaf662be610b74ee113db0c92226e0b50a/CvGameCoreDLL/FSimpleDataStorage.h#L527): catch exceptions from load, delete the wrapper-owned local raw array, and rethrow. Successful load already nulls tempArray, and its success path is unchanged. Public direct load still leaves caller raw ownership intact when transfer fails; it does not silently consume caller data on failure. FDynamic2DArray has no corresponding readArray wrapper in this header and is unchanged.

All 22 pre-existing XANA marker lines remain in order. New blocks have dated annotations. Prior dynamic lifetime, allocation-byte, dimension, empty-data and const-access corrections remain. Pointer-only class layouts, eight-byte header offset, flat ordering, stream format and independent feature boundaries preserved.

## Verification

Compile from the repository root:
g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -g -ICvGameCoreDLL tests/storage-exceptions/check.cpp -o storage-exceptions-check

Run with ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1.

195 tracked exception/resource cases passed against the complete actual header, including:
- Static arrays of sizes 1/2/3/4/8: empty copies, successful independent copies, failure at each default-assignment and source-copy position, and default-construction failures during destination creation.
- Dynamic XML wrapper sizes 1 through 8 and static wrapper sizes 1/2/3/4/8: failures during element copying, default construction and assignment, plus successful transfer values.
- Direct static load failures retain the caller's exact raw pointer/data; caller cleanup releases the remaining raw resources.

Tracked objects own separate heap payloads and register live addresses. After unwinding/explicit destination cleanup, the live set must equal its pre-call ownership baseline, detecting leaked element lifetimes without relying on LeakSanitizer. Four independent negative controls restore the old static constructor, move reset outside its catch, remove dynamic XML-wrapper cleanup, or remove static XML-wrapper cleanup. Each fails a resource-ownership assertion.

The existing complete-header 202 dynamic lifetime/exception/ownership cases and 120 dimension/allocation/load cases also passed under the same strict C++03/ASan/UBSan settings. No warning suppression or leak-detector guarantee.

## Scope and limits

Engine XML/stream interfaces and deletion macros are stand-ins. The original deletion convention is retained, but native engine allocator hooks, actual XML error paths, MSVC7.1/DLL and gameplay are not validated. Exceptions thrown inside SetVariableListTagPair before control returns are outside the new load catch and remain unverified. Zero-size/invalid-size raw handoff contracts also remain queued.

No strong guarantee is added to reset, assignment or public load: these may clear old values or retain valid partially updated destination values on failure. This patch fixes abandoned ownership during construction and wrapper unwinding, not value rollback. T destructors are assumed not to throw. Eight-byte alignment and extreme generic-type contracts remain unchanged.

This is scoped generic-header work with consuming-engine integration still outstanding; an unrelated baseline DLL build would not validate these exception paths. No DLL build triggered or claimed. Code and report commits use [skip ci]. Original source branches and 1.14 were not modified.

## Coverage rotation note

PromotionAltersUnitHPValues and its existing assistant/native report were also inspected without editing. Current convert applies promotions before setDamage; no conversion-order defect was found. maxHitPoints, currHitPoints, setDamage and the constructor/promotion delta paths were read. Nonpositive HP and lowering maximum HP below existing damage still need a coherent damage/death policy; no arbitrary minimum, healing or kill behavior was introduced, and no redundant HP build was triggered.
