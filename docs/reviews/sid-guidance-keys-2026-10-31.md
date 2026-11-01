# Solais guidance option keys — 2026-10-31

Reviewed SidSaysPatch source: `b6abf837c8b756c023246a42ac2b4e8243e4a80d`, after `7d0ec96d4dc52b7534e376018a97cd10e8469fff`. Reused SidSaysDiscoveryBuild-ChatGPT parent `89b417f5aa3f93e80506835953651146bd853b3d`. [Committed asset update e960bff4f5d418abfb0b4e23c4f34814f71586be](https://github.com/SuperXANA/AdvCiv/commit/e960bff4f5d418abfb0b4e23c4f34814f71586be).

## Completed integration

The three changed XML files are incorporated using their supplied paths and XANA comments. The later authored file organization is preserved: the heading now resides in Civ4GameText_advc_OptionsScreen_mlp.xml; the advisor option label resides in CIV4GameTextInfos_mlp.xml; the help description resides in CIV4GameText_Misc1_mlp.xml.

| Key | Source location | Updated English |
| --- | --- | --- |
| TXT_KEY_SIDS_TIPS | [OptionsScreen line 529](https://github.com/SuperXANA/AdvCiv/blob/b6abf837c8b756c023246a42ac2b4e8243e4a80d/Assets/XML/Text/Civ4GameText_advc_OptionsScreen_mlp.xml#L529) | Solais' Guidance: (existing highlight/reset markup preserved) |
| TXT_KEY_PLAYER_OPTION_ADVISOR_HELP | [GameTextInfos line 1299](https://github.com/SuperXANA/AdvCiv/blob/b6abf837c8b756c023246a42ac2b4e8243e4a80d/Assets/XML/Text/CIV4GameTextInfos_mlp.xml#L1299) | Solais' Guidance |
| TXT_KEY_PLAYER_OPTION_ADVISOR_HELP_HELP | [Misc1 line 15](https://github.com/SuperXANA/AdvCiv/blob/b6abf837c8b756c023246a42ac2b4e8243e4a80d/Assets/XML/Text/CIV4GameText_Misc1_mlp.xml#L15) | Strategy advice attributed to Solais a Tuath and Histories of Civilization; the authored description of AI recommendations is preserved. |

The two new file blobs are copied exactly. The only assistant text correction is the book-title spelling at Misc1 line 16: Civiliation becomes Civilization. The rest of that file's bytes, all original translation content and XANA comments are unchanged. No additional lore, translations or attribution policy is invented.

The project's established _mlp.xml override convention is accepted as verified project behavior. Inherited file-level text-key collisions are not an open concern or blocker for this work. The earlier static-review qualification is updated accordingly; no new claim of independently repeating a live game test is made.

## XML checks

All three actual source blobs were verified against their Git blob IDs before editing. They parse under their declared ISO-8859-1 encoding. The changed files contain 188 TEXT records, 187 distinct keys and all five language elements for each record. An existing identical duplicate for TXT_KEY_DENIAL_MINORITY_RELIGION is retained; this is not treated as a conflicting override or changed finding.

Each of the three target keys occurs exactly once across the three files. Every heading translation retains the same COLOR_HIGHLIGHT_TEXT/COLOR_REVERT pair in order and no formatting argument. The title correction is the only semantic/byte delta from the selected user files. The existing ISO-8859-1 German umlauts remain in that encoding.

A retrieval adapter normalized the non-ASCII Misc1 text into UTF-8 even for its base64 file response. That response was not accepted as the raw source. Reconstructing the original ISO-8859-1 bytes reproduced Git blob `396fca059df27227b5c10c47f9bc1d4a4ce75190` exactly; there is no source encoding defect. The edited blob was published with explicit base64 bytes and verified as `3917f41333fb6ef3ef51b32625123c6a414e9df8`. No unnecessary encoding conversion was committed.

[Machine-readable evidence](sid-guidance-keys-2026-10-31.json) records all source/output blob IDs and SHA-256 hashes. These checks establish XML structure and preservation, not a new live rendering/XDR-engine test. Runtime follow-up concerns the new wording and the three UI surfaces, not re-proving the established override convention.

## Build and boundaries

Only XML assets and review records change. CvGameCoreDLL, the read-only discovery diagnostics, CvGame scheduling hooks, automatic assertion debugger and actual workflow are unchanged. No DLL build is appropriate for this asset-only update, and publication uses [skip ci]. Prior native DLL evidence remains tied to tested commit `770e9e4f0984f3099b7eaa8c261bbaa51a1e0756`, not to these XML checks.

Read-only baseline 1.14 remains `5970334b64a875b5cdb370c94fc9a98db4eacda6`; current dll-build remains `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`. Original branches, other feature boundaries and prior review results remain intact.
