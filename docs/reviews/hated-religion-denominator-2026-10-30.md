# Hated-religion zero denominator — 2026-10-30

HATED-20261030-03. Implements the previously recorded, unresolved religion-scoring arithmetic defect rather than presenting the observation as newly discovered. Read-only source HatedCivicReligionDiplomacy a9c1a754b5e9b64e10ceaa22fd02fa78f3718785; reused HatedDiplomacyDraft-ChatGPT parent c45a473baa07adc9cfbe898f17e074025902016a. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against global ledger bc405cd9333ec0204f965c4f31c756c2ba3f05cb.

## Committed correction

CvPlayerAI::AI_religionValue, CvGameCoreDLL/CvPlayerAI.cpp:18245: replace iLikedReligionCivs / iHatedReligionCivs with iLikedReligionCivs / std::max(1, iHatedReligionCivs).

The hated count starts at zero and increases only for known eligible civilizations following the candidate religion with annoyed/furious attitudes. No known rivals, rivals following other religions, or only cautious/pleased/friendly followers all leave it zero. The old expression therefore divides by zero in ordinary game states. The separate std::max(1, iTotalCivs) protects only the outer denominator.

The correction treats zero hated weight as a neutral divisor of one. With no disliked followers, that reproduces the actual 1.14 liked-civilization contribution; for positive hated counts, every operation and integer-division order is unchanged. This is a scoped denominator repair, not a replacement scoring model. XANA 05-24-2025 markers and earlier counter/cache corrections are preserved.

Integer truncation still means liked=1,hated=2 yields zero boost; hated=1 leaves the liked count unchanged. Deciding whether enemies should directly penalize religion utility or whether fractional ratios should be retained remains a separate mechanics decision. No such policy is invented here.

## Verification

tests/hated-diplomacy/religion-check.cpp embeds the complete actual revised function, original feature function and pinned baseline function under distinct method names, with reduced city/player/personality/iterator/holy-city/vote interfaces.

Strict C++03 -Wall -Wextra -Werror -pedantic, ASan and UBSan passed 83,970 configurations: zero through four eligible foreign civilizations; each foreign state drawn from another religion or candidate-religion furious/annoyed/cautious/pleased/friendly; three personality differences spanning the clamp; three religion flavors; no/own/foreign holy city; vote-religion bonus on/off. All revised results also match an independent small-input arithmetic model.

65,556 configurations with positive hated counts match the actual original feature function exactly. 18,414 configurations with zero hated counts match the actual baseline function exactly. An absent-religion early-return case also passes without accessing city/foreign data. Restoring the original expression reports UBSan runtime error: division by zero in the first no-rival configuration. Leak detection disabled as unsupported; no leak claim.

The fixture's eligible iterator inputs are supplied explicitly; it does not validate the real PlayerIter filters, engine metadata, strategic religion selection, turn integration, attitude caching or full classes. Chosen inputs avoid unrelated overflow and invalid flavor/personality domains. Large intermediate products, 10+religionFlavor validity and full save/cache compatibility remain uncertified.

No native MSVC 7.1/DLL/game result is claimed. This partial branch uses [skip ci]; no workflow run was triggered. Remaining feature lifecycle/save versioning and integration scopes stay open.
