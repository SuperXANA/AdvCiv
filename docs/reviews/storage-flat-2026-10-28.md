# Flat 2D storage copy/load repair — 2026-10-28

Source FSimpleDataStorage: 1b7de3bc31268786c341238ff9ecc2e25640f27e.
Previous isolated head: 09ab0206d861424f9797ae0aaceae90b0319c71f.
Code commit: 80aba592df6f12d4a3e85a615b615bb4a41763ee, SimpleStorageChangeDraft-ChatGPT.

## STORAGE-20261028-02: total size passed as one dimension

FDynamic2DArray::Read (291), copy constructor (342), and operator= (353)
called reset(totalSize). reset takes X and Y, with Y defaulting to zero;
init computes X*Y and returns without allocating for zero. A nonempty copy
then writes through null. Read passes null storage to the stream.

Changed calls at revised lines 297, 346 and 357 to reset(totalSize, 1).
The existing class exposes flat indexing and stores only a total size in
its header and stream. This preserves that format and allocation size.
It does not reconstruct or invent separate dimension metadata.

## STORAGE-20261028-03: an empty load preserved old contents

Read skipped every operation after reading size zero. Loading an empty array
into a populated object therefore retained stale contents. Line 300 now clears
storage for a nonpositive size. Negative counts are treated as empty; no claim
of robust malformed-stream validation or allocation-limit enforcement is made.

## Verification

python tests/storage-flat/check.py passes with g++ -std=c++03 -Wall -Wextra
-Werror -pedantic and ASan/UBSan, UBSAN_OPTIONS=halt_on_error=1.
The actual full header is parsed and its int 2D methods execute against a small
integer-buffer stream and allocation macro stubs. Sizes 0–12 exercise copy,
assignment over populated storage, self-assignment, independent copy mutation,
write/read, repeated load, empty replacement, and trailing stream sentinel.
A 2x3 source verifies preservation of all six flat elements.

The previous header fails the empty-load size assertion. A second negative
control fixes only empty replacement and leaves reset calls unchanged; UBSan
reports a store to null in the copy constructor. These are source-fixture
results, not MSVC 7.1 or full DLL tests.

## Limits / continued coverage

No new branch or DLL workflow; no build was triggered. Original source and
read-only 1.14 remain unchanged. New repairs carry XANA date annotations.

General T lifetime/alignment, size multiplication/allocation overflow, const
get fallback, XML transfer, 1D/static storage lifecycle and real stream ABI
remain outside this scoped test. The separate 1D empty-read path has not been
changed by this 2D repair. No gameplay mechanics or missing implementation
were supplied. Prior findings and missing-implementation skip gates are retained.
