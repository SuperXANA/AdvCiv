# Partner-specific diplomacy filters — 2026-10-27

## Inputs and scope

Source branch: [PartnerLeaderCivSpecificDiplomacyText at d37d0ca0adcaef748e0c7b32ccd90568dbee05e0](https://github.com/SuperXANA/AdvCiv/tree/d37d0ca0adcaef748e0c7b32ccd90568dbee05e0). All eight source blobs and their XANA blocks were read. No original branch head changed since the preceding coverage snapshot, so this pending branch received the next first pass.

Read-only baseline: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Named workflow source: dll-build at 058e4d0e1760f76195071823d3e2dc85c81b7285.
The isolated build overlays the feature implementation onto the complete baseline, retaining base-only files. Original branches remain unchanged. XANA 03-29-2025 markers are preserved, including the original tag spelling.

This is an independent implementation of the source branch's four partner filters; no LLM diplomacy or other feature branch is merged into it.

## PARTNER-20261027-01 — missing declarations and legacy response ownership

[New CvDiplomacyResponse/CvDiplomacyInfo definitions](https://github.com/SuperXANA/AdvCiv/blob/d37d0ca0adcaef748e0c7b32ccd90568dbee05e0/CvGameCoreDLL/CvInfo_Civilization.cpp#L1280) use four new arrays and expose eight forwarding/accessor methods, but the branch supplies no corresponding CvInfo_Civilization.h changes. The legacy CvDiplomacyTextInfo header declares getters without adding its Response array members, initialization or deletion.

Complete those declarations and storage lifetimes. Append the new data members after existing members so existing field offsets are retained; initialize and destroy every new array. Keep the active response XML loading from the branch and add the corresponding legacy XML list loading against the pinned base. This addresses compile and ownership gaps; preserving field offsets alone is not a runtime ABI certification.

## PARTNER-20261027-02 — new legacy getters check an element instead of the pointer

[The new CvDiplomacyTextInfo getters](https://github.com/SuperXANA/AdvCiv/blob/d37d0ca0adcaef748e0c7b32ccd90568dbee05e0/CvGameCoreDLL/CvInfo_Misc.cpp#L1277) evaluate array[j] == NULL. That already dereferences the array and compares a Boolean with zero, rather than guarding an absent list. Optional filters can therefore be unsafe instead of acting as wildcards.

Check response/index bounds and the array pointer before accessing an element. Apply equivalent release-mode bounds handling to all new active and legacy partner getters. Absent lists return false for each membership query, so the existing Python isUsed logic treats them as unrestricted.

## PARTNER-20261027-03 — legacy leader exports bind the wrong predicates

[Both legacy other-leader exports](https://github.com/SuperXANA/AdvCiv/blob/d37d0ca0adcaef748e0c7b32ccd90568dbee05e0/CvGameCoreDLL/CyInfoInterface3.cpp#L447) point to getLeaderHeadTypes. The positive partner condition and its negation therefore read the ordinary leader mask instead of their own masks. Bind each Python name to its corresponding other-leader accessor. All eight partner exports are checked in the fixture.

The Python filter itself is retained: ordinary Civilization/Leader masks test the trading partner; the four Other masks test the active player. Positive lists allow membership, negative lists veto membership, and independent categories combine with AND. This is response selection, not an AI decision or attitude change.

## PARTNER-20261027-04 — added cache arrays retain the old format flag

The source adds four serialized arrays to [CvDiplomacyResponse's cache stream](https://github.com/SuperXANA/AdvCiv/blob/d37d0ca0adcaef748e0c7b32ccd90568dbee05e0/CvGameCoreDLL/CvInfo_Civilization.cpp#L1433) while retaining flag 0. Old records would be read with the wrong layout.

Write format 1 for the affected response stream and for the legacy text-info container. Format-0 readers skip the added arrays and reset their new pointers to NULL; format-1 readers read them. New absent filters are serialized as explicit false arrays through a small RAII helper, without passing NULL to the external array writer. The legacy stream appends its new arrays after the existing per-response fields; its outer format flag selects that layout.

These are XML-info cache formats, not game-save format changes. The fixture checks versions 0 and 1 with a simulated stream, including reread from new to old and absent-list writes. Real Windows cache-file interoperability and cache invalidation were not exercised; 1.14's normal configuration disables XML file caching. Existing baseline cache behavior for unrelated fields is not certified by these tests.

## Baseline and data decisions

The complete base's diplomacy assets and leader roster are retained. The source's only partner-specific data example is Celestia speaking to Sombra; those IDs are absent from the pinned native roster. Preserve that exact response as inactive tests/partner-diplomacy/source-response.xml rather than loading unresolved IDs or importing an unrelated custom roster. No new live partner restrictions or dialogue lines are activated on the baseline roster.

The source CyInfoInterface3.cpp also predates three unmarked upstream event-binding fixes. The overlay retains 1.14's correct getReligionRequired, isPickOtherPlayerCity and CvEventInfo::getNumUnits bindings. These are baseline reconciliation, not new mod findings.

## Verification

Local checks:

```
python3 tests/partner-diplomacy/check_cpp.py
python3 tests/partner-diplomacy/check_python.py
```

The C++ fixture compiles the actual response declarations, constructors/destructors, new getters, forwarding methods, cache methods and cache helper with strict C++03, -Wall -Wextra -Werror -pedantic, ASan and UBSan. LeakSanitizer is disabled for host compatibility. It uses asymmetric civilization/leader counts, optional and set masks, out-of-range queries, both cache layouts, rereads and NULL-list serialization. Original unrelated response fields are initialized in the fixture; it does not audit every existing legacy selector or cache field.

The Python fixture executes the actual unchanged selection methods with fake game objects. It checks both player axes, allow/deny lists, category combinations, contradictions, attitudes/power, filtering before random selection and no random call when no response/trading partner is eligible. It also verifies all eight binding member pointers, retained upstream binding fixes, optional schema declarations and the inactive source example. It runs under Python 3 as an isolated compatible-method fixture, not inside Civ4's embedded Python or Boost.Python.

The workflow comes from the named dll-build source with the previously validated complete-overlay harness: DLL sync root, protected machine-local Project configuration, stale top-level source cleanup only, root-source manifest, clean outputs, MSVC 7.1 probe, forced rebuild, sequential Release/Debug, exact artifact collection and guarded cleanup.

Native validation is pending for the first published code commit. No historical or fixture result substitutes for the triggered DLL build. Game startup, real XDR loading, embedded Python/Boost conversions, displayed dialogue, cross-version DLL ABI and multiplayer remain untested.
