# Organization pass-3 declarations and staged-list bounds — 2026-10-30

ORGLOAD-20261030-01/02. Read-only source UniqueCivicsReligions d0fc7c0f93320e112903416c17bb2a2030819d60; reused CivicScrollDraft-ChatGPT parent f85393be51e32f7440fedc3e4f7946d8b56f25cb. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against global ledger 7154a34bc88bbcd5cdde4201c35ee15f1b1c5a83.

## Committed corrections

ORGLOAD-20261030-01: CvReligionInfo::readPass3 and CvCorporationInfo::readPass3 are defined in CvInfo_Organization.cpp (231 and 392) but absent from their respective class declarations. An inherited base declaration does not declare a derived class's out-of-class member definition. Add public bool readPass3() declarations in CvInfo_Organization.h:90 and :147, bracketed by the existing feature's XANA markers. This permits those existing derived definitions to compile and be called as derived members.

ORGLOAD-20261030-02: both derived methods use staged index 2 for HybridOrganization after the common base resolves indices 0 and 1 for PrereqCivilization/PrereqLeader. Their old size<1 guard allowed size 2; the base's size<2 guard then succeeded and the third access was out of bounds. Require size>=3 before calling the base at CvInfo_Organization.cpp:233 and :394. Reject incomplete lists without changing fields or performing lookups.

The reader at 65–70 stages the first two strings, religion reader at 223–224 and corporation reader at 386–387 append the third. No new authoring tag, ID lookup policy or hybrid mechanics is invented. The existing base resolver, accepted extra-tail behavior, unknown-name lookup results and successful staging clear remain unchanged.

## Verification

tests/organization-pass3/check.cpp contains the complete actual three pass-3 bodies and the two added derived declarations in reduced class shells. Global lookup, fields and error assertions are interface stubs. FAssert is disabled to exercise release-style false-return behavior; real Debug assertion handling is not tested.

4,116 configurations passed strict C++03 -Wall -Wextra -Werror -pedantic with ASan/UBSan: both derived classes, sizes 0–5, 343 combinations of empty/NONE/known/unknown strings per size. Lists below three preserve staged data and all fields with zero lookups. Lists of at least three use the first three values, perform exactly three lookups, clear staging, and a second call returns false without changes. The test does not establish category-correct IDs; that lookup contract is deliberately stubbed.

Negative controls: remove only the two derived declarations and compilation reports no matching declaration for each definition. Restore only the two old guards and the acceptance assertion fails for size two; a separate run with -D_GLIBCXX_ASSERTIONS confirms std::vector::operator[] fails __n<this->size(). Leak detection disabled as unsupported; no leak claim.

No whole production header/classes, MSVC 7.1, XML file/parser, full DLL, game or save/cache validation is claimed. The fixture extracts scoped declarations and bodies and cannot certify unrelated class members or consumers. This partial integration draft uses [skip ci]; no native build triggered.

## Remaining review

CvXMLLoadUtilitySet.cpp's pass-3 loops at 705–709 discard return values; rejection is therefore not yet certified to abort loading. Repeated reads/default inheritance, full enum/type metadata, hybrid loader completion, constructor defaults, actual UI/binding/caller integration and native compatibility remain open. Surplus staged entries are still accepted/cleared as before, not validated as an authoring contract. Earlier civic/religion UI and player-gate refinements remain intact.
