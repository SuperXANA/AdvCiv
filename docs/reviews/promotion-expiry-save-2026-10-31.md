# Versioned promotion deadline unit persistence — 2026-10-31

EXPIRY-20261031-06. Read-only source PromotionTimedExpireTurns `5f0e1235780e19a81a09aba91234bb0487489fcf`; reused PromotionExpiryDraft-ChatGPT parent `bc405cd9333ec0204f965c4f31c756c2ba3f05cb`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no changed original heads against global ledger 98d3214ad7489a6de53b1572d010820e3734111d. Prior expiry, sentinel and lifecycle reports were read before this persistence follow-up.

[Correction and fixture 4f26fd68d6405c9a45bced3062629ebf15644bc7](https://github.com/SuperXANA/AdvCiv/commit/4f26fd68d6405c9a45bced3062629ebf15644bc7).

## Defect

Baseline CvUnit writes version 8 and ends its data after seven terrain/feature/unit-combat maps. The feature also writes version 8 but appends m_aiPromotionExpireTurns. Its read function unconditionally consumes that new field in both the >=7 map path and the older readArray path. Therefore loading a baseline unit consumes subsequent object data as deadline-map bytes, displacing the stream. Conversely, the unchanged baseline reader cannot recognize the feature's extra field under the same version.

## Correction

CvGameCoreDLL/CvUnit.cpp:
- read: after the unchanged baseline seven-map reader tail, read the deadline map only when uiFlag>=9 (line 10701). For earlier versions reset it to its existing numeric-zero default (line 10703), including when the destination object previously held deadlines.
- write: emit uiFlag=9 (line 10720), retaining the existing historical version-8 comment. The existing appended map write is unchanged.
- remove the unconditional deadline read/readArray calls from the older map branches.

The corrected old-version seven-map tail before the new gate matches the pinned baseline tail exactly. EnumMap.h was read and documents reset() as restoring the map's default; this numeric map defaults to zero. The earlier expiry-sentinel correction treats zero as no scheduled deadline. No deadline is invented for a save that never stored one.

Original feature XANA markers and previous lifecycle/sentinel changes remain. New gate/version lines have dated ChatGPT markers. No compact storage type, duration arithmetic, promotion ownership or expiry mechanics change in this patch.

## Verification

Run `python tests/promotion-expiry/save-check.py`. It extracts the actual CvUnit reader tail, actual writer version statements and actual writer tail. The surrounding unit fields, engine stream and map serializer are stand-ins. The map stand-in uses counted int payloads for modern maps and fixed three-int payloads for legacy arrays; this deliberately is not the real compact EnumMap encoding.

245 C++03/ASan/UBSan cases passed across versions 6–9, seven payload sizes, five value seeds and four version-9 deadline payload shapes (empty, infinite -1, zero, positive including 32767). Tests cover the seven existing map payloads and modern/legacy read dispatch, zero deadline-map reads and one reset for old versions, version-9 map reads, stale destination state, three trailing sentinel values, and exact rewritten version-9 host bytes.

Negative controls independently restore the old reader or writer flag. Restoring the ungated deadline read fails the end-of-unit stream-position assertion on a baseline-format fixture. Restoring version 8 fails the emitted-version assertion. No corrupted engine save or runtime recovery behavior was tested.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`, ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Compatibility limits and next scope

Previously produced feature saves marked version 8 already contain the new map but cannot be distinguished from baseline version 8 by that flag. They are not migrated or supported by a heuristic decoder. Corrected version-9 saves require this feature reader and are not expected to load in unchanged baseline DLLs. This is a structural fix toward baseline-save loading, not certification that complete real saved games load successfully.

No full CvUnit translation unit, MSVC7.1/DLL, actual EnumMap byte encoding, engine save, promotion-ID remapping, XML/cache, multiplayer or gameplay validation. Whole legacy unit read paths outside the extracted tail are untested. Compact short deadline range, positive duration arithmetic overflow and scaled-to-zero turn-zero ambiguity remain queued. Existing int-map timing fixtures are not native short-map validation.

Partial draft uses [skip ci]; no DLL run triggered or claimed. Reuse PromotionExpiryDraft-ChatGPT for remaining integration.
