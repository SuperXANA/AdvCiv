# Temporary plot changes preserve empty originals — 2026-10-30

PLOTTIMER-20261030-07. Read-only source LeaderCivilizationVariantMechanics 39edf4ca659e806b6fb4bb2de4ab280756829a99; reused PlotTimerDraft-ChatGPT parent 887dde82df4082665e22ba7b50da17ffa06e915a. Read-only baseline 1.14 5970334b64a875b5cdb370c94fc9a98db4eacda6. Complete 75-branch inventory found no changed original heads against global ledger 493cb38589f903411956d6117681f4b7c3a22b88. Earlier timer/lifecycle/version findings retained; this implements queued repeated-change restoration coverage.

## Committed correction

CvPlot.cpp's five setTemp*Type functions decide whether to capture the original using their corresponding active timer <=0, replacing comparisons of stored original type with NO_*.

| Function | Changed line |
| --- | ---: |
| CvPlot::setTempTerrainType | 2063 |
| CvPlot::setTempFeatureType | 2082 |
| CvPlot::setTempBonusType | 2101 |
| CvPlot::setTempImprovementType | 2121 |
| CvPlot::setTempRouteType | 2141 |

NO_FEATURE, NO_BONUS, NO_IMPROVEMENT and NO_ROUTE are legitimate original states, not reliable uninitialized-backup markers. Example: an originally featureless plot gets temporary feature A, then B while its countdown is active. The old second call sees saved NO_FEATURE and replaces that backup with A; expiry restores A instead of the featureless original. The same collision affects the other empty-state channels.

A positive timer already identifies an active temporary change throughout the existing wrappers and PlotTempChangeMap::update. Capture once when inactive; preserve the original across active replacements. Terrain follows the same state convention, though normal engine terrain is not NO_TERRAIN. Existing type-change gates, timer replacement/clamping, feature variety capture, map layout, stream version and ordinary restoration calls are unchanged. Existing XANA markers preserved.

## Verification

tests/plot-restoration/check.py extracts all five actual revised CvPlot temporary-type setters and compiles them with the complete actual PlotTempChangeMap.h/.cpp. CvPlot ordinary setters/getters, globals, stream interfaces and ArrayEnumMap are stubs. The enum-map stub retains enum default -1, numeric default zero and signed-short storage checks.

3,744 strict C++03 -Wall -Wextra -Werror -pedantic ASan/UBSan sequences passed: all distinct first/second temporary types across three stub terrain IDs and three IDs plus NO_* for the other four channels; initial and replacement durations 1/2/5; every still-active age before replacement. Assertions check original backup before/after replacement, exact timer reset/countdown, restoration at expiry, feature variety preservation, no repeat expiry effect, channel isolation and a separate unchanged plot.

Restoring only the five original capture conditions fails the original-backup assertion. Leak detection disabled as unsupported; no leak claim. No warning suppression.

These tests do not execute real CvPlot setters, game metadata/variety bounds, engine enum-map serialization, world-builder edits, save migration, graphics, MSVC7.1 or a DLL/game session. Stub variety values exercise copying, not the actual varieties available for specific real features. Only positive-duration replacements are verified. Same-type refresh still follows the old early-out; zero-duration/cancellation semantics and unrelated permanent edits during a temporary effect remain separate policy/integration scopes.

Partial restoration draft uses [skip ci]; no native build triggered. Prior version-8 map payload discriminator remains, and old ambiguous feature-version-7 saves are not newly supported. Whole-feature metadata/player/yield and actual map encoding still require review before native validation.
