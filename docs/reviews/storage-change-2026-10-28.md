# Simple storage change dispatch — 2026-10-28

Source FSimpleDataStorage at 1b7de3bc31268786c341238ff9ecc2e25640f27e.
Code https://github.com/SuperXANA/AdvCiv/commit/4c08ef06e1a95f2b5b093fcc2e6142fc5e419a45.
Read-only 1.14 remains 5970334b64a875b5cdb370c94fc9a98db4eacda6.
This is an implemented generic storage helper, not a missing game mechanic. Its existing defects can be repaired without inventing feature rules.

## STORAGE-20261028-01 — bool specialization collides with bool overload

[FDynamicArray::change, line 87](https://github.com/SuperXANA/AdvCiv/blob/4c08ef06e1a95f2b5b093fcc2e6142fc5e419a45/CvGameCoreDLL/FSimpleDataStorage.h#L87),
[FDynamic2DArray::change, line 257](https://github.com/SuperXANA/AdvCiv/blob/4c08ef06e1a95f2b5b093fcc2e6142fc5e419a45/CvGameCoreDLL/FSimpleDataStorage.h#L257),
[FStaticArray::change, line 423](https://github.com/SuperXANA/AdvCiv/blob/4c08ef06e1a95f2b5b093fcc2e6142fc5e419a45/CvGameCoreDLL/FSimpleDataStorage.h#L423).

Each original class declares change(int,T) and change(int,bool). For T=bool these become duplicate member signatures, so bool arrays cannot instantiate.

The repair uses one templated change method per class and a small C++03 partially specialized FStorageChange helper at lines 14–22. The bool argument specialization assigns static_cast<T>(value), preserving the source's existing flag-assignment overload behavior even for numeric arrays. Other argument types are converted to T before addition, retaining the previous delta conversion order. For example, int storage changed by -0.5 adds zero, rather than adding a floating delta to the existing value before truncation.

This preserves ordinary call-value behavior; it does not promise source compatibility for code taking pointers to the old non-template member overloads. No such callers were established in this sparse source branch. Arithmetic overflow, enum arithmetic and arbitrary custom element types are not addressed here.

## Ancillary parse repair

The dynamic array allocation casts have an unmatched opening parenthesis in the supplied header. The two assignments now use m_pArray = reinterpret_cast<T*>(pBuffer + iHEADERSIZE), at new lines 45 and 219. This is required to parse the full header for the dispatch fixture. Other previously reported storage concerns are not presented as new findings or silently rewritten.

Existing source notes are retained. New helper delimiters use a dated ChatGPT XANA marker. No production allocator, header size or wire format changes in this pass.

## Verification

python tests/storage-change/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. LeakSanitizer disabled; UBSan halt_on_error enabled.

The test includes the actual complete repaired header and instantiates static, dynamic and two-dimensional arrays of bool and int. It checks bool assignment/reset, int-array bool assignment rather than increment, positive/negative numeric increments, and numeric conversion before addition. Dynamic checks use the existing proxy accessors, not the unresolved get reference fallback. Array construction/init/destruction exercised here use only trivial bool/int types.

FDataStreamBase, CvXMLLoadUtility, assertions and allocation/deletion macros are stubs. The actual source CvMemoryManager.h was read to compare headered deletion: it deletes the original char buffer and nulls the data pointer. The fixture's equivalent deletion macro does not establish actual engine allocator behavior.

Two-dimensional shape/copy/reset/read paths, stale data, const/reference accessors, arbitrary element lifetime/alignment, allocation-size overflow, caller integration, XML traversal, real streams, MSVC 7.1, DLL and gameplay remain unverified. No workflow or DLL build was triggered. A full build of an otherwise unused header would not by itself validate its template instantiations.

## Coverage

No existing matching assistant branch was present, so the scoped proposal uses SimpleStorageChangeDraft-ChatGPT, descending from the unchanged original source and retaining both original headers. FSimpleDataStorage stays partial. This records the first committed refinement for this source, separate from earlier source-only observations.

Fresh inventory showed no original source-head changes; CivicScroll's difference was already-delivered coverage reconciliation. The four recorded missing-implementation skips remain in effect. Other partial reviews and failed/unverified native states remain; stop gate false.
