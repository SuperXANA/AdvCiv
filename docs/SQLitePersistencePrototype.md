# Inactive SQLite persistence prototype

XANA: 2026-10-30 — schema and replay design fixture; production persistence remains disabled.

This prototype supplies a version-one schema fixture and focused tests for
cross-save event records and directional AI memory observations. It does not
activate the database manager, install a game schema, assign game identities,
change save serialization, or apply event or diplomatic consequences.

The source investigated is
[`AISurvivorSQLiteBuild-ChatGPT` at `c02eea47`](https://github.com/SuperXANA/AdvCiv/tree/c02eea47ded87b403ad9e2d36ba1824a59c14e8c).
The consolidated assistant branch is the development destination; the original
`AISurvivorStatTracking` branch and independent features are not integration
targets for this change. Existing wrapper, AdvCiv 1.14, C++03, MSVC 7.1, static
SQLite 3.7.5, and XANA annotation requirements remain in place.

## Inactive artifacts and version boundary

- Schema: [`tests/fixtures/sqlite/persistence_v1.sql`](../tests/fixtures/sqlite/persistence_v1.sql).
- Regression harness: [`tests/test_sqlite_persistence.py`](../tests/test_sqlite_persistence.py).
- Run from the repository root: `python tests/test_sqlite_persistence.py`.

The fixture declares `PRAGMA user_version = 1` and identifies its format as
`mlpciv.persistence.fixture`, with identity protocol
`opaque-game-timeline-occurrence-v1`. These are prototype compatibility markers,
not permission to enable an existing database. The test adapter checks the exact schema shape against a fresh fixture,
and both the version and metadata must match before accepting writes. Changing an XML key's interpretation or the
identity/replay protocol may require a new format or migration even when the
table layout appears compatible.

Production keeps `SQL_SCHEMA_VERSION (0)` in
[`CvDatabaseSchema.h`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvDatabaseSchema.h#L6).
[`CvDatabaseManager::init()`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvDatabaseManager.cpp#L89)
returns false at version zero. No fixture is installed at the manager's
`Assets/SQL/CvGameDatabaseSchema.sql` path, and no production initialization or
wrapper code changes are required.

An empty, explicitly created test database may receive the fixture in a
transaction. An existing unknown, older, newer, structurally mismatched, or metadata-mismatched
database must be rejected without mutation. Version zero is not sufficient
evidence that an existing database is empty or disposable. No automatic upgrade,
downgrade, repair, table deletion, or migration is supplied.

## Minimal record model

| Table | Identity and purpose | Deliberate boundary |
| --- | --- | --- |
| `game_record` | Opaque `game_id`, with a `ruleset_key` declaring interpretation of type keys. | A distinct game receives a distinct ID even when names, seeds, maps, and settings match. No generator is implemented. |
| `timeline_record` | Composite game and opaque timeline identity. | Separates explicitly registered continuations. It does not establish ancestry, replay authorization, or which timeline contributes to cross-game knowledge. |
| `participant_record` | Opaque participant ID scoped to a game, with player slot, leader XML key, and civilization XML key as context. | A slot or leader type is not a cross-game person identifier. No cross-game aliases or unique-slot policy are invented. |
| `event_record` | Composite `(game_id, timeline_id, occurrence_id)` primary key; `sequence_no` is also unique within a timeline. Records turn, kind, type key, optional trigger context, actor, optional other participant, and canonical context. | `event_application` and `memory_observation` distinguish source categories. Turn, local trigger ID, and XML type describe an occurrence; they do not identify it globally. |
| `memory_fact` | Composite source occurrence, observer, subject, and memory XML key, with a signed nonzero delta. | An inert directional fact associated with a source record; it is not an accumulated live memory count or attitude modifier. |

Foreign keys keep related records in the same game/timeline/occurrence namespace.
Immutable rows prevent a retry from silently becoming an edit or deletion. The
test writer explicitly compares every stored payload field before accepting an
existing key as an exact retry. A changed field, sequence collision, or
incomplete/different memory-fact set fails the whole write transaction; it must
not be hidden by `INSERT OR IGNORE` or overwrite an earlier record with
`INSERT OR REPLACE`.

The complete memory-fact set comparison belongs to the test adapter, not to the
SQL constraints alone. Append-only tables do not seal the membership of a
previously committed batch against an additional raw child insert. Unsupported
direct writes must not bypass the adapter; a production design must enforce its
complete-batch write boundary and authority explicitly.

Opaque IDs and canonical context values are supplied by the tests. Their
generation, canonical encoding, maximum size, collision resistance, and save
representation are unresolved production requirements. The SQL fixture cannot
prove two supplied IDs refer to the same real action, or that a declared ruleset
is the one actually running.

The sequence is a test ordering constraint, not the game's turn number and not
an implemented serialized checkpoint cursor. A single turn can contain multiple
events and memory changes. XML type names avoid persisting load-order enum
integers as durable semantic keys, but names still need versioned meaning and a
reviewed rename/mapping policy.

## What the existing event interfaces establish

[`EventTriggeredData`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvStructs.h#L114)
contains the local ID, trigger, turn, player, other player, and city/unit/plot
context. Its
[`read` and `write`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvStructs.cpp#L41)
serialize those values. They provide useful source context without providing a
globally unique event occurrence.

[`CvPlayer::initTriggeredData`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L15680)
allocates local data, sets player/turn/context, then can delete it if the Python
trigger check rejects it. Creation is not evidence that a chosen event was
successfully applied. The local
[`FFreeListTrashArray` allocator](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/FFreeListTrashArray.cpp#L95)
assigns an ID from its own counter. Its
[`save serialization`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/FFreeListTrashArray.cpp#L305)
restores that counter and the records. Loading an earlier save restores the
earlier allocation state; divergent later actions can therefore reuse future
local IDs already observed in an external database.

[`CvPlayer::applyEvent`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L16004)
finds triggered data and checks whether the chosen event can occur. It calls
`setTriggerFired` before that check can reject the event. The function later
[`applies additional events`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L16586)
recursively using the same trigger ID and can copy triggered data into a delayed
countdown while changing its turn. A trigger ID alone would collapse distinct
applications. Selecting the final successful logging boundary, including Python
callbacks and delayed/additional events, needs further integration design.

[`setEventOccured`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L15197)
stores one current value per event type and contains global/team propagation.
[`resetEventOccured`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L15186)
and
[`doEvents`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L16719)
remove entries. This map is current save state, not an append-only event history.
It cannot safely be backfilled as a complete cross-save journal, and propagated
copies must not automatically become separately counted source events.

## What the diplomacy interfaces establish

[`AI_getMemoryCount`, `AI_changeMemoryCount`, and `AI_setMemoryCount`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayerAI.cpp#L19033)
operate on directional observer/subject/memory-type counts. The setter also
adjusts cached attitude. Memory counts are already
[`read from saves`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayerAI.cpp#L23031)
with a historical enum migration and
[`written to saves`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayerAI.cpp#L23221).
They must not be blindly increased again when an external fact is read after
loading those same counts.

Event attitude fields already call these memory interfaces in
[`CvPlayer::applyEvent`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayer.cpp#L16425).
Other calls also perform
[`randomized memory decay`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvPlayerAI.cpp#L19555).
Consequently, a generic hook on every `AI_changeMemoryCount` call would mix new
incidents, decay, and bookkeeping. The prototype records inert observations;
it defines no new memories, decay rule, personality coefficient, aggregation,
or diplomatic consequence. Signed deltas are not permission to set a negative
live memory count.

A future design must distinguish the save's ordinary memory state from
cross-game recollection, decide which incidents qualify, map recurring identities
explicitly, and specify whether and how recollection affects any consumer.
The same leader XML key appearing in another game does not establish that all
variants or instances are the same remembered individual.

## Save replay contract and its limits

The fixture demonstrates the following database-level contract using supplied
identities:

1. A new occurrence and its complete memory-fact set commit together.
2. Retrying the exact same occurrence and facts returns the existing data.
3. Reopening the database and retrying after an uncertain acknowledgement does
   not create another occurrence or apply another delta.
4. Loading an old test cursor and replaying known exact records leaves the
   already committed future tail intact. It does not retract records merely
   because the selected save predates them.
5. Reusing a committed sequence position with a different identity or payload
   fails. No silent rewriting or automatic branch creation occurs.
6. An explicitly registered distinct timeline can contain distinct records.
   The fixture does not establish ancestry, inherited history, cross-fork
   deduplication, aggregation, or which timeline's records may satisfy a later
   prerequisite.

This contract detects conflicts only when the caller supplies comparable
identities and ordering. It does not generate identities for real Civ actions
or recognize two differently numbered replays as the same occurrence. A fresh
random ID on every load would defeat idempotency; a save-restored counter alone
would collide during divergent replay. Neither approach activates safe
persistence by itself.

Before production writes, specify a serialized game/timeline/checkpoint identity
and an action journal or equivalent protocol that recognizes acknowledged and
unacknowledged retries, detects divergence, and handles pending occurrences.
Define what happens on new game, map regeneration, scenario start, copied save,
legacy save lacking identity, and deliberate continuation fork. A legacy save
must not silently become a new game on every load or be merged with another
game because its name and seeds match.

The existing game name is
[`mutable`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvInitCore.cpp#L1498),
RNG seeds are
[`supplied to reproduce games`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvGame.cpp#L62),
and the
[`load session counter`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvGame.cpp#L9043)
changes on reload outside network multiplayer. None establishes durable game
identity. General game script data is serialized but
[`cleared during map regeneration`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvGame.cpp#L277)
and is available to Python; it is not an unowned identity slot.

SQLite commit and writing a BtS save are separate operations. A successful SQL
transaction does not commit a save or guarantee that the game completed its
associated effects. Activation requires explicit ordering and crash-recovery
rules for both directions of partial success. It also requires a decision about
when external history becomes visible to prerequisites, including what an older
save may learn from a later committed tail.

## Multiplayer and migration gates

The existing
[`database filename`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvDatabaseManager.cpp#L361)
adds the game name for multiplayer. This neither shares database contents nor
elects a writer. A local file's successful transaction cannot establish
multiplayer authority.

Before multiplayer activation, define one authority for game/timeline identity
and writes, an agreed ordered input history, and a versioned common snapshot for
every synchronized consumer. Independent local rows must not influence event
eligibility, AI choices, diplomatic counts, or RNG use. Specify host change,
reconnect, missing/conflicting database, PBEM/hotseat transfer, and incompatible
client behavior. The active player is not automatically the authority.

[`isGameMultiPlayer`](https://github.com/SuperXANA/AdvCiv/blob/c02eea47ded87b403ad9e2d36ba1824a59c14e8c/CvGameCoreDLL/CvGame.cpp#L4157)
normally covers network, PBEM, and hotseat but can return false when the debug
`m_bFeignSP` flag is set. Future gating must inspect the actual session mode and
authority, including this disguise, rather than relying solely on that helper.
The prototype has no multiplayer writer or synchronized reader.

Before any supported schema upgrade, supply an explicit source-to-target
migration, backup/recovery procedure, invariant checks, and rollback/failure
tests. Preserve unknown data on rejection. Changing a version marker alone is
not a migration. Identity and replay changes require the same care as SQL table
changes. The current fixture is experimental and cannot promise compatibility
with a future shipping schema.

## Verification and interpretation

| Evidence | Result | What it establishes |
| --- | --- | --- |
| New fixture regressions on bundled SQLite 3.7.5 | 14 tests passed on 2026-10-30; exact source ID `ed759d5a9edb3bba5f48f243df47be29e3fe8cd7`. | Database-level identity constraints, exact retries, reopen/old-cursor replay, atomic rollback/recovery, and rejection of incompatible metadata/versions for the tested helper. It does not exercise Civ save loading. |
| Existing wrapper regressions | Default and temporary version-one runs passed with bundled 3.7.5. Windows path-body syntax check and normal/UBSan integer-conversion checks passed. | Existing tested connection, transaction, binding, foreign-key, and version behavior under the portable harness. Civ stubs are not the BtS executable. |
| Historical native Release and Debug DLL build at `d31ca516d41e15ffd76a8a4a9807c58dc9d0c741` | [Run 40538272885 succeeded](https://github.com/SuperXANA/AdvCiv/actions/runs/40538272885). | MSVC 7.1 compilation and static SQLite 3.7.5 linkage for that exact historical revision. This fixture does not change DLL sources or require a new native build. |
| Actual Beyond the Sword execution | Not performed for this prototype. | No claim of working gameplay persistence, real save replay, runtime Windows path behavior, or multiplayer synchronization. |

The existing integer-conversion regression contained an extra closing parenthesis
in its oversized negative-text assertion. This test-only syntax error was
repaired with XANA annotations; no production value-conversion behavior changed.

The new harness calls the SQLite C API through Python `ctypes` and compiles
the same 83-source engine manifest with the core build macros into a temporary
host shared library. This host test library is not a game dependency or a
change to the statically linked Windows DLL. It never uses Python's system
`sqlite3` module. Tests simulate checkpoints and uncertain acknowledgements;
they do not parse a BtS save or simulate an operating-system crash.

No C++ integration change is justified by the fixture alone. Production stays
disabled until the save identity, replay/divergence, authority, migration, and
consumer contracts are sufficiently established and then validated in the
native DLL and Beyond the Sword runtime separately.
