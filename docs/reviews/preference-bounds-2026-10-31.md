# Preference lookup-map ID bounds — 2026-10-31

PREFERENCE-20261031-07. Read-only source LeaderCivilizationDecisionPreferences `aac03388283a5ac316f6a19f6e3754a7435b6511`; reused PreferenceFrameworkDraft-ChatGPT parent `afb7f7ce941698df0c904a233c1120dacb177970`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory has no original-head changes against global ledger c23d090f23e88ccf600d58cb89f76a5062030622. Prior preference cursor and list/map lifecycle work was read and preserved.

[Correction and fixture dcd135136f8b3fabdc87bbe39a89f0cac6d8d7f9](https://github.com/SuperXANA/AdvCiv/commit/dcd135136f8b3fabdc87bbe39a89f0cac6d8d7f9).

## Defect

The five enclosing loaders allocate lookup maps to their corresponding GC info counts, but accept every record ID other than NO_* before indexing those maps. The record declarations in CvXMLStructs.h store IDs as int, and their read methods pass those ints to SetInfoIDFromChildXmlVal. The pinned baseline utility's InfoIDFromChild<T,false> path delegates to global info lookup without the enum-bound assertion of its enum specialization. A successful global lookup from another category can therefore yield a nonnegative ID beyond this map's size. The enclosing static_cast to a category enum did not validate that size.

Zero-capacity tables plus ID zero, or a positive ID equal to the table count, can write outside the allocation. Non-sentinel negative values are likewise unchecked, although ordinary unknown-name lookup normally supplies -1.

## Completed correction

Keep each record ID as int until validation, require 0<=ID<the corresponding GC count, then append the accepted record and write the map using that checked int. No enum conversion is needed for the raw map index. Records outside range are skipped, extending the existing NO_* skip behavior; return/error/default policy is not otherwise changed.

| Reader/list | File | Guard line |
| --- | --- | ---: |
| CvTechPreferenceInfo::read | CvInfo_Civilization.cpp | 1628 |
| CvEventPreferenceInfo::read | CvInfo_RandomEvent.cpp | 2163 |
| CvUnitPreferenceInfo::read, UnitCombat | CvInfo_Unit.cpp | 2647 |
| CvUnitPreferenceInfo::read, UnitClass | CvInfo_Unit.cpp | 2681 |
| CvUnitPreferenceInfo::read, Unit | CvInfo_Unit.cpp | 2715 |

Valid record order, last-duplicate indexing, NONE behavior, omitted lists, existing cleanup and XML cursor movement remain unchanged. Earlier XANA boundaries and edits remain; each new guard has a dated annotation.

## Verification

Run `python tests/preference-bounds/check.py`. It extracts actual full enclosing class declarations and implementations from constructors through read, including destructors and lookup/record getters. The globals, XML tree/cursor and record readers are stand-ins. Earlier actual-record-reader fixtures remain separate evidence; this test injects raw IDs at that interface.

15,552 strict C++03/ASan/UBSan configurations passed: six rotations of category capacities 0–5, all pairs of nine input IDs (INT_MIN,-2,-1,0,1,5,6,99,INT_MAX), and all 32 masks of present/omitted replacement lists. Each case first populates valid initial state, then loads a mix of boundary IDs, checks accepted vector cardinality/order, every valid lookup and record ID, last-duplicate behavior, independent category counts and cursor restoration.

Five negative controls restore an ID!=-1 guard for one list at a time while restricting inputs to nonnegative IDs. Every control reproduces ASan heap-buffer-overflow at a lookup-map write. An initial broad negative probe reached an ASan write SEGV for INT_MIN; the focused nonnegative controls establish the ordinary upper-bound defect independently of extreme negative values.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0, UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Limits / remaining scope

Range checks cannot prove category correctness for a wrong-category global ID whose numeric value happens to be within range. No new keyed schema, type registry or authoring contract was invented. Full category validation, real parser/XML installation, owning-info copying/default inheritance/cache, player initialization and complete engine/native integration remain open.

No full MSVC7.1/DLL/game result. Partial scoped code uses [skip ci]; no DLL run triggered. This is not a validation of the real global-ID lookup or enum ABI, which are stubbed in the fixture. Original branches and baseline remain untouched.


---

# Follow-up: unit preference consumer and save-load integration — 2026-10-31

Source branch `LeaderCivilizationDecisionPreferences` remains unchanged at `aac03388283a5ac316f6a19f6e3754a7435b6511`. The existing assistant branch was reused; it is now 17 commits ahead of that source head with the source head as its merge base. No user-owned branch was edited.

## PREFERENCE-20261031-08 — independent unit fallback and sentinel safety

In `CvPlayerAI.cpp`, the previous combined fallback only attempted class and combat preferences when neither the leader nor civilization had a more-specific entry. This incorrectly allowed one profile's direct-unit choice to suppress the other profile's class/combat choice. The combat lookup also passed `u.getUnitCombatType()` directly to the bounded index-map accessor; `NO_UNITCOMBAT` is a valid sentinel and must not be used as an array index.

Correction: `copyUnitPreferenceForUnit` now resolves direct unit, then class, then combat independently for each profile. It skips class/combat lookup when the corresponding type is `NO_UNITCLASS`/`NO_UNITCOMBAT`. The resulting leader and civilization choices are both applied.

[Implementation commit ffc3fed40cfc401d40fb482ecf65fe44e6eea32c](https://github.com/SuperXANA/AdvCiv/commit/ffc3fed40cfc401d40fb482ecf65fe44e6eea32c).

## PREFERENCE-20261031-09 — unit percentage modifier was copied but unused

The typed snapshot helper copied `iUnitValueModifierPercent`, but `AI_unitValue` never consumed that value. The unit preference modifier therefore had no effect on unit valuation.

Correction: apply leader and civilization percentage modifiers after the rest of unit valuation, using the same additive-percent convention as technology preferences: multiply by `100 + modifier`, then divide by 100. Both profiles are applied in sequence. The existing integer multiplication convention is retained; extreme modifier/score overflow is not separately proven safe.

[Implementation commit 895734bc6130811d8cb520490c5dd9b92663f561](https://github.com/SuperXANA/AdvCiv/commit/895734bc6130811d8cb520490c5dd9b92663f561). The focused consumer fixture was updated in [bd478e60670bd208d0990e7297ca73edc4af8f37](https://github.com/SuperXANA/AdvCiv/commit/bd478e60670bd208d0990e7297ca73edc4af8f37).

## PREFERENCE-20261031-10 — derived preference selections were not rebuilt after save load

The six cached leader/civilization preference IDs are derived from loaded player identity and XML; they are not serialized. `CvPlayerAI::AI_init` initializes them for new-game initialization, but `CvPlayerAI::read` did not rebuild them after `CvPlayer::read` restored the saved leader and civilization. A loaded game could therefore retain constructor defaults or stale selections.

Correction: the end of `CvPlayerAI::read` now calls `AI_updateTechPreferences`, `AI_updateEventPreferences`, and `AI_updateUnitPreferences` after the saved player state has been read.

[Implementation commit ee098b8c62490346cc6632366ff16ecce9e1cf6d](https://github.com/SuperXANA/AdvCiv/commit/ee098b8c62490346cc6632366ff16ecce9e1cf6d).

## PREFERENCE-20261031-11 — XML schema root spelling

The new technology and event preference schema declarations spelled the root element `PerferenceInfos`, while their loader paths and expected XML root names spell `PreferenceInfos`. Corrected both schema element names.

[Technology schema correction](https://github.com/SuperXANA/AdvCiv/commit/762681ebf7d85738076424e81785170bdabbd121).
[Event schema correction](https://github.com/SuperXANA/AdvCiv/commit/eb2b2cd551c2ea8fed420f80deb2459e95a3703a).

## PREFERENCE-20261031-12 — event/unit preference XML authoring remains incomplete

`CvXMLLoadUtilitySet.cpp` requests `CIV4UnitPreferenceInfos.xml` at line 713 and `CIV4EventPreferenceInfos.xml` at line 865. The current feature-branch tree contains only `XML/Civilizations/CIV4TechPreferenceInfos.xml`; neither matching event nor unit preference data file is supplied. The event schema now declares the expected structure, but the data file is absent. No unit preference schema/data authoring path is present in this branch.

Do not invent leader/civilization unit or event preferences. Supply the intended XML assets and schemas before runtime validation or full feature integration.

## Verification and limits

A focused C++03 helper fixture compiled with `g++ -std=c++03 -Wall -Wextra -Werror -pedantic` and passed checks for independent leader/civilization fallback, `NO_UNITCLASS`/`NO_UNITCOMBAT` sentinel handling, and compounded percentage modifiers. The repository consumer fixture was expanded to cover 4096 combinations plus sentinel, mixed-specificity, and modifier cases; that full repository fixture was not run in this turn.

All code/test/schema commits used `[skip ci]`; no DLL build was triggered. No MSVC 7.1, actual XML installation/cache, save/load game, or runtime result is claimed. The remaining missing event/unit XML authoring prevents approval of the whole feature for integration.


---

# Separate feature review: summon transfer follow-up — 2026-10-31

Source branch `LeaderCivilizationSummoningRandomEvents` remains at `d237c40d9d5f19e8c1d60f2c8a8ff3e15d3792bc`. The existing `SummonCatchupDraft-ChatGPT` branch is a direct descendant of that source head and is 12 commits ahead. No user-owned branch was edited and no branch merge was performed.

[Commit 9408469df1c280bc24db9aee750ac972bb77028b](https://github.com/SuperXANA/AdvCiv/commit/9408469df1c280bc24db9aee750ac972bb77028b) corrects the city-transfer helper's `CvEventInfo` parameter type, malformed city-split message construction, notification helper message argument, and city pointer constness. It also rejects explicit leader/civilization pairs that are incompatible when `GAMEOPTION_LEAD_ANY_CIV` is disabled. The assistant branch already contains earlier corrections to the source's malformed candidate-builder call, mutable unit count, missing defector vector, and stray conditional semicolon.

## SUMMON-20261031-12 — random selection is repeated across eligibility and execution

The event eligibility path and event execution path both call the random leader/civilization resolver. The resolver consumes synchronized RNG and the selected pair is not persisted in triggered-event data. Consequently, eligibility evaluation can consume RNG and the later execution can resolve a different pair. Repeated eligibility/valuation queries can also alter the RNG stream.

A durable correction requires an explicit selection lifecycle in triggered-event data, including save/load handling, or a deterministic eligibility-only check followed by one execution-time draw. The relevant event-triggered-data storage and serialization contract is not supplied in this feature branch. Do not invent those fields or persistence rules.

The prior skip remains in force: the military/defection implementation references `CvUnit::isHero()` and `canFoundCity()`, absent from pinned AdvCiv 1.14 and with no feature-supplied `CvUnit` implementation. Hero classification is unspecified. Do not import unrelated feature branches or invent unit semantics to force a build. No DLL build was triggered; the branch is not approved for integration.


---

# Build workflow follow-up — 2026-10-31

The `dll-build` branch advanced from `07133f27906c364b266043a1788ec0eacd2e8b3b` to `f77f8a67cd17fdfa9d1c3f443d49005cee04421e`. The complete commit diff adds `BuildTiming.log` to the list of stale MSBuild logs removed before a build. The source hash gate and build command are unchanged. This prevents a prior timing log from being mistaken for output from the current build.

No native run was triggered for this cleanup-only workflow change. The next meaningful overlay should copy the exact current `.github/workflows/auto-dll-build.yml` from `dll-build`.
