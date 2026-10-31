# Full-width promotion deadlines — 2026-10-31

EXPIRY-20261031-07 (deadline width and versioned codec), EXPIRY-20261031-08 (empty-payload reset), EXPIRY-20261031-09 (promotion debug-help pointer/formatting), EXPIRY-20261031-10 (baseline AI caller compatibility). Read-only original PromotionTimedExpireTurns 5f0e1235780e19a81a09aba91234bb0487489fcf; existing PromotionExpiryDraft-ChatGPT reused from 0c3c76cf0374bb0e27ca3d2af30ea607bb0dbca8. Read-only baseline 1.14 pinned at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory has no original source changes against the preceding global ledger f1d3125c0f35dff4c4a144c63a66d9437a270acd. Prior expiry/sentinel/lifecycle/persistence reports were read; this covers their still-open compact-storage scope.

[Width and codec correction c9452a8ca970330846ea85c24e416b2a09a98292](https://github.com/SuperXANA/AdvCiv/commit/c9452a8ca970330846ea85c24e416b2a09a98292).
[Help-text correction a6e3652786017f274911abbeee01f65e299a680d](https://github.com/SuperXANA/AdvCiv/commit/a6e3652786017f274911abbeee01f65e299a680d).
[Verified fixture follow-up 3c4eb4a8a5887a1ab39a794be0045f916c351b02](https://github.com/SuperXANA/AdvCiv/commit/3c4eb4a8a5887a1ab39a794be0045f916c351b02).

## Deadline representation and save version

CvUnit.h:1217 stored m_aiPromotionExpireTurns as ArrayEnumMap<PromotionTypes,int,short>. Both getter and setter expose int absolute game turns, but CompactV controls the actual stored values, not just the disk encoding. 32768 cannot fit a signed short; on the target representation it becomes negative, causing doExpireTempPromotions to skip it under the existing nonpositive-sentinel check. Larger values can also wrap to an earlier positive deadline. This is distinct from duration arithmetic overflow.

Change only that map's compact value type to int. Numeric default zero and infinite-duration -1 remain. No class member is added and no maximum lifetime, saturation, healing or expiry policy is invented. Original XANA/XABA boundary comments and earlier assistant corrections remain.

The actual baseline EnumMap.h:1403–1441 writes a bool for any nondefault value followed, when true, by its compact value array; it does not encode the array length. Changing short to int therefore requires a new unit payload version:
- Current writer emits version 10 at CvUnit.cpp:10737 and writes the int map at its existing tail position.
- Reader uses the int map for version >=10.
- Version 9 reads a temporary ArrayEnumMap<PromotionTypes,int,short>, then copies the signed values by promotion ID into current storage.
- Versions <=8 consume no deadline payload and retain numeric-zero defaults, as in the previous correction.

The seven existing unit-map reader operations remain unchanged. Version-9 signed data is preserved as stored; previously truncated values cannot be reconstructed into their intended original deadlines. Pre-existing unversioned feature-v8 saves remain ambiguous/unsupported. The promotion info count/order must still match the saved map. This feature's version 10 is not an integration contract with independent feature branches.

## Empty-payload reset

Baseline ArrayEnumMap::read only overwrites values when its bool marker is true. A false/empty payload leaves an already allocated destination unchanged. Reset the deadline map before all version dispatch at CvUnit.cpp:10707. This prevents an empty modern payload from retaining deadlines when an object is reused. The temporary version-9 map begins with its normal zero default.

## Help-text defects exposed by native build

The first native build reaches existing XANA debug-help code in CvGameTextMgr.cpp:599–604:
- pUnit is a pointer, so .getPromotionExpireTurn fails C2228; use ->.
- append('') is an invalid empty character literal, producing C2137/C2668; restore the pinned baseline's append(' ') separator.
- szTempBuffer is CvWString, whose append(pointer, integer) is a string-length overload, not printf-style formatting. Passing L"(%d)" and remaining turns can append literal/truncated text or read beyond that literal. Append CvWString::format(L"(%d)", remaining) instead.

The revised block shows a suffix only for a positive finite deadline at or after the current game turn. Zero and negative sentinels produce no countdown; the existing Alt/debug gate is unchanged. Current gameplay turn values are assumed nonnegative, as in the surrounding engine API. No general negative-turn arithmetic contract is introduced.

## Focused verification

python3 tests/promotion-expiry/width-check.py (save-check.py now delegates to it) extracts the actual map declaration, getter/setter, complete expiry method and reader/writer tail/version statements. 405 strict C++03, -fno-exceptions, ASan/UBSan cases pass. They cover positive deadlines up through INT_MAX, expiry before/at deadlines, versions 6–10, promotion counts 0/1/2/5, old short versus new int widths, empty/nonempty payloads, stale destinations, trailing stream sentinels and rewrite/reload to version 10. Four negative controls independently restore short storage, read version 9 as int, omit reset or restore writer version 9; each fails.

The reduced map model follows the actual bool-plus-current-length compact-array algorithm but is not the full EnumMap template. Other seven maps and the engine stream/unit are stand-ins. The new fixture supersedes the old int-only codec fixture; its old 245-case count is historical and is not added to the new result.

python3 tests/promotion-expiry/help-check.py extracts the actual revised countdown block. 49 C++03/-fno-exceptions/ASan/UBSan cases pass with reduced game/unit/string interfaces. Replacing formatted append with the old length-based append fails. This tests suffix text, not the complete help routine or engine rendering. A fixture-only statement-boundary issue was corrected in the follow-up before the successful checks; no warning suppression was used.

LeakSanitizer is disabled in the focused runs; no leak-detector or real-save execution result is claimed.

## Full native validation

Start with complete baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6, overlay all seven selected branch DLL files, retain all baseline-only files, and preserve the existing assistant reports/tests. The prepared tree restores 862 baseline-only repository files. Copy actual dll-build workflow f77f8a67cd17fdfa9d1c3f443d49005cee04421e unchanged except for the three exact provenance pins. Scope-only commits use [skip ci].

First tested commit 1cc42f0f355f13d73bcd8e7d49b7bb480f538672, selected source c9452a8ca970330846ea85c24e416b2a09a98292, run https://github.com/SuperXANA/AdvCiv/actions/runs/41240448923:
Both Release and Debug failed with 0 warnings/6 errors. Actual extracted Build.log files show C2228 twice (CvGameTextMgr.cpp599/600), C2137 and C2668 at604, plus nmake/MSBuild failure wrappers. All four ZIPs were downloaded/extracted: Release log13057112725/diagnostics13057267254, Debug log13056644436/diagnostics13056813990. Exact pins, timing logs and identical 349-file manifests verified; digest 8077f059a6aad6fa5b9b870d8fd942d8298541552d24050807c1a349adce74d6. No DLL produced. This failed early result does not validate the new map body.

Second tested commit c6a28db9227b49913d340a02d99951a8992add23, selected source 3c4eb4a8a5887a1ab39a794be0045f916c351b02, run https://github.com/SuperXANA/AdvCiv/actions/runs/41240717223:
Both configurations got past the corrected help text, then failed CvUnitAI.cpp:519 C2660: CvUnit::upgradeXPChange does not take zero arguments (0 warnings/3 errors including wrappers). All four ZIPs extracted and Build.log/BuildTiming/pins/manifests verified: Release log13056499116/diagnostics13057411526, Debug log13057271830/diagnostics13057670975; manifest digest aa724e3ec167f0309afd50e986d4a4677ce2912d9320638c4691027e349dc0d1.

Actual pinned baseline declares upgradeXPChange(UnitTypes eUnit = NO_UNIT); supplied feature CvUnit.h:279 omits that default, while its definition does not use the parameter. Restore only the baseline default argument, preserving the feature signature/body and marker comments. This is a baseline compatibility repair in this independent overlay, not an import from the HP feature. [Correction 68b02fd7884f1e6e3f646740f12f8cbbd91db7dd](https://github.com/SuperXANA/AdvCiv/commit/68b02fd7884f1e6e3f646740f12f8cbbd91db7dd).

Final selected source 68b02fd7884f1e6e3f646740f12f8cbbd91db7dd; tested commit 0c9a61c50e70378d4296ba556077a1d77517bf7e; run https://github.com/SuperXANA/AdvCiv/actions/runs/41241007281

Both final matrix jobs completed successfully:
- Release job124654715854 and Debug job124654715732; actual probe output in both confirms _MSC_VER == 1310 (MSVC 7.1).
- Actual extracted MSBuild Build.log files report Build succeeded, 0 Warning(s), 0 Error(s).
- Both DLLs verify as PE32 x86 DLLs; Debug PDB is present.
- All four final ZIPs extracted and inspected, in addition to the eight failed-attempt ZIPs (12 total).

| Configuration | DLL/log artifact | Source diagnostics | DLL bytes | PDB bytes |
| --- | ---: | ---: | ---: | ---: |
| Release | 13056884920 | 13058055090 | 6,569,984 | — |
| Debug | 13057487073 | 13057392275 | 25,206,784 | 70,675,456 |

SHA256:
- Release DLL: 6ca934c8810f048aa1f324b99f5ea47c319d789869b3bbfd33991443bc23b94b
- Debug DLL: 62c78e156e848d4c14ed97dcf233e45aa20458513a653001a796f93a964cf044
- Identical Release/Debug 349-file source manifests: 123b2e4360109a416902e4c4b6308ccfdd25adad55475997f00d09a6419f76f7

All expected/actual manifests match byte-for-byte, diff files are empty, verification status is passed, and recomputed digests match both provenance fields. Exact tested/source/baseline/workflow/configuration pins and BuildTiming logs were checked for every configuration in all three attempts. The successful manifest's CvUnit.cpp and CvUnit.h entries were independently checked against the local published source. Complete-tree verification found all baseline files present, exactly seven feature DLL paths, 362 DLL blobs total and zero unexpected baseline-only DLL modifications.

This is full compilation/linking of the corrected isolated overlay. It does not execute serialization or prove real save compatibility.

## Remaining limits

Actual engine saves, promotion-ID/count migrations, XML/schema/cache behavior, complete event application, UI rendering and gameplay/multiplayer remain unverified. The map change prevents representable int deadlines from being narrowed, but existing positive-duration multiply/divide/add arithmetic can still overflow before calling the setter. Correct handling of unrepresentable durations and positive durations scaled to zero at turn zero still needs a coherent native failure/timing policy; no arbitrary cap or guessed migration is included.

A previously removed original inline XANA infinite-duration note is restored beside the nonpositive deadline guard in the final comment-only publication. This retains the corrected zero/infinite behavior. The tested commit precedes this annotation-only change; its exact source hashes remain recorded above.

Original source and 1.14 remain unchanged. No exception recovery, independent feature merge, binary artifact or full runner log was added to the repository.
