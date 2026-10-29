# Storage read getter return contract — 2026-10-29

STORAGE-20261029-06. Reuse SimpleStorageChangeDraft-ChatGPT at7634ca04cbd7c32302c3d1556a0adbdfae0dff1b; original FSimpleDataStorage remains1b7de3bc31268786c341238ff9ecc2e25640f27e.

FDynamicArray::get at FSimpleDataStorage.h:71 and FDynamic2DArray::get at244 returned T& from const methods, yet their invalid-index fallback returned temporary T(). Standard C++03 rejects instantiation for int/double/bool; a temporary cannot safely back a returned reference. Return T by value, matching existing FStaticArray::get. Preserves values and default-zero fallback while preventing mutation through these read methods.

Source compatibility: external callers attempting get(i)=value or binding a mutable reference must use existing set/change or mutable proxy access. Supplied original feature tree consists of this header, CvMemoryManager.h and README, not integrated engine consumers; no blanket claim that all external callers are compatible. General nontrivial T copying and storage lifetime remain outside verified scope. Object layout/wire format unchanged; no reference fallback shared mutable dummy introduced.

Actual complete revised header passed strict C++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan for scalar int/double/bool. Empty containers, indices-2..5 around size3, valid reads, const reads, independent value snapshot and retained set/proxy writes checked. Dependencies are stream/XML/allocation-macro stubs. Original header fails the same six template instantiations with cannot-bind-reference-to-rvalue errors. No native MSVC7.1/DLL/game result. Partial draft [skip ci].

Prior repairs retained; independent feature boundaries and user originals preserved. tests/storage-get/check.cpp can compile directly from repository root with g++ using usual strict flags.
