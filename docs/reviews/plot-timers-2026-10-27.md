# Temporary plot timer review — 2026-10-27

Source: [LeaderCivilizationVariantMechanics at 39edf4ca659e806b6fb4bb2de4ab280756829a99](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/CvPlot.cpp#L2055).
Proposed code: [d3989b6ff7feeabad3681795edeeee4420af7895](https://github.com/SuperXANA/AdvCiv/commit/d3989b6ff7feeabad3681795edeeee4420af7895).
Read-only reference: [AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6](https://github.com/SuperXANA/AdvCiv/tree/5970334b64a875b5cdb370c94fc9a98db4eacda6).

This is a scoped draft for the XANA 04-26-2025 temporary plot-change block and its supporting PlotTempChangeMap files. The supporting files are new to this feature branch, although they originally lack paired XANA comments; the marked CvPlot/CvMap call sites establish their feature context. Original XANA markers are preserved, and matching markers now delimit those supporting files. All 21 source blobs remain present; only three source files change. No other feature branch is imported. Unmarked upstream differences remain as supplied because this is a source-branch draft, not a complete 1.14 build overlay.

## PLOTTIMER-20261027-01 — timer channel routing and repeated addition

Changed functions:

| Function | Original lines | Proposed lines | Why |
| --- | --- | --- | --- |
| CvPlot::changeTempTerrainTimer | [2154–2159](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/CvPlot.cpp#L2154) | [2154–2159](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/CvPlot.cpp#L2154) | Dispatches to changeTempRouteTimer instead of the terrain channel. |
| CvPlot::changeTempFeature/Bonus/Improvement/RouteTimer | [2161–2187](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/CvPlot.cpp#L2161) | [2161–2187](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/CvPlot.cpp#L2161) | Along with the terrain wrapper, calls undeclared getTemp*Type accessors. The default ignore-inactive gate now uses each existing countdown getter (positive means active countdown). Explicit false still forwards from zero. |
| PlotTempChangeMap::changeTempTerrain/Feature/Bonus/Improvement/RouteTimer(CvPlot const&, int) | [95–127](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.cpp#L95) | [117–149](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L117) | These overloads add the current timer before forwarding to index overloads that add it again. |
| PlotTempChangeMap::getTempFeatureTimer(CvPlot const&) | [103–106](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.h#L103) | [105–108](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.h#L105) | Reads the terrain countdown, affecting callers including feature help. |

For example, a bonus timer of 10 changed by -1 becomes 19 in the original arithmetic, rather than 9. Repeated reductions can increase duration until the compact storage overflows or narrows. The proposal forwards only the delta and keeps each channel independent. It deliberately uses countdown activity for the default gate; this does not establish a complete cancellation or temporary-removal policy.

## PLOTTIMER-20261027-02 — component compiler blockers

The proposal repairs these actual definitions/declarations:

- setRealFeatureType and setTempFeatureType, both plot and index overloads: extra closing parentheses ([original lines 11, 41, 136, 167](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.cpp#L11); proposed starts [33, 63, 158, 189](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L33).
- setTempTerrainTimer(PlotNumTypes, int): missing closing parenthesis at [original line 194](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.cpp#L192), repaired at [proposed line 216](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L214).
- setTempFeatureTimer(PlotNumTypes, int): refers to nonexistent kPlot instead of its ePlotNum parameter at [original line 200](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.cpp#L198), repaired at [proposed line 222](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L220).
- getRealImprovementType(PlotNumTypes) const: missing parameter-list closing parenthesis at [original header line 201](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.h#L201), repaired at [proposed line 203](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.h#L203).

PlotTempChangeMap.h now includes CvPlot.h directly for its inline plotNum calls instead of pulling in the larger CvMap header. These repairs compile the component with the stated stubs; they do not prove the surrounding branch can build.

## PLOTTIMER-20261027-03 — signed-short timer bounds and safe arithmetic

All five timers use ArrayEnumMap<PlotNumTypes,int,short> ([original header lines 161–184](https://github.com/SuperXANA/AdvCiv/blob/39edf4ca659e806b6fb4bb2de4ab280756829a99/CvGameCoreDLL/PlotTempChangeMap.h#L161)). Original setters clamp only the lower bound; original index mutators add arbitrary signed int values before storing them. Large positive values can exceed short storage, and current + INT_MAX can overflow signed int before narrowing.

The five index setters and five index change functions now use [clampTempTimer/addTempTimer, proposed lines 10–23](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L10), with call sites at [214–270](https://github.com/SuperXANA/AdvCiv/blob/d3989b6ff7feeabad3681795edeeee4420af7895/CvGameCoreDLL/PlotTempChangeMap.cpp#L214). The proposed policy saturates to 0..SHRT_MAX (0..32767 on the target). Positive additions are limited by remaining capacity before addition; negative changes are compared against -current before addition, including INT_MIN. Existing short storage and stream layout are retained. This is a finite-duration policy, not unlimited-duration support.

## Verification and limits

Ran `python tests/plot-timers/check.py` successfully with g++ `-std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`. LeakSanitizer is disabled. The fixture compiles the actual complete PlotTempChangeMap header/implementation and extracts the five actual CvPlot timer wrappers. CvPlot, global map access, and ArrayEnumMap are instrumented stubs. The stub enforces signed-short bounds and baseline-style default values; it is not the engine's enum-map implementation.

Checks cover all five channels, independent plots, distinct terrain/feature countdowns, repeated -1 changes, default inactive gating and explicit forwarding, negative setters, INT_MIN/INT_MAX deltas and setters, short boundary saturation, reset, and the existing positive-countdown expiry loop restoring explicitly supplied real values/feature variety once. Metadata/XML, real engine plot setters, map load/save, serialization, graphics state, zero-duration restoration, refresh/overlap rules, temporary removal, UI text, game and multiplayer behavior remain unvalidated. The unrelated gameplay-mechanic loader/player/yield integration requires separate review.

**No workflow was added and no DLL build was triggered.** Actions reported zero runs for the exact proposed code SHA on PlotTimerDraft-ChatGPT. This is not native MSVC 7.1, full DLL, save, or gameplay validation.

## Additional first-pass coverage: AdvancedDiplomacy

Pinned source: [e83ce4c7977daf4193b07d0b94a533bb0338fb11](https://github.com/SuperXANA/AdvCiv/blob/e83ce4c7977daf4193b07d0b94a533bb0338fb11/CvGameCoreDLL/CvDeal.cpp#L748).

CvDeal::startTrade's only literal XANA code annotation is the added self-ID guard at lines 751–752. The source-to-1.14 diff for CvDeal.cpp consists solely of those two added lines. The loop is PlayerAIIter<MAJOR_CIV,OTHER_KNOWN_TO>(kToPlayer.getTeam()). The actual pinned [ExplicitAgentIterator::passFilters, lines 134–135](https://github.com/SuperXANA/AdvCiv/blob/5970334b64a875b5cdb370c94fc9a98db4eacda6/CvGameCoreDLL/AgentIterator.cpp#L134) requires the candidate's team to differ from the recipient team. Thus neither the recipient nor any teammate enters this loop, and the self-ID guard is redundant under 1.14's iterator contract. It does not create a self-memory behavior fix on that baseline. No behavioral defect or code rewrite is proposed for the marked guard; no extra branch or build was created for it. This conclusion does not change third-party tech memory or certify the branch's unmarked historical upstream differences.

## Coverage rotation

Current source heads and 1.14 were rechecked unchanged after publication. The previous assistant head difference was the already-delivered SummonCatchup documentation commit. This pass covers two previously pending source scopes. Five initial source reviews remain pending: LeaderSpecificMultilayeredAIDecisionEval, RealisticAIDecisions, UniqueCivicsReligions, UnitStatusEffects, alert-autofix-1. Partial integration scopes and unverified native states remain; the stop gate is not satisfied.
