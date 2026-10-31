# Temporary feature-variety changes — 2026-10-31

PLOTTIMER-20261031-08. Read-only original LeaderCivilizationVariantMechanics 39edf4ca659e806b6fb4bb2de4ab280756829a99; reused PlotTimerDraft-ChatGPT parent 1fa0a79b6e9d3d002b7096d4b5b437ec8087533b. Read-only 1.14 baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory has no changed original source heads against global ledger d307c2ba103c8d53d23a668c218fd66cc464dafa; the only assistant difference was the preceding assertion-artifact report.

[Scoped correction deccf25b689cd34c355ee9094d64863a43c8701f](https://github.com/SuperXANA/AdvCiv/commit/deccf25b689cd34c355ee9094d64863a43c8701f).

## Completed correction

CvPlot::setTempFeatureType, CvGameCoreDLL/CvPlot.cpp:2077–2080, previously entered its body only when the requested feature type differed from the current type. Its explicit iVariety parameter was ignored for a variety-only transition. This differs from the actual pinned baseline CvPlot::setFeatureType, which compares both type and normalized variety.

Example: a plot holds feature F, variety 0. Request temporary feature F, variety 1, for five turns. Previously nothing changed and no timer was scheduled. The correction applies variety 1, captures F/0 as the original, and restores F/0 on expiry. An active temporary replacement still preserves the first original, including its variety.

Extend the existing entry guard to admit a different explicit variety only when the feature is present and the variety is nonnegative and below that feature art's getNumVarieties(). The ordinary setter still performs its existing normalization and engine updates. No backup algorithm, timer arithmetic, serialized type, field layout or other channel was changed. Original/parent XANA markers remain; the new guard has a dated annotation.

The validity check keeps this correction narrow: same-state calls, same-type automatic/invalid variety requests and NO_FEATURE retain their prior no-op behavior. Existing type-changing requests follow the original path. Positive-duration replacement follows the already implemented timer reset convention. No same-state refresh, zero-duration cancellation or permanent-edit policy was selected.

## Verification

Run python3 tests/plot-variety/check.py. It extracts the actual revised temporary-feature setter and the actual normalization/early-return front end of CvPlot::setFeatureType. It compiles them with the complete actual PlotTempChangeMap.h/.cpp.

7,294 sequences pass strict C++03, -fno-exceptions, -Wall -Wextra -Werror -pedantic, ASan and UBSan:
- 7,200 positive-duration sequences across three feature IDs, one through four available varieties, every original/first/replacement variety combination, durations 1/2/5 and every still-active age before replacement.
- 90 same-type automatic/invalid variety no-op cases.
- Four NO_FEATURE no-op cases.

Checks cover the applied variety, first original/type-variety backup, timer replacement or unchanged same-state timer, exact expiry restoration, ordinary setter call counts, no repeated expiry effect and isolation of terrain/bonus/improvement/route channels. Restoring only the old type-only entry guard fails the variety assertion.

The earlier tests/plot-restoration/check.py fixture was extended only with the metadata accessor interface required to compile the revised guard; its existing 3,744 repeated-change/restoration cases also pass under their original strict C++03/ASan/UBSan flags. That fixture's count is regression evidence, distinct from the new cases. No claim is made that its old metadata-free setter stand-ins execute real engine art rules.

Engine tables/art info, actual EnumMap encoding, plot storage and stream interfaces remain stand-ins. The baseline ordinary-setter normalization front end is actual source, but its subsequent graphics, yield, sight and surrounding-city updates are omitted. No MSVC7.1, full DLL, real map save, graphics or gameplay validation is claimed. LeakSanitizer is disabled.

## Whole-feature readiness disposition

VARIANT-20261031-01. No DLL build was triggered. The fully specified temporary-change component can be checked independently, but the same original head contains an unresolved gameplay-mechanic axis contract:
- CvInfo_GameplayMechanic.h:77–78 declares m_iElysiumTerrainAxis / m_iGehennaTerrainAxis.
- Its getters at33–34 access undeclared m_iElysiumPlotChangeAxis / m_iGehennaPlotChangeAxis.
- CvInfo_GameplayMechanic.cpp:9–10 initializes yet another pair, m_iElysiumPlotChangeAxisAxis / m_iGehennaPlotChangeAxisAxis.
- Its XML reader at167–168 assigns positive Ragnarok to Gehenna and negative Ragnarok to Elysium, while the header getter comments describe Elysium as positive and Gehenna as negative.

The metadata files are byte-for-byte unchanged from original source 39edf4ca659e806b6fb4bb2de4ab280756829a99. The original tree supplies no XML configuration/schema resolving this contract; neither CIV4GameplayMechanicInfos.xml nor CIV4PlotChangeAxisInfos.xml exists in that source or the pinned repository baseline. The supplied loader requests those tables at CvXMLLoadUtilitySet.cpp:724 and687 respectively. As the branch README describes manual integration, missing standalone installation assets alone are not classified as a directory defect.

The metadata class also contains obvious source readiness errors, including the destructor's trailing colon and unmatched nested block at13 onward, and an m_apTerrainYieldChanges reference despite the declared m_aTerrainYieldChanges vector. These are static source observations, not errors from an executed native compiler run. A complete class repair requires a coherent declaration/constructor/accessor/XML model; no replacement axis fields, sign interpretation or configurations were invented merely to obtain compilation.

Record an exact-head skip for original 39edf4ca659e806b6fb4bb2de4ab280756829a99 and pause associated full-feature integration. Resume after user source changes supply consistent metadata implementation and the intended axis/configuration details. The completed component correction remains available on the assistant branch. Do not repeatedly build or re-review this unchanged incomplete head.

This scoped source/test/report publication uses [skip ci]. Current dll-build workflow f77f8a67cd17fdfa9d1c3f443d49005cee04421e was read; no baseline-only or partial build is substituted for full feature validation. Original branch, baseline and independent feature code remain untouched.
