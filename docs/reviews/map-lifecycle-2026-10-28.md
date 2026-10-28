# Temporary plot map lifecycle follow-up — 2026-10-28

Source feature LeaderCivilizationVariantMechanics at 39edf4ca659e806b6fb4bb2de4ab280756829a99.
Previous assistant head 16e8e116231e952d4829229c8b1124a289f59227; code https://github.com/SuperXANA/AdvCiv/commit/6cce496f0f0de61f236b1be2ad7a3d6299b0e2e3.
Read-only 1.14 remains 5970334b64a875b5cdb370c94fc9a98db4eacda6. Existing timer findings PLOTTIMER-20261027-01..03 remain recorded; this is separate lifecycle/turn coverage.

## PLOTTIMER-20261028-04 — reset dereferences deleted or null storage

[CvMap::reset, line 218](https://github.com/SuperXANA/AdvCiv/blob/6cce496f0f0de61f236b1be2ad7a3d6299b0e2e3/CvGameCoreDLL/CvMap.cpp#L218).

The original constructor sets m_pTempChangesMap to NULL at line 39 and calls reset. reset first calls uninit, whose XANA block deletes the temporary-change map, then originally invokes m_pTempChangesMap->reset() at line 218. On initial construction this dereferences null; subsequent resets also use storage after deletion. Allocation occurs only later inside init at line 81, so it cannot protect the constructor/reset path.

The repair constructs a fresh PlotTempChangeMap at the end of reset, after uninit and the ordinary reset work. It removes the later allocation from init (line 81 becomes an ownership comment) so init does not replace/leak the object already created by reset. Existing constructor initialization and uninit deletion are retained, as are XANA 04-26-2025 boundaries. A default-constructed PlotTempChangeMap supplies empty enum maps; the proposal does not change their serialized types or field order.

## PLOTTIMER-20261028-05 — gameplay duration depends on graphics readiness

[CvMap::doTurn, lines 347–358](https://github.com/SuperXANA/AdvCiv/blob/6cce496f0f0de61f236b1be2ad7a3d6299b0e2e3/CvGameCoreDLL/CvMap.cpp#L347).

The original block calls PlotTempChangeMap::update only if GC.IsGraphicsInitialized() is true. That method advances timers and restores plot state, so the condition controls game state rather than merely rendering. The proposal removes this condition and advances temporary effects for every plot after its ordinary doTurn call. This permits the same logical countdown progression in graphics-ready and graphics-unready execution.

Actual restoration invokes engine plot setters. Their graphics-side behavior is not certified by this fixture; integration must confirm those normal setters handle the engine's unready paths correctly. No alternate graphics policy or UI behavior is introduced.

## Verification

python tests/map-lifecycle/check.py passed with g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. LeakSanitizer disabled.

The fixture extracts the actual marked pointer-init/allocation/deletion snippets and the complete actual doTurn body. A modeled lifecycle surrounds the snippets, with allocation/destruction counters and stub plots. Structural assertions verify constructor initialization precedes reset, uninit precedes reset allocation, exactly one new PlotTempChangeMap exists in the translation unit, and init already calls reset before the removed allocation site.

It checks one live storage object after construction/init, repeated reset, balanced final destruction, per-plot normal turn before timer update, and five timer ticks with graphics readiness false and true. The stream/read/write methods, actual enum maps, engine CvMap initialization, allocation failure, world-builder regeneration, plot setter graphics integration and game/multiplayer sessions are excluded. It is not a full CvMap compilation, MSVC 7.1 test or DLL build.

No workflow was added or DLL build triggered. Whole-feature native eligibility remains unverified; further work should reuse PlotTimerDraft-ChatGPT and apply the authorized complete pinned-base overlay before any useful DLL build. Existing read/write version handling and the broader gameplay-mechanic integration still require separate coverage.

Only CvMap.cpp changes in production this pass. The original feature branch and 1.14 remain untouched; no new branch was created.

## Rotation

Fresh inventory showed no changed source heads. The GenderCounter head difference was its already-delivered review documentation. UnitStatusEffects remains deferred; the ceiling alert remains closed. Failed and unverified native builds and partial scopes remain, so the stop gate is false.
