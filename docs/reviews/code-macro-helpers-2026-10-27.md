# CodeMacroHelpers enum lookup refinement

Source branch: CodeMacroHelpers at d9908667cdc5fddef11a49e3864dfad1ecc47e92.
Read-only complete base: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Build workflow source: dll-build at 058e4d0e1760f76195071823d3e2dc85c81b7285.

## Scope and findings

The changes refine the XANA 03-21-2026 Easy Enum Lookup blocks in
CvGameCoreDLL/CvGlobals.h. The original markers are retained.

1. CvGlobals used CvEnumType before declaring the class and constructed it
   inline before its definition. The proxy also used GC before that macro was
   defined in the header. Forward-declare the proxy, declare the globals method,
   and define it after the complete proxy. Resolve lookups through the declared
   CvGlobals singleton accessor directly.
2. Debug validators expanded DO_FOR_EACH_INFO_TYPE, including integer-indexed
   info classes with no corresponding enum. Generate the overloads only for
   dynamic and static info types that have enum types.
3. The proxy borrowed a const char pointer. Saving a proxy built from a temporary
   string, or changing the caller's string before conversion, could leave a
   dangling or changed lookup name. Own the name in CvString.

The public GET_ENUM and GET_ENUM_HIDE_ASSERT syntax is retained. Prefix checking
remains assertion-based and integer fallback conversions retain their existing
behavior. This is not a strong enum-type safety redesign. Lookup still occurs
when converting the proxy; do not carry proxies across a reload of XML indices.

The selected branch's DLL files are overlaid onto the complete base. Base-only
files remain present. After overlay, CvPlayer.h retains the pinned baseline's
short storage for religion and corporation city counters; the selected branch's
unmarked char widths are unrelated to this helper and would narrow those counts. No game mechanics or save format changes
are intended. The workflow is copied from the pinned dll-build source with only
the rsync source adapted from the sparse branch root to ./CvGameCoreDLL/.

## Verification

Run: python tests/enum-lookup/check.py

The diagnostic compiles the actual proxy block and actual enum macro lists in a
small globals fixture using g++ -std=c++03, both with FASSERT_ENABLE disabled and
enabled. It checks copy/direct initialization, delayed conversion from a temporary,
independence from caller string mutation, missing-name lookup flag forwarding,
and wrong-prefix assertion dispatch.

Both focused configurations passed before publishing. The fixture uses mock
lookup indices and does not validate the complete DLL, XML loading, or gameplay.
The isolated branch's GitHub Actions run is the authoritative DLL build check;
its outcome is recorded in the associated review response.
