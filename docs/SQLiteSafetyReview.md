# SQLite foundation safety review

Reviewed branch: `AISurvivorStatTracking` at
`f2575de4bb94f561d3e1f0df651489487e3742ae`.
Changes are isolated in `AISurvivorSQLiteFixes-ChatGPT`.

## Scope and current readiness

This is a database foundation, not an implemented cross-save event or diplomacy
system. The source contains `SQL_SCHEMA_VERSION (0)` and supplies no game schema
or migration scripts. Initialization deliberately remains unavailable while that
version is zero. No gameplay tables, synthetic memories, or event rules are
invented by this patch. Callers must check availability and define their fallback
behavior before depending on persisted data. A positive supported version and an
actual schema at `Assets/SQL/CvGameDatabaseSchema.sql` are future requirements.

## Corrections

- Database allocation precedes CvGame construction: game construction invokes
  reset/uninit and needs the manager to exist. Removed the undeclared legacy
  `getSQLIFace` accessor.
- Schema bootstrap uses the private connection, avoiding the circular requirement
  that a schema already be loaded before its version can be queried. Public
  queries remain unavailable until verification succeeds.
- Failed/unknown/newer schema reads do not erase the database. Removed automatic
  writable_schema/deletion/VACUUM recovery. Schema installation is transactional
  and must set the exact expected user_version before commit. Migration fails
  closed until explicit source-to-target migration steps are supplied; blindly
  replaying every migration file is not safe.
- Failed opens release the SQLite handle. Failed initialization cleans up and can
  retry. Closing does not finalize statements still borrowed by callers: SQLite
  returns BUSY and the connection remains available for cleanup/retry.
- Cached statements are reset and bindings cleared on return. Checkout verifies
  the SQL text, not just a potentially reused cache name. Changing SQL also
  rebuilds parameter/column maps, including after reset(false).
- `exec()` reports successful SQLITE_DONE for writes; `next()` reports rows only.
  Exhausted/failed statements do not automatically rerun on another next/exec.
  `getLastResult()` exposes the last sqlite3_step status, so false from next can
  be distinguished as DONE versus an execution error.
- Transaction begin updates ownership flags on reuse; an unsuccessful begin
  cannot claim a successful commit. Destruction rolls back an active transaction.
- Fixed parameter-map initialization, missing declarations, iterator spelling,
  string accessors, null handling, bounds checks, duplicate text case labels,
  binding typo/default argument, value-copy semantics required by C++03, query
  builder definition syntax, and SQL-fragment printf-format misuse.
- Windows path discovery uses the wide-character API consistently and unloads
  each library in its owning scope. Schema path includes Assets. Windows path
  discovery is not exercised by the portable tests.

## Ownership contract

The manager owns the connection and cached statements. A SQLiteStatement borrows
one handle exclusively until reset/finalize/destruction returns it. Statement
objects must not outlive the manager. A busy uninit can be retried after borrowers
return; this is not a guarantee that arbitrary use after manager destruction is
safe. The cache is not a synchronization mechanism for concurrent threads.

SQLiteValue owns copied value data and is copyable. Prepared statements and
transactions remain noncopyable. SQL identifiers/raw fragments passed to the
query builder are trusted code, not escaped user input; bind data values instead.

## Focused tests

`python tests/test_sqlite_wrappers.py`

