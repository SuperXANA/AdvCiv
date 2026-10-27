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

## Remaining integration design

Cross-save writes need explicit game/branch/event identity and replay semantics:
loading an earlier save must not silently double-count or retract committed
history. A transaction alone does not define that policy. Multiplayer must not
let independent local database contents influence synchronized gameplay without
a defined common snapshot/authority. Current filenames based on game names do
not establish globally unique game identity or synchronization. Persistent
schema migration, backup/recovery policy, complete error reporting, and actual
event/diplomacy consumers remain future work.
