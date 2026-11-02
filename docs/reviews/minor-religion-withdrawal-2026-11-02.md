# Minor-religion withdrawal anger — 2026-11-02

MINORRELIGION-20261102-01. Existing isolated branch: `CivicScrollDraft-ChatGPT`.
Implementation parent: `a7a1290aa2a0c125432dd60df5f4153294eead82`.
Read-only AdvCiv 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Original `UniqueCivicsReligions` remains at `d0fc7c0f93320e112903416c17bb2a2030819d60`.
Workflow source pinned for the native matrices: `dll-build` at
`1cc8c3d24e9fe15126485de0b9e6604167caac36`.

Release and Debug compiled and linked successfully under MSVC 7.1, both with zero
warnings and zero errors, at prepared commit
`bc6173a8ff9bc14588d80734a93c887ea95175cb` in
[run 41476525357](https://github.com/SuperXANA/AdvCiv/actions/runs/41476525357).
Actual artifact Build.log files, compiler probes, source manifests, provenance,
x86 DLLs and the Debug PDB were inspected. In-game withdrawal, rendering and a
fresh-game save/reload remain unverified.

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

Initial source implementation: `201ab3bc1f9254eaf6c99c9353a5041d7c9b4c81`.
Prepared commit: `298db31e52027b86912a8241ecbac3204cc92837`.
[Run 41475051763](https://github.com/SuperXANA/AdvCiv/actions/runs/41475051763)
compiled past the former timer blocker in both configurations, then failed in
`CvCityAI.cpp` at lines 5762, 5785, 5804 and 5809 on undeclared identifiers/scopes
and the resulting invalid member call. Both actual Build.log summaries contain
zero warnings and seven errors including NMAKE/MSBuild wrappers.

MINORRELIGION-20261102-02 fixes those newly exposed native errors: resolve the
hybrid from the evaluated building; compare competing-corporation value against
the existing local minor-organization value; extend the trigger-corporation ID
into the scope that already uses it; and guard headquarters/count lookups when
that optional ID is NO_CORPORATION. Existing arithmetic, religion prerequisite,
and ordinary corporation valuation remain intact. Source correction:
`d664c818c2486f47a4fc150fe9296fb4ef809371`.

`python3 tests/hybrid-building-value/check.py` compiles the complete actual hybrid
block with distinct enum and engine stand-ins under the same strict C++03/sanitizer
flags. Eight cases cover ordinary value, stronger/weaker competing HQs, existing
corporation levels, disabled corporations and missing corporation/religion/hybrid
sentinels. These are scoped valuation checks, not full AI/gameplay validation.

Both failure-log and source-diagnostic ZIPs were downloaded and extracted, and
their actual Build.log/BuildTiming.log, pins and 349-entry source manifests were
inspected. Expected/actual manifests match digest
`4e3cfd356db81b9f0380b801bef52d4b7875f906aff42269a9fce5a20eb4437b`.
Artifact IDs: Release logs `13156143669`, sources `13156842183`; Debug logs
`13156852107`, sources `13156732280`. No DLL was produced by this first matrix.

Corrected prepared commit `08f53cf64ae57ce3d79b2eaaa5d41b0b716be27b`
was tested in [run 41475698321](https://github.com/SuperXANA/AdvCiv/actions/runs/41475698321).
Both configurations compiled the corrected hybrid valuation and then failed in
`CvGameTextMgr.cpp`: two extra closing parentheses in civic prerequisite help
(lines 7191/7201) and two `ReligonTypes` misspellings in hybrid religion help
(lines 10554/11223), with dependent diagnostics. Actual Build.log in each has
zero warnings and eighteen errors including wrappers.

MINORRELIGION-20261102-03 corrects only those four source lines, retaining the
existing conditions and text behavior. Correction source:
`6eb9b57565e9136a37c223a9973258d0977d29c1`. All four ZIPs from this second
matrix were extracted and their actual logs and exact provenance inspected.
Both 349-entry manifests match
`a5b9ca6ed7a8832db5da493ebe0576302599dd42693d6b55ffaced9a0a42ca84`.
Artifact IDs: Release logs `13157092477`, sources `13157147514`; Debug logs
`13156234351`, sources `13157122634`. No DLL was produced.

Prepared commit `bed22dc80e8bdd2e47afc824b4ad5c94bf6fe51a` was tested in
[run 41476027569](https://github.com/SuperXANA/AdvCiv/actions/runs/41476027569).
Both configurations compiled the preceding changes and then failed at
`CvTeam.cpp:4494`: a technology-founding religion loop used undeclared
`eReligion`, also producing a dependent member-call error. Each actual Build.log
has zero warnings and four errors including wrappers.

MINORRELIGION-20261102-04 changes that lookup to the already-declared
`eLoopReligion`, preserving the exclusion of minor organizations from founding
solely through technology. Source correction:
`e43dcf0ed56702c9bb3c739d6e5231da136bce23`. All four third-matrix ZIPs were
extracted and actual logs, exact pins and matching 349-entry manifests verified.
Manifest digest:
`fe40d01dac9dae8651f4b0945043eea793e8cb8aaca6016c9cfc14b18880e25f`.
Artifact IDs: Release logs `13156414384`, sources `13157078044`; Debug logs
`13157397778`, sources `13157941620`. No DLL was produced.

Prepared commit `bc6173a8ff9bc14588d80734a93c887ea95175cb` is tested in
[run 41476525357](https://github.com/SuperXANA/AdvCiv/actions/runs/41476525357).
Release succeeded with zero warnings and errors. Its actual Build.log and
BuildTiming.log were inspected; its x86 PE DLL is 6,578,176 bytes with SHA256
`60d657efc0e6989e6cda550846f7b4d6b0fc098da6393982b457069e1ff6a9c6`.
The independently verified 349-entry Windows source manifest matches the pinned
local source manifest, digest
`3920d10c21db66118e7a6e5fd720f57d68c21656d609cfc74ba28b509dde3fd4`.
Artifact IDs: Release DLL/logs `13156574097`, sources `13158031730`.
Debug also succeeded with zero warnings and errors. Its actual Build.log and
BuildTiming.log were inspected. Its x86 PE DLL is 25,231,360 bytes, SHA256
`9ec196fb2bdbc86099657476c789310f29b75afd4ddf5a4b3089a2a6e2d27b65`.
Its 70,822,912-byte PDB has the expected Microsoft MSF 7.00 header and SHA256
`9899f15a503edcdc401e0a7b642e490c6e997c6e4cfed356088c5654e14ec34e`.
Artifact IDs: Debug DLL/PDB/logs `13157733294`, sources `13157683346`.
Both actual source manifests match the same local digest above; each provenance
record names this exact tested commit, its configuration, the pinned baseline,
selected feature source and workflow source. Both logs confirm successful
`_MSC_VER == 1310` selection. All final four ZIPs were extracted and inspected.

| Configuration | Native compilation/link | Warnings | Errors | Binary artifact |
| --- | --- | ---: | ---: | --- |
| Release | Passed | 0 | 0 | DLL and logs |
| Debug | Passed | 0 | 0 | DLL, PDB and logs |

The three intervening failures were followed only after concrete source
corrections. No unchanged failed source was rebuilt. No branch was created,
merged, force-pushed or deleted; only the existing assistant branch was updated.
Baseline, original feature and workflow-source branch heads remained unchanged.

The existing branch already contains the complete
pinned baseline plus its 24 changed DLL files: 362 DLL blobs, retaining all 338
baseline-only files, and 349 root source files. The prepared workflow uses the
current pinned `dll-build` file with only its three provenance placeholders filled.
Its shared workspace concurrency group, serial Release/Debug matrix, protected
machine-local Project configuration, fresh-output/log cleanup, independent source
hash verification and `_MSC_VER == 1310` compiler probe remain intact.

The remaining runtime check is a new game with appropriate organization data:
trigger joining and departure, inspect the temporary happiness/anger breakdown,
repeat a departure while anger is active, observe expiry (including a one-turn
penalty), and save/reload during the penalty to compare remaining turns and
citizen allocation. Include unhappiness immunity in that game check. This has not
been performed; local stream fixtures and successful native builds do not replace
it. Existing unrelated ownership-transfer and religion-spread policies were not
redesigned or runtime-certified.
