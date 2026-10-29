# One-dimensional empty replacement — 2026-10-29

Source assistant head SimpleStorageChangeDraft-ChatGPT 540b0f094b81ef8b41f425ca50630e516dc0f76b; original FSimpleDataStorage remains 1b7de3bc31268786c341238ff9ecc2e25640f27e. No user source changes at inventory.

STORAGE-20261029-04: FDynamicArray::Read, FSimpleDataStorage.h:111–121. A zero count performed no replacement, leaving the prior destination contents visible. Add clear() in the nonpositive-count branch, matching already-refined 2D read behavior. Wire format unchanged; negative count treatment is clearing, not certification of corrupt-save handling.

STORAGE-20261029-05: FDynamicArray::operator=, lines 180–196. Assigning an empty source called reset(0), whose deliberate default behavior reinitializes using the destination's existing size. Explicitly clear for an empty source; retain reset(size) for populated sources and self-assignment guard. Do not change reset() semantics globally.

Validation: actual complete revised header compiled under strict C++03 with ASan/UBSan, instantiating scalar int 1D copy/assignment/read/write. Sizes 0–12, deep copy independence, populated-to-empty assignment, self-assignment, stream sentinel, repeated reads and explicit empty stream replacement checked. Stream/XML/allocation macro dependencies are stubs; arbitrary nontrivial T, actual engine serialization and MSVC DLL not tested. Original header fails empty-source assignment assertion in same fixture.

Reuse existing feature draft; no new branch or DLL build. Commit skips CI. Prior findings retained. Tests: tests/storage-empty/check.py; run with python3. Scope limitations remain: get returns an invalid reference for out-of-bounds access, const correctness, overflow/allocation/alignment/lifetime issues, and other feature integration. No unrelated API redesign here.