The harness compiles production wrapper/manager/query sources with C++03
(`-pedantic-errors`, allowing the vendor header's long-long extension), minimal
Civ type stubs, and the bundled SQLite 3.7.5 header. Only the manager's Windows
path-discovery function is substituted with an in-memory test path. By default the harness builds the bundled 3.7.5 C sources using the same 83-file
manifest as the Windows build wrapper; set SQLITE_TEST_LIBRARY to override the
engine library (for example, a previously built archive).

- `SQLITE_TEST_LIBRARY=/path/to/libsqlite3_375.a python tests/test_sqlite_wrappers.py`
- Add `SQLITE_TEST_SCHEMA_FIXTURE=1` to generate a temporary version-1 test
  configuration and exercise transactional schema install/version verification.
  This changes only the generated harness, not the production schema constant.
- Add `SQLITE_TEST_SANITIZE=1 ASAN_OPTIONS=detect_leaks=0` for AddressSanitizer and
  UndefinedBehaviorSanitizer on the wrapper/test code. The supplied static
  SQLite library is not itself sanitizer-instrumented.

Passed with bundled SQLite 3.7.5: write success, constraint failure, iteration
exhaustion, named bindings and lookup maps, NULL/invalid-column reads, copyable
values, cache key collisions, SQL replacement after reset(false), transactions
(commit/rollback/reuse/failed nested begin), safe busy-close retry, failed-open
cleanup, partial schema rollback, configured-schema install, exact version
checks, and preservation of a newer-version on-disk database and sentinel row. ASan/UBSan also passed with leak detection disabled. LeakSanitizer cannot
run under this execution environment's ptrace instrumentation; leak coverage is
not claimed. Initial tests also passed against system SQLite 3.46.1.

These are focused tests, not a full DLL build, Windows filesystem verification,
SQLite engine audit, multiplayer synchronization test, or in-game save validation.

## Follow-up review, 2026-10-27

This pass starts from the existing manager fixes at
`b37d61abd737fc6d93abda3cbc1693af5f4919fb`. The original feature branch and
SQLite 3.7.5 vendor files remain unchanged. New findings and refinements:

- **SQLITE-20261027-01 — Transaction ownership after automatic rollback.**
  `INSERT OR ROLLBACK` can end a transaction without notifying its C++ owner.
  The stale owner's later commit or destructor could then affect another
  caller's transaction. The manager now tracks a transaction generation using
  SQLite 3.7.5's trace callback and autocommit state, including boundaries inside
  raw SQL batches; wrappers verify ownership before commit/rollback. Connection
  shutdown also invalidates ownership. A failed reused `begin()` now clears a
  previous successful commit result. Regressions cover implicit rollback through
  both execution paths, stale destruction, read-only `COMMIT; BEGIN;` batches,
  connection replacement, and failed reuse.
- **SQLITE-20261027-02 — Scaled bindings failed compilation and reads lost precision.**
  Binding used an integer cast unsupported by AdvCiv's actual `scaled` class;
  constructing a read value with a divisor of 100 truncated the floating value
  and applied an extra scale change. The earlier portable stub hid both issues.
  Bind/read conversions now use the existing `getDouble()`/`fromDouble()` API,
  with positive and negative fractional round-trip checks.
- **SQLITE-20261027-03 — Declared foreign keys were unenforced.**
  SQLite 3.7.5 defaults enforcement off in this build. A schema script's
  `PRAGMA foreign_keys=ON` would also be ineffective inside the manager's schema
  transaction. Initialization now enables and verifies enforcement immediately
  after opening the connection, before schema work. Regressions reject orphan
  inserts and check `ON DELETE CASCADE`.
- **SQLITE-20261027-04 — Fast project configurations skipped the SQLite wrapper.**
  Their final `jom build` selected the original makefile, omitting the static
  SQLite build/link setup. Both build and rebuild commands now select
  `BuildSQLite/Makefile.sqlite` for each fast configuration.
- **SQLITE-20261027-05 — Windows DLL compilation needed explicit includes.**
  MSVC 7.1 precompiled-header builds require the direct `CvGameCoreDLL.h` include
  before each affected source's implementation. The manager also needs the full
  `CvGame` declaration for its multiplayer path calls, and its wide path must
  append a wide filename literal. Portable stubs cannot establish these Windows
  compiler requirements; the DLL workflow supplies the actual validation.
- **SQLITE-20261027-06 — Cached column names survived SQLite recompilation.**
  Schema changes can make SQLite automatically recompile a cached `SELECT`,
  changing its result columns after the wrapper has built its name map. The
  wrapper now refreshes names after the first successful step, including an
  empty result. Regressions add a table column and recreate a view with the same
  column count but different names.

- **SQLITE-20261027-07 — Static archive creation assumed a separate lib.exe.**
  MSVC 7.1 compiled all game and SQLite sources, then archive creation could
  not launch the assumed Toolkit `lib.exe`. The wrapper now uses its existing
  `link.exe /lib` library-manager mode, retaining the same toolchain and static
  archive. Both configurations are rebuilt from clean sources for validation.

- **SQLITE-20261027-08 — Final DLL link omitted the static archive.**
  Archive creation succeeded, but the preserved stock link command still
  reported unresolved SQLite APIs. Appending a library macro after including
  the machine Makefile did not connect the archive in this build environment.
  A dedicated additive `sqlite_dll` target now explicitly supplies the archive,
  retains resolved linker flags and postbuild hooks, and displays the command.
  Ordinary and fast project configurations both invoke this target.

The focused portable regression suite passes with the bundled SQLite 3.7.5,
including a reader/writer lock test where COMMIT returns BUSY and the same
owner successfully retries after the reader releases its lock.
Full DLL build results are recorded below. Windows
path discovery, in-game save loading and multiplayer synchronization still
require integration verification.

## Remaining integration design

Cross-save writes need explicit game/branch/event identity and replay semantics:
loading an earlier save must not silently double-count or retract committed
history. A transaction alone does not define that policy. Multiplayer must not
let independent local database contents influence synchronized gameplay without
a defined common snapshot/authority. Current filenames based on game names do
not establish globally unique game identity or synchronization. Persistent
schema migration, backup/recovery policy, complete error reporting, and actual
event/diplomacy consumers remain future work.

## Additional range and Windows-body checks

Scaled reads now reject values outside scaled::MIN..MAX, including NaN/infinity,
returning zero rather than invoking an overflowing fixed-point conversion. This
conservative bound may reject the fractional interval beyond integer MAX. Existing
fractional binding behavior, transaction-generation safeguards, foreign-key setup,
and schema-recompile metadata refresh are preserved. Added regressions cover
non-finite/out-of-range doubles and both accepted endpoints.

`python tests/test_sqlite_windows_path.py` syntax-checks the actual Windows path
function with narrow/wide string and API declarations. This catches type mistakes
hidden by the portable database harness's substituted path function; it does not
validate the Windows filesystem, calling convention, runtime, or ABI.


## DLL verification record, 2026-10-27

Source revision: `09f5b449a440e31bb349f6cd887b1c8d26f578cc` on
`AISurvivorSQLiteFixes-ChatGPT`. Full validation tree:
`4ec20de346a3c1118e8ab189b09854cae2e9a332` on
`AISurvivorSQLiteBuild-ChatGPT`, retaining AdvCiv 1.14 baseline
`5970334b64a875b5cdb370c94fc9a98db4eacda6` and its save-version 28 repairs.
SQLite remains 3.7.5; no vendor engine sources were changed during this pass.

[Exact workflow run](https://github.com/SuperXANA/AdvCiv/actions/runs/40536272889)
uses the configured Toolkit 2003 C/C++ compiler and linker, builds 83 selected
SQLite C translation units without the game PCH, creates sqlite3.lib, and passes
it explicitly into the DLL link. MSBuild 2010 is the project orchestrator.

| Configuration | Full rebuild | Artifact |
| --- | --- | --- |
| Release | Passed, including upload and cleanup | 12748562410 |
| Debug | Passed, including upload and cleanup | 12747604433 |

Release binary inspection: PE32 i386, 6,909,952 bytes, imports MSVCR71.dll,
msvcp71.dll, Python 2.4 and Boost VC71, and has no SQLite DLL import.
DLL SHA-256: `4a19d1a2ae26539390016af37b3aa2576b4e22f691f1ee43c701de943887d692`.

Portable C++03 default/schema-fixture suites and ASan/UBSan schema-fixture checks
passed against bundled 3.7.5. The final suite includes non-finite/range guards,
positive/negative fractional values, BUSY COMMIT retry, automatic rollback
ownership, foreign keys, and schema-recompiled column maps. The Windows path
syntax/type regression also passed. Fast configurations were inspected and their
project XML parsed; they were not separately built in this validation run.

Earlier run 40535483093 at da3bd25 passed both full configurations before the
additional range guards. Earlier failure runs 40532545391 (SSH quoting),
40532859809 (PCH directive), 40533396511 (CvGame include/wide literal),
40533695428 (archive tool launch), and 40534437815 (archive omitted from final
DLL link) were addressed by subsequent commits and should not be retried unchanged.

This establishes compiler/static-link compatibility. It does not execute the
DLL inside Beyond the Sword, exercise the Windows filesystem at runtime, or
validate savegame/multiplayer behavior. SQL_SCHEMA_VERSION remains zero; the
actual gameplay schema, migrations, replay semantics, authority, and event/memory
consumers remain implementation work.
