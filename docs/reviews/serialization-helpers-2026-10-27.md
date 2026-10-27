# Serialization helpers review — 2026-10-27

Source: SerializationHelpers at 2be6010dc6787a717c851cd125e005010cf71450.
Read-only base: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Workflow: dll-build at 94e1a9ae4892d0524337fc76fe2ad411f403f0c5.

## Defect and repair

CvDataStream::Write(const TCHAR*) forwards a pointer to FDataStreamBase::Write, which has primitive overloads but no string overload. The pointer converts to bool, losing the text. Read(TCHAR*) similarly selects a primitive character read instead of decoding a string.

Delegate both legacy wrapper overloads to the existing WriteString/ReadString API. Add explicitly named owning std::string and std::wstring overloads so callers can avoid guessing output buffer capacity. The legacy buffer read retains the base API's requirement that callers allocate a sufficiently large destination.

Retain enum values as int, including negative sentinel values; retain the existing enum-trait compile-time check and null-stream behavior. This wrapper does not perform runtime enum-domain validation.

## Integration and validation

Overlay the repaired helper and include onto the complete pinned base; restore unrelated older-header differences and retain base-only files. The copied workflow changes only the rsync source directory to ./CvGameCoreDLL/ for this layout. No EXE-facing FDataStreamBase virtual interface is changed.

Focused C++03 tests compile the actual repaired helper against an overload-sensitive mock stream, in narrow and wide TCHAR configurations. They verify string codec dispatch, a trailing integer, empty and owning strings, and negative/positive enum values. The fixture's static-assert stub emits unused-typedef warnings; these tests are not DLL validation.

The full DLL result is the Actions run matching this branch's exact commit. A successful build parses the included wrapper but does not demonstrate a Civ4 save/load round trip or instantiate every future enum type. Runtime persistence testing remains necessary.

No existing save format is deliberately migrated: any caller that already wrote strings through the broken wrapper must version its affected record when adopting the corrected codec.

## Coverage

This pass covers SerializationHelpers and its primitive/string/enum forwarding against the pinned FDataStreamBase interface. Prior reviewed areas: team-size attitude, timed promotions, per-combat upgrade costs, and leader-specific UWAI aspect weights.
