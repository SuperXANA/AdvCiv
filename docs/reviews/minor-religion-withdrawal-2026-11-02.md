# Minor-religion withdrawal anger — 2026-11-02

MINORRELIGION-20261102-01. Existing isolated branch: `CivicScrollDraft-ChatGPT`.
Implementation parent: `a7a1290aa2a0c125432dd60df5f4153294eead82`.
Read-only AdvCiv 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Original `UniqueCivicsReligions` remains at `d0fc7c0f93320e112903416c17bb2a2030819d60`.
Workflow source pinned for the forthcoming matrix: `dll-build` at
`1cc8c3d24e9fe15126485de0b9e6604167caac36`.

## Mechanism

The former departure hook called an undeclared `changeUnhappinessTimer`, causing
C3861 in both configurations of [run 41224382638](https://github.com/SuperXANA/AdvCiv/actions/runs/41224382638).
The explicit implementation request reopens that recorded readiness gate. This
implements the missing behavior; it is not another attempt at the unchanged failure.

A dedicated city integer timer is necessary: joining happiness is already an
independent positive bonus, while hurry anger derives its intensity from accumulated
rushing intervals and has its own modifiers. Sharing either state would conflate
different effects. No hurry/conscript/defiance state or calculation is changed.

- `m_iUnhappinessTimer` initializes to zero in the actual city constructor. AdvCiv
  1.14 merged city reset into this constructor; there is no separate reset method.
- Positive `WithdrawalUnhappinessTurns` adds exactly that many turns. Zero/negative
  durations do nothing, preserving the existing metadata default of zero. The
  metadata constructor/reader and the joining hook are unchanged.
- Repeated departures extend one city-wide duration; they do not multiply anger.
  Positive additions saturate at the representable integer maximum, and negative
  changes stop at zero. Only effective changes dirty AI citizen assignment.
- `getTemporaryUnhappiness()` uses the existing nonnegative `TEMP_HAPPY` magnitude
  from joining happiness. This is the explicit symmetry chosen here, with no new
  numeric balance constant or game-speed multiplier. A zero magnitude disables the
  numerical effect even if a duration is active.
- `unhappyLevel()` includes the new source after its existing no-unhappiness guard.
  Joining happiness and departure anger may coexist; neither erases the other.
- Existing anger expires after city production/decay and before `doReligion()`.
  A departure occurring inside that religion update therefore retains its full
  duration, including the one-turn case. It affects the next complete city
  production interval; old anger decrements once per city turn until zero.
- `setAngerHelp()` adds the same amount to its breakdown and total, with remaining
  turns. `Assets/XML/Text/CIV4GameText_MinorReligion_mlp.xml` supplies the new key.
  Its English entry follows the existing single-language fallback convention.

City serialization advances `uiFlag` from 17 to 18 and writes the dedicated timer
immediately after the pre-existing happiness timer. The matching conditional read
defaults it to zero for pre-18 city records, including when reading into an object
that previously held anger. Both neighboring field order and timer independence
are retained. This is a city record revision, not migration of any previously
released feature save format. An older DLL cannot read the new city format.

Original XANA annotation lines remain in order. The historical TODO is retained
and immediately followed by a dated implementation note. All new DLL edits are
bracketed by dated XANA annotations, and previous branch refinements are retained.

## Focused regression evidence

Run `python3 tests/minor-religion-withdrawal/check.py`.

The runner compiles the actual complete timer methods, joining/departure hooks,
`happyLevel`, `unhappyLevel`, and `setAngerHelp` under strict C++03 with ASan/UBSan.
Declarations, constructor assignments, the production-through-religion turn slice,
and versioned stream slices are extracted from current production source. Engine
interfaces, unrelated happiness sources and the typed sequential stream are
stand-ins. This is not complete city construction, actual FDataStreamBase encoding,
the full city turn, native ABI validation, or a Civ4 save-file test.

Across four fresh processes for configured magnitudes 0–3 (the existing
`happyLevel()` caches the define), the fixture passes:

- 24 lifecycle/tooltip scenarios covering durations 1–6, a departure arising
  inside the religion update, mixed/repeated departures, zero/negative metadata
  durations, independent joining/hurry/conscript/defiance values, immunity,
  citizen-assignment invalidation, expiry and no negative countdown.
- 44 stream scenarios: ten zero/active-duration round trips plus a version-17
  default/alignment case per process. Active timers continue with identical
  post-load expiry; neighboring values and a trailing sentinel remain aligned.
- 140 boundary scenarios covering zero, positive and negative deltas through
  INT_MIN/INT_MAX, saturation and no-op dirty-state behavior.

Three independent negative controls remove the unhappiness contribution, bypass
the legacy stream guard, or remove the tooltip contribution. Each is rejected by
the corresponding value, stream-boundary, or tooltip-total assertion.

Flags: `-std=c++03 -Wall -Wextra -Werror -pedantic
-fsanitize=address,undefined`; `ASAN_OPTIONS=detect_leaks=0`,
`UBSAN_OPTIONS=halt_on_error=1`. No leak or game-runtime claim.

Preserved fixtures also pass: 15 organization getter / 20 religion-weight cases,
2,695 weight mutation/bounds/allocation-failure cases, 15,360 base/hybrid metadata
constructor/read configurations, two reduced religion-reader cases, and the
existing civic-screen drawing/visibility fixture.

## Native validation

Pending the prepared matrix. The existing branch already contains the complete
pinned baseline plus its 24 changed DLL files: 362 DLL blobs, retaining all 338
baseline-only files, and 349 root source files. The prepared workflow will use the
current pinned `dll-build` file with only its three provenance placeholders filled.
Its shared workspace concurrency group, serial Release/Debug matrix, protected
machine-local Project configuration, fresh-output/log cleanup, independent source
hash verification and `_MSC_VER == 1310` compiler probe remain intact.

Native compilation will be recorded separately from unverified in-game religion
withdrawal, city-screen rendering, and a newly started game saved and reloaded.
