# Sid tips localization integration — 2026-10-31

## Changed source and committed integration

SidSaysPatch changed from `3171a91bd8b595781f624d94ee14d3f2552ac9e7` to `7d0ec96d4dc52b7534e376018a97cd10e8469fff`. The two new commits add only Assets/XML/Text/CIV4GameText_Misc1_mlp.xml; its CvGameCoreDLL files are unchanged. The authored [TXT_KEY_SIDS_TIPS record at line 529](https://github.com/SuperXANA/AdvCiv/blob/7d0ec96d4dc52b7534e376018a97cd10e8469fff/Assets/XML/Text/CIV4GameText_Misc1_mlp.xml#L529) provides English, French, German, Italian and Spanish labels.

The existing SidSaysDiscoveryBuild-ChatGPT branch is reused. [Asset commit 33eb4651a21eaa4d28c51d946f558f6768d97112](https://github.com/SuperXANA/AdvCiv/commit/33eb4651a21eaa4d28c51d946f558f6768d97112) copies that file using its exact Git blob, preserving every authored entry and the XANA attribution comment. English is `[COLOR_HIGHLIGHT_TEXT]Sol's Tips: [COLOR_REVERT]`. No translation or unrelated rank/feat/diplomacy entry was rewritten.

This is an asset integration, not a new C++ correction. The CvGame scheduling hooks, read-only diagnostic locator, assertion debugger and actual build workflow remain unchanged. Original branches and read-only 1.14 remain unchanged. No merge or new branch was used.

## Source-grounded loading path

Pinned baseline [CvXMLLoadUtility::LoadGlobalText at line 501](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvXMLLoadUtilitySet.cpp#L501) enumerates `xml\\text\\*.xml`; the authored filename matches this pattern. [SetGameText at lines 1178–1180](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvXMLLoadUtilitySet.cpp#L1178) reads CvGameText and registers its key/value with gDLL->addText. Thus the asset targets the ordinary localization path directly.

The baseline [load-order comments at lines 554–578](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/CvXMLLoadUtilitySet.cpp#L554) explicitly preserve enumeration order for mod overrides and state that the first definition wins. Static XML validity therefore does not establish which definition wins in an installed game containing other definitions. Enumeration/addText are executable interfaces; their actual installed file order was not observed. Where global-text caching is enabled, the early cache return at lines 484–491 is also part of a fresh-load test.

Literal discovery's lack of a match cannot by itself prove that executable function modification is necessary. This supplied localization key offers a separate data-driven evaluation path; no function address or memory write is proposed here. Existing discovery diagnostics are retained.

## Verification and limits

The complete added file parses as namespace-qualified Civ4GameText with 26 TEXT records and 26 unique, nonempty keys. Exactly one record is TXT_KEY_SIDS_TIPS. All five language values exist; each retains exactly COLOR_HIGHLIGHT_TEXT and COLOR_REVERT in order, with no printf argument. File bytes are ASCII, a valid subset of the declared ISO-8859-1 encoding; numeric character references parse successfully. The XANA comment is retained. The imported Git blob is identical to the selected user source.

These are Python XML/structural checks, not the game's XDR parser, actual text registration, duplicate resolution, language selection or live tips rendering. They do not certify the broader meaning of the other 25 authored entries or supply missing translations.

[Machine-readable evidence](sid-tips-xml-2026-10-31.json) records the file hash, exact pins, values and verification limits. No test fixture or DLL source change was needed for this reversible asset copy.

No DLL build was triggered: compilation cannot validate a text asset's installed loading/UI behavior. The commit uses [skip ci]. Prior DLL validation remains tied to exact commit `770e9e4f0984f3099b7eaa8c261bbaa51a1e0756` and [run 41255403884](https://github.com/SuperXANA/AdvCiv/actions/runs/41255403884); it is not presented as validation of the new XML.

Next useful evidence is a fresh BtS text load with this file installed at Assets/XML/Text and observation of the strategy-tip heading in the selected language. If the old heading remains, inspect competing definitions and loading/cache behavior before considering any executable patch.
