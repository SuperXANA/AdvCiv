# Storage native failure paths — 2026-10-31

STORAGE-20261031-13. This correction applies the user's revised no-exceptions requirement to existing assistant work. Source FSimpleDataStorage remains read-only at 1b7de3bc31268786c341238ff9ecc2e25640f27e. Reused SimpleStorageChangeDraft-ChatGPT parent 8fdddb020c1f880e751eb35420c35516f07a07a8. Baseline 1.14 remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Inventory: 75 branches; no changed original feature source heads against the prior global ledger. Newer preference and summon assistant records were consulted and reconciled into the coverage ledger.

[Committed correction 87cd9ba0c0fa3395077200999960c2c1cda061a4](https://github.com/SuperXANA/AdvCiv/commit/87cd9ba0c0fa3395077200999960c2c1cda061a4).

## Why the prior correction is superseded

The assistant added std::bad_alloc and six recovery boundaries to a DLL-facing generic storage helper. Even when a local test could recover, that supplied no recovery contract for Civ4's executable. The original user header contains no such exception paths. The earlier allocation-byte rejection and exception-cleanup recommendations are superseded by this implementation; historical reports remain available as records, not current advice. Exception injection fixtures have been removed from the current tree.

## Completed code

In CvGameCoreDLL/FSimpleDataStorage.h:
- FStorageAllocationSize asserts and returns 0 on invalid/overflowing requests.
- FStorageConstructArray uses std::nothrow allocation, asserts on allocation failure and returns NULL before writing the header or constructing elements. Successful construction/destruction of elements remains explicit.
- Dynamic/static copy paths check the destination allocation before writing it. FStaticArray allocation also uses std::nothrow.
- Direct load returns before copying/deleting caller-owned XML data when destination allocation fails. The local readArray wrappers explicitly delete their staging buffer after load returns, including failed transfer and zero-sized staging.
- Stream reads return before passing a NULL destination to the stream. Static value access returns T() for invalid/missing storage; set/change return without dereferencing it. Static Write asserts and returns if storage is absent.
- No try, catch or throw keyword remains in the production header. All pre-existing XANA lines remain in order, including the original user's marker. Pointer-only class layouts, eight-byte header, flat ordering and successful wire format remain unchanged.

Generic T construction, copying, assignment and destruction must not raise exceptions. C++03 cannot enforce that contract. The patch does not add recovery around arbitrary user-defined element operations or the XML/stream interface.

## Verification

Run from repository root:

```sh
python3 tests/storage-native/check.py
python3 tests/storage-bytes/check.py
```

The complete production header compiles with g++ -std=c++03 -fno-exceptions -Wall -Wextra -Werror -pedantic and ASan/UBSan. 253 native-return/lifetime cases pass. GNU linker wrapping of the standard nothrow array-allocation symbol deterministically returns NULL; production code contains no test hooks. Coverage includes both dynamic classes and static storage, failed initialization/copy/assignment, caller-owned raw retention, wrapper-owned staging disposal, stream payload suppression after failed allocation, normal values and tracked object lifetimes. Four independent negative controls detect invalid byte counts treated as success, a failed-copy NULL write, abandoned raw ownership and lost local staging.

The updated byte fixture passes 72 native-size_t and 90 explicitly simulated unsigned-32 boundary cases plus class caller checks with exceptions disabled. Simulation is not a native 32-bit ABI result. Retained unrelated fixture harnesses define FAssertMsg so they remain compilable; their historical results are not presented as newly executed.

LeakSanitizer could not inspect /proc task state in this environment. It was disabled for the successful ASan/UBSan runs; tracked live-object accounting still passed. No leak-detector result is claimed.

## Limits and next work

No full DLL run was triggered. This branch supplies a standalone storage header and deletion helper, not a consuming engine integration that instantiates these paths. A baseline-only DLL would not validate them. Both publication commits use [skip ci], the GitHub Actions push suppression already used by this repository; current dll-build workflow f77f8a67cd17fdfa9d1c3f443d49005cee04421e was read.

MSVC7.1, actual engine allocation/deallocation hooks, XML/stream consumers and runtime behavior remain unverified. std::nothrow availability/allocator compatibility must be checked in that actual integration. Reset/assignment may leave storage empty after allocation failure. The existing void Read API has no error status: returning avoids a NULL payload write but does not make a partially consumed save safe to resume. A consumer must propagate load failure through its own native status contract before engine use. Reference-returning operators retain an initialized-storage/valid-index precondition; they cannot return NULL or a fabricated element reference. The eight-byte alignment design is unchanged.

The no-exceptions audit here covers this storage feature; it does not certify every independent branch. No other feature code, user-owned branch or baseline was changed.
