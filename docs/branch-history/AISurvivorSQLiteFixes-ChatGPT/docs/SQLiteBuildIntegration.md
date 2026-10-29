# AISurvivor SQLite build integration

Prepared for the pinned AISurvivorStatTracking source f2575de4bb94f561d3e1f0df651489487e3742ae and AdvCiv 1.14 base 5970334b64a875b5cdb370c94fc9a98db4eacda6.

- Bundled SQLite remains 3.7.5 (source ID ed759d5a9edb3bba5f48f243df47be29e3fe8cd7).
- C source manifest follows LIBOBJS0 from the official version-3.7.5 Makefile.in: https://github.com/sqlite/sqlite/blob/version-3.7.5/Makefile.in . It excludes the command-line shell and legacy standalone FTS1/FTS2 extensions. Optional/platform implementations remain guarded by their own upstream macros.
- The omitted sqlite3ext.h is restored from https://github.com/sqlite/sqlite/blob/version-3.7.5/src/sqlite3ext.h . loadext.c includes it even when loading extensions is disabled.
- SQLITE_OMIT_LOAD_EXTENSION deliberately disables unused dynamic extension loading; it is not a schema change. SQLITE_THREADSAFE=1 preserves synchronized library use. SQLITE_CORE matches the upstream integrated-extension build convention.
- Project/AISurvivorSQLite.vcxproj is an additive copy of the pinned base project; its NMake commands use BuildSQLite/Makefile.sqlite. That wrapper includes the machine's Project/Makefile and Makefile.user, compiles SQLite as C (/TC) without the game's precompiled header (/Y-), and uses the additive sqlite_dll target to link that archive explicitly into the DLL. The archive is made by the configured MSVC 7.1 link.exe /lib, avoiding a dependency on a separate lib.exe. Ordinary and JOM configurations use the same target. /MD matches the base project runtime convention.
- The separately prepared complete-tree build workflow (not included in this sparse branch) is copied from dll-build 058e4d0e1760f76195071823d3e2dc85c81b7285, with exact branch trigger, complete-tree source path, explicitly allowed additive project file, original machine Project files excluded, a stale-root-source manifest rejection, Rebuild, exact fresh artifact path, and fail-on-missing artifact. It never deletes unknown remote sources.
- All copied core files must preserve the latest 1.14 save migration, especially CvGame save flag 28 and onAllGameDataRead religion/corporation count repair.

## Checks performed

83 bundled SQLite C translation units compiled with GCC in C89 mode. Static library linked to a smoke program, opening an in-memory database, creating/inserting a table, executing and rolling back a transaction, reporting SQLite 3.7.5, and closing cleanly. This is not VC++2003 compilation, full DLL validation, or in-game testing.

Before publishing, recheck the chosen branch refs and queued/in-progress workflows, reconcile active user edits, and review the workflow diff. Shared concurrency prevents overlap only with workflows using the same group; user-triggered/manual external builds cannot be proven absent by GitHub status alone.


The isolated validation workflow now runs ordinary Release and Debug sequentially
under the shared workspace concurrency group. Each uses Rebuild, requires a fresh
configuration-specific DLL, uploads a separate artifact, and completes cleanup.
MSBuild 2010 orchestrates the project; the actual C/C++ compiler and linker remain
the machine-configured Microsoft Visual C++ Toolkit 2003 (MSVC 7.1).


## Full DLL validation

The complete source/commit mapping, per-configuration results, artifact IDs,
Release PE inspection, regression coverage and limitations are recorded in
[SQLiteSafetyReview.md](SQLiteSafetyReview.md#dll-verification-record-2026-10-27).
Exact run: https://github.com/SuperXANA/AdvCiv/actions/runs/40536272889 .
