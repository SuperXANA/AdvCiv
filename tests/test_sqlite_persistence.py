#!/usr/bin/env python3
"""Inactive persistence protocol regressions against bundled SQLite 3.7.5.

This TEST-ONLY adapter supplies opaque identities; it does not discover game IDs,
read Civ4 saves, replay gameplay, or mutate live AI memory. It builds a temporary
shared host library from the native build's 83-source SQLite manifest. No system
SQLite, production initialization, C++ source, or installation asset is changed.
Run: python tests/test_sqlite_persistence.py
"""
# XANA: 10-30-2026 Inactive persistence fixture and replay regression adapter.
import contextlib
import ctypes
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/sqlite/persistence_v1.sql"
SQLITE_DIR = ROOT / "CvGameCoreDLL/sqlite"
SOURCE_ID = "2011-01-28 17:03:50 ed759d5a9edb3bba5f48f243df47be29e3fe8cd7"
EVENT_COLUMNS = (
    "game_id", "timeline_id", "occurrence_id", "sequence_no", "turn",
    "record_kind", "type_key", "trigger_key", "local_trigger_id", "actor_id",
    "other_id", "context_key",
)
MEMORY_COLUMNS = (
    "game_id", "timeline_id", "occurrence_id", "observer_id", "subject_id",
    "memory_key", "delta",
)


class SQLiteError(RuntimeError):
    pass


class FixtureError(RuntimeError):
    pass


class ReplayConflict(FixtureError):
    pass


class InjectedFailure(FixtureError):
    pass


def build_engine(directory):
    """Use exactly the native static-library source manifest and core macros."""
    manifest = (ROOT / "CvGameCoreDLL/BuildSQLite/Makefile.sqlite").read_text()
    names = list(dict.fromkeys(re.findall(
        r"\$\(SQLITE_OBJ_DIR\)\\([a-zA-Z0-9_]+)\.obj", manifest)))
    if len(names) != 83:
        raise AssertionError("SQLite manifest changed; review the test build")
    objects = []
    for name in names:
        obj = directory / (name + ".o")
        subprocess.run([
            "gcc", "-std=c89", "-w", "-fPIC", "-DSQLITE_CORE",
            "-DSQLITE_THREADSAFE=1", "-DSQLITE_OMIT_LOAD_EXTENSION",
            "-I", str(SQLITE_DIR), "-c", str(SQLITE_DIR / (name + ".c")),
            "-o", str(obj),
        ], check=True)
        objects.append(str(obj))
    library = directory / "libsqlite3_persistence_375.so"
    subprocess.run(["gcc", "-shared", "-o", str(library)] + objects +
                   ["-ldl", "-lpthread", "-lm"], check=True)
    api = ctypes.CDLL(str(library))
    signatures = {
        "sqlite3_libversion": (ctypes.c_char_p, []),
        "sqlite3_libversion_number": (ctypes.c_int, []),
        "sqlite3_sourceid": (ctypes.c_char_p, []),
        "sqlite3_open_v2": (ctypes.c_int, [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p),
                                         ctypes.c_int, ctypes.c_char_p]),
        "sqlite3_close": (ctypes.c_int, [ctypes.c_void_p]),
        "sqlite3_errmsg": (ctypes.c_char_p, [ctypes.c_void_p]),
        "sqlite3_exec": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_char_p,
                                      ctypes.c_void_p, ctypes.c_void_p,
                                      ctypes.POINTER(ctypes.c_void_p)]),
        "sqlite3_free": (None, [ctypes.c_void_p]),
        "sqlite3_prepare_v2": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_void_p),
                                            ctypes.c_void_p]),
        "sqlite3_bind_null": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_bind_int64": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int,
                                            ctypes.c_longlong]),
        "sqlite3_bind_double": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int,
                                             ctypes.c_double]),
        "sqlite3_bind_text": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int,
                                           ctypes.c_char_p, ctypes.c_int,
                                           ctypes.c_void_p]),
        "sqlite3_step": (ctypes.c_int, [ctypes.c_void_p]),
        "sqlite3_finalize": (ctypes.c_int, [ctypes.c_void_p]),
        "sqlite3_column_count": (ctypes.c_int, [ctypes.c_void_p]),
        "sqlite3_column_type": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_column_int64": (ctypes.c_longlong, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_column_double": (ctypes.c_double, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_column_text": (ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_column_blob": (ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_int]),
        "sqlite3_column_bytes": (ctypes.c_int, [ctypes.c_void_p, ctypes.c_int]),
    }
    for name, (result, arguments) in signatures.items():
        function = getattr(api, name)
        function.restype = result
        function.argtypes = arguments
    assert api.sqlite3_libversion() == b"3.7.5"
    assert api.sqlite3_libversion_number() == 3007005
    assert api.sqlite3_sourceid().decode("ascii") == SOURCE_ID
    return api


class Connection:
    """Small host C API harness; deliberately independent of gameplay wrappers."""
    def __init__(self, api, path, *, create=True):
        self.api = api
        self.handle = ctypes.c_void_p()
        flags = 0x00000002 | (0x00000004 if create else 0)  # READWRITE [| CREATE]
        status = api.sqlite3_open_v2(str(path).encode("utf-8"), ctypes.byref(self.handle),
                                    flags, None)
        if status:
            error = api.sqlite3_errmsg(self.handle).decode("utf-8")
            self.close()
            raise SQLiteError(error)
        try:
            # This must be enabled outside a transaction on EVERY reopened handle.
            self.exec("PRAGMA foreign_keys=ON")
            if self.scalar("PRAGMA foreign_keys") != 1:
                raise FixtureError("foreign key enforcement unavailable")
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.handle:
            status = self.api.sqlite3_close(self.handle)
            if status:
                raise SQLiteError("SQLite close failed: %d" % status)
            self.handle = ctypes.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _check(self, status):
        if status:
            raise SQLiteError("%d: %s" %
                              (status, self.api.sqlite3_errmsg(self.handle).decode("utf-8")))

    def exec(self, sql):
        error = ctypes.c_void_p()
        status = self.api.sqlite3_exec(self.handle, sql.encode("utf-8"),
                                       None, None, ctypes.byref(error))
        try:
            self._check(status)
        finally:
            if error:
                self.api.sqlite3_free(error)

    def query(self, sql, parameters=()):
        statement = ctypes.c_void_p()
        self._check(self.api.sqlite3_prepare_v2(
            self.handle, sql.encode("utf-8"), -1, ctypes.byref(statement), None))
        try:
            for index, value in enumerate(parameters, 1):
                if value is None:
                    status = self.api.sqlite3_bind_null(statement, index)
                elif isinstance(value, int):
                    status = self.api.sqlite3_bind_int64(statement, index, value)
                elif isinstance(value, float):
                    status = self.api.sqlite3_bind_double(statement, index, value)
                elif isinstance(value, str):
                    encoded = value.encode("utf-8")
                    status = self.api.sqlite3_bind_text(statement, index, encoded,
                                                       len(encoded), ctypes.c_void_p(-1))
                else:
                    raise TypeError("unsupported fixture parameter")
                self._check(status)
            rows = []
            while True:
                status = self.api.sqlite3_step(statement)
                if status == 101:  # SQLITE_DONE
                    return rows
                if status != 100:  # SQLITE_ROW
                    self._check(status)
                row = []
                for column in range(self.api.sqlite3_column_count(statement)):
                    kind = self.api.sqlite3_column_type(statement, column)
                    if kind == 1:
                        value = self.api.sqlite3_column_int64(statement, column)
                    elif kind == 2:
                        value = self.api.sqlite3_column_double(statement, column)
                    elif kind in (3, 4):
                        pointer = (self.api.sqlite3_column_text(statement, column)
                                   if kind == 3 else
                                   self.api.sqlite3_column_blob(statement, column))
                        size = self.api.sqlite3_column_bytes(statement, column)
                        value = ctypes.string_at(pointer, size) if size else b""
                        if kind == 3:
                            value = value.decode("utf-8")
                    else:
                        value = None
                    row.append(value)
                rows.append(tuple(row))
        finally:
            self.api.sqlite3_finalize(statement)

    def scalar(self, sql, parameters=()):
        rows = self.query(sql, parameters)
        if len(rows) != 1 or len(rows[0]) != 1:
            raise FixtureError("expected exactly one scalar")
        return rows[0][0]

    @contextlib.contextmanager
    def transaction(self):
        self.exec("BEGIN IMMEDIATE")
        try:
            yield
            self.exec("COMMIT")
        except BaseException:
            self.exec("ROLLBACK")
            raise

    def signature(self):
        return self.query("SELECT type,name,tbl_name,sql FROM sqlite_master "
                          "ORDER BY type,name")


class FixtureStore:
    """TEST-ONLY policy example, not an operational persistence interface.

    No ID is derived here from a seed, turn, player slot, or trigger allocator.
    Callers supply stable game/timeline/occurrence/participant IDs. A stale save
    with a new occurrence at an occupied sequence fails; only an explicit new
    timeline permits divergence. Existing events require an exact memory set.
    """
    def __init__(self, api, path, schema, expected_signature, *, create=False):
        self.db = Connection(api, path, create=create)
        self.schema = schema
        self.expected_signature = expected_signature
        try:
            version = self.db.scalar("PRAGMA user_version")
            if version == 0:
                if not create or self.db.scalar("SELECT count(*) FROM sqlite_master"):
                    raise FixtureError("not an explicitly approved empty fixture database")
                with self.db.transaction():
                    self.db.exec(schema)
                    self.validate()
            else:
                self.validate()
        except BaseException:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def validate(self):
        if self.db.scalar("PRAGMA user_version") != 1:
            raise FixtureError("unsupported fixture version; no automatic migration")
        if self.db.signature() != self.expected_signature:
            raise FixtureError("unsupported fixture shape; do not repair automatically")
        if self.db.query("SELECT singleton,format_id,identity_protocol FROM fixture_metadata") != [
            (1, "mlpciv.persistence.fixture", "opaque-game-timeline-occurrence-v1")
        ]:
            raise FixtureError("incompatible fixture format or identity protocol")

    def _ensure(self, table, columns, key_count, values):
        # Table/column strings are fixed trusted harness constants; bind all data.
        where = " AND ".join(name + "=?" for name in columns[:key_count])
        old = self.db.query("SELECT " + ",".join(columns) + " FROM " + table +
                            " WHERE " + where, values[:key_count])
        if old:
            if old != [tuple(values)]:
                raise ReplayConflict("same %s identity, different payload" % table)
            return 0
        self.db.query("INSERT INTO " + table + " (" + ",".join(columns) +
                      ") VALUES (" + ",".join("?" for _ in columns) + ")", values)
        return 1

    def seed(self, game="game-A", timeline="main"):
        with self.db.transaction():
            self._ensure("game_record", ("game_id", "ruleset_key"), 1,
                         (game, "fixture-rules-v1"))
            self._ensure("timeline_record", ("game_id", "timeline_id"), 2,
                         (game, timeline))
            columns = ("game_id", "participant_id", "player_slot", "leader_key",
                       "civilization_key")
            self._ensure("participant_record", columns, 2,
                         (game, "pony-A", 0, "LEADER_FIXTURE_A", "CIVILIZATION_FIXTURE"))
            self._ensure("participant_record", columns, 2,
                         (game, "pony-B", 1, "LEADER_FIXTURE_B", "CIVILIZATION_FIXTURE"))

    def apply_batch(self, records, *, fail_after_inserts=None):
        """Atomic observations only; an unknown acknowledgement is retried whole.

        No OR IGNORE/REPLACE, live counters, or loading-time deletion. A successful
        return counts newly inserted rows; zero means an exactly identical retry.
        """
        inserted = 0
        with self.db.transaction():
            for event, memories in records:
                values = tuple(event[name] for name in EVENT_COLUMNS)
                identity = values[:3]
                expected_memories = [tuple(memory[name] for name in MEMORY_COLUMNS)
                                     for memory in memories]
                if any(row[:3] != identity for row in expected_memories):
                    raise ReplayConflict("memory must belong to its source occurrence")
                keys = [row[:-1] for row in expected_memories]
                if len(set(keys)) != len(keys):
                    raise ReplayConflict("duplicate memory identity in requested batch")
                existing = self.db.query(
                    "SELECT " + ",".join(EVENT_COLUMNS) + " FROM event_record "
                    "WHERE game_id=? AND timeline_id=? AND occurrence_id=?", identity)
                if existing:
                    if existing != [values]:
                        raise ReplayConflict("same occurrence identity, different event")
                    actual_memories = self.db.query(
                        "SELECT " + ",".join(MEMORY_COLUMNS) + " FROM memory_fact "
                        "WHERE game_id=? AND timeline_id=? AND occurrence_id=?", identity)
                    if sorted(actual_memories) != sorted(expected_memories):
                        raise ReplayConflict("same occurrence identity, different memory set")
                    continue
                inserted += self._ensure("event_record", EVENT_COLUMNS, 3, values)
                if inserted == fail_after_inserts:
                    raise InjectedFailure("simulated failure after event insertion")
                for memory in expected_memories:
                    inserted += self._ensure("memory_fact", MEMORY_COLUMNS, 6, memory)
                    if inserted == fail_after_inserts:
                        raise InjectedFailure("simulated failure after memory insertion")
        return inserted


def observation(occurrence="occurrence-1", sequence=1, *, game="game-A", timeline="main"):
    """Synthetic test data. XML-style names introduce no gameplay consequence."""
    event = dict(zip(EVENT_COLUMNS, (
        game, timeline, occurrence, sequence, 20, "event_application",
        "EVENT_FIXTURE_ONLY", "EVENTTRIGGER_FIXTURE_ONLY", 7,
        "pony-A", "pony-B", json.dumps({"fixture": "canonical context"},
                                       sort_keys=True, separators=(",", ":")),
    )))
    memory = dict(zip(MEMORY_COLUMNS, (
        game, timeline, occurrence, "pony-A", "pony-B", "MEMORY_DECLARED_WAR", 1,
    )))
    return event, [memory]


class PersistenceRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_directory = tempfile.TemporaryDirectory(prefix="advciv-persistence-engine-")
        cls.api = build_engine(pathlib.Path(cls.build_directory.name))
        cls.schema = FIXTURE.read_text()
        with Connection(cls.api, ":memory:") as reference:
            reference.exec(cls.schema)
            cls.signature = reference.signature()
        print("Bundled engine: SQLite 3.7.5; source ID " + SOURCE_ID, flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.build_directory.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="advciv-persistence-case-")
        self.addCleanup(self.directory.cleanup)
        self.path = pathlib.Path(self.directory.name) / "fixture.sqlite"
        self.stores = []
        self.addCleanup(self.close_stores)

    def close_stores(self):
        for store in self.stores:
            store.close()

    def store(self, *, create=True, schema=None):
        store = FixtureStore(self.api, self.path, self.schema if schema is None else schema,
                             self.signature, create=create)
        self.stores.append(store)
        return store

    def rows(self, store):
        return (store.db.query("SELECT * FROM event_record ORDER BY game_id,timeline_id,sequence_no"),
                store.db.query("SELECT * FROM memory_fact ORDER BY game_id,timeline_id,occurrence_id,observer_id,subject_id,memory_key"))

    def test_production_is_still_disabled(self):
        header = (ROOT / "CvGameCoreDLL/CvDatabaseSchema.h").read_text()
        self.assertRegex(header, r"#define\s+SQL_SCHEMA_VERSION\s+\(0\)")
        self.assertFalse((ROOT / "Assets/SQL/CvGameDatabaseSchema.sql").exists())
        self.assertEqual(FIXTURE.relative_to(ROOT).parts[0], "tests")

    def test_exact_retries_and_same_identity_changed_payload(self):
        store = self.store()
        store.seed()
        event, memories = observation()
        self.assertEqual(store.apply_batch([(event, memories)]), 2)
        before = self.rows(store)
        for _ in range(3):
            self.assertEqual(store.apply_batch([(event, memories)]), 0)
        for field, altered in (("context_key", "different"), ("turn", 21),
                               ("type_key", "EVENT_DIFFERENT"), ("actor_id", "pony-B")):
            with self.subTest(field=field):
                changed = dict(event, **{field: altered})
                with self.assertRaises(ReplayConflict):
                    store.apply_batch([(changed, memories)])
        with self.assertRaises(ReplayConflict):
            store.apply_batch([(event, [dict(memories[0], delta=2)])])
        with self.assertRaises(ReplayConflict):
            store.apply_batch([(event, [])])
        with self.assertRaises(ReplayConflict):
            store.apply_batch([(event, memories + [dict(memories[0], memory_key="MEMORY_FIXTURE_EXTRA")])])
        self.assertEqual(self.rows(store), before)

    def test_game_timeline_and_participant_identity_are_separate(self):
        store = self.store()
        for game, timeline in (("game-A", "main"), ("game-B", "main"), ("game-A", "explicit-fork")):
            store.seed(game, timeline)
            self.assertEqual(store.apply_batch([observation(game=game, timeline=timeline)]), 2)
        self.assertEqual(store.db.scalar("SELECT count(*) FROM event_record"), 3)
        self.assertEqual(store.db.scalar("SELECT count(*) FROM memory_fact"), 3)
        # Reusing a player slot for a new incarnation does not reuse the person ID.
        store.db.query("INSERT INTO participant_record VALUES (?,?,?,?,?)",
                       ("game-A", "pony-C-incarnation", 0, "LEADER_FIXTURE_A", "CIVILIZATION_FIXTURE"))
        self.assertEqual(store.db.scalar("SELECT count(*) FROM participant_record WHERE game_id=? AND player_slot=?",
                                        ("game-A", 0)), 2)

    def test_memory_observation_has_no_random_event_requirement(self):
        store = self.store()
        store.seed()
        event, memories = observation()
        event.update(record_kind="memory_observation", type_key="MEMORY_DECLARED_WAR",
                     trigger_key=None, local_trigger_id=None, actor_id="pony-B", other_id=None,
                     context_key=json.dumps({"fixture": "direct memory observation"},
                                            sort_keys=True, separators=(",", ":")))
        memories[0].update(observer_id="pony-B", subject_id="pony-A", delta=-2)
        self.assertEqual(store.apply_batch([(event, memories)]), 2)
        self.assertEqual(store.apply_batch([(event, memories)]), 0)
        self.assertEqual(store.db.query("SELECT record_kind,trigger_key,local_trigger_id,other_id "
                                        "FROM event_record"),
                         [("memory_observation", None, None, None)])
        self.assertEqual(store.db.query("SELECT observer_id,subject_id,delta FROM memory_fact"),
                         [("pony-B", "pony-A", -2)])

    def test_reopen_old_checkpoint_and_uncertain_acknowledgement(self):
        store = self.store()
        store.seed()
        earlier_save = [observation()]
        store.apply_batch(earlier_save)
        future = observation("occurrence-2", 2)
        store.apply_batch([future])  # Pretend process stopped before caller saw acknowledgement.
        committed = self.rows(store)
        store.close()
        for _ in range(3):
            store = self.store(create=False)
            store.seed()
            self.assertEqual(store.db.scalar("PRAGMA foreign_keys"), 1)
            self.assertEqual(store.apply_batch(earlier_save), 0)
            self.assertEqual(store.apply_batch([future]), 0)
            self.assertEqual(self.rows(store), committed)  # Loading retracts no future fact.
            store.close()

    def test_divergent_old_save_requires_explicit_timeline(self):
        store = self.store()
        store.seed()
        store.apply_batch([observation(), observation("committed-future", 2)])
        before = self.rows(store)
        with self.assertRaises(SQLiteError):
            store.apply_batch([observation("different-future", 2)])
        self.assertEqual(self.rows(store), before)
        store.seed(timeline="explicit-fork")
        self.assertEqual(store.apply_batch([observation("different-future", 2, timeline="explicit-fork")]), 2)

    def test_failure_rolls_back_whole_batch_then_retry_succeeds(self):
        store = self.store()
        store.seed()
        original = self.rows(store)
        event, memories = observation()
        memories.append(dict(memories[0], observer_id="pony-B", subject_id="pony-A", delta=-1))
        with self.assertRaises(InjectedFailure):
            store.apply_batch([(event, memories)], fail_after_inserts=2)
        self.assertEqual(self.rows(store), original)
        self.assertEqual(store.apply_batch([(event, memories)]), 3)
        # A real constraint failure after a valid event+memory must also roll back.
        first = observation("batch-2", 2)
        bad_event, bad_memories = observation("batch-3", 3)
        bad_memories[0]["subject_id"] = "missing-participant"
        before = self.rows(store)
        with self.assertRaises(SQLiteError):
            store.apply_batch([first, (bad_event, bad_memories)])
        self.assertEqual(self.rows(store), before)
        self.assertEqual(store.apply_batch([first]), 2)

    def test_orphans_and_invalid_scalar_payloads_are_rejected(self):
        store = self.store()
        store.seed()
        for field, value in (("actor_id", "unknown"), ("sequence_no", 0),
                             ("sequence_no", 2147483648), ("sequence_no", 1.5),
                             ("turn", -1), ("record_kind", "unknown"),
                             ("local_trigger_id", -1)):
            with self.subTest(field=field, value=value):
                event, memories = observation()
                event[field] = value
                with self.assertRaises(SQLiteError):
                    store.apply_batch([(event, memories)])
                self.assertEqual(self.rows(store), ([], []))
        for delta in (0, 2147483648, -2147483649, 1.5):
            with self.subTest(delta=delta):
                event, memories = observation()
                memories[0]["delta"] = delta
                with self.assertRaises(SQLiteError):
                    store.apply_batch([(event, memories)])
                self.assertEqual(self.rows(store), ([], []))
        orphan = tuple(observation()[1][0][column] for column in MEMORY_COLUMNS)
        with self.assertRaises(SQLiteError):
            store.db.query("INSERT INTO memory_fact VALUES (?,?,?,?,?,?,?)", orphan)
        self.assertEqual(self.rows(store), ([], []))

    def test_append_only_and_replace_cannot_retract_history(self):
        store = self.store()
        store.seed()
        event, memories = observation()
        store.apply_batch([(event, memories)])
        before = self.rows(store)
        # 3.7.5 defaults recursive triggers OFF. REPLACE must fail even then.
        store.db.exec("PRAGMA recursive_triggers=OFF")
        self.assertEqual(store.db.scalar("PRAGMA recursive_triggers"), 0)
        for table in ("fixture_metadata", "game_record", "timeline_record",
                      "participant_record", "event_record", "memory_fact"):
            with self.subTest(table=table):
                for verb in ("UPDATE " + table + " SET " +
                             ("singleton=singleton" if table == "fixture_metadata" else "game_id=game_id"),
                             "DELETE FROM " + table):
                    with self.assertRaises(SQLiteError):
                        store.db.exec(verb)
                # Complete duplicate payloads also cannot bypass immutable guards.
                with self.assertRaises(SQLiteError):
                    store.db.exec("INSERT OR REPLACE INTO " + table + " SELECT * FROM " + table)
        changed = dict(event, context_key="replacement must fail")
        divergent = dict(event, occurrence_id="different-at-same-sequence")
        for replacement in (changed, divergent):
            with self.assertRaises(SQLiteError):
                store.db.query("INSERT OR REPLACE INTO event_record VALUES (" +
                               ",".join("?" for _ in EVENT_COLUMNS) + ")",
                               tuple(replacement[column] for column in EVENT_COLUMNS))
        with self.assertRaises(SQLiteError):
            store.db.exec("INSERT OR IGNORE INTO event_record SELECT * FROM event_record")
        self.assertEqual(self.rows(store), before)

    def test_unversioned_existing_database_is_preserved(self):
        with Connection(self.api, self.path) as raw:
            raw.exec("CREATE TABLE sentinel(v); INSERT INTO sentinel VALUES(73)")
        before = self.path.read_bytes()
        with self.assertRaises(FixtureError):
            self.store()
        self.assertEqual(self.path.read_bytes(), before)
        with Connection(self.api, self.path) as raw:
            self.assertEqual(raw.scalar("SELECT v FROM sentinel"), 73)
            self.assertEqual(raw.scalar("PRAGMA user_version"), 0)

    def test_unknown_versions_and_formats_are_preserved(self):
        cases = ("negative", "future", "missing-metadata", "missing-table")
        for case in cases:
            with self.subTest(case=case):
                path = pathlib.Path(self.directory.name) / (case + ".sqlite")
                with Connection(self.api, path) as raw:
                    if case in ("negative", "future", "missing-metadata"):
                        raw.exec("CREATE TABLE sentinel(v); INSERT INTO sentinel VALUES(73)")
                        raw.exec("PRAGMA user_version=" + {"negative": "-1", "future": "2", "missing-metadata": "1"}[case])
                    else:
                        raw.exec(self.schema)
                        # Construct malformed input externally, not through the adapter.
                        raw.exec("DROP TABLE memory_fact")
                        raw.exec("CREATE TABLE sentinel(v); INSERT INTO sentinel VALUES(73)")
                    version = raw.scalar("PRAGMA user_version")
                before = path.read_bytes()
                with self.assertRaises(FixtureError):
                    FixtureStore(self.api, path, self.schema, self.signature, create=True)
                self.assertEqual(path.read_bytes(), before)
                with Connection(self.api, path) as raw:
                    self.assertEqual(raw.scalar("SELECT v FROM sentinel"), 73)
                    self.assertEqual(raw.scalar("PRAGMA user_version"), version)

    def test_metadata_mismatch_with_exact_schema_is_preserved(self):
        # Simulate externally corrupted content without changing the schema shape.
        # This is test input construction, never a recovery mechanism.
        for field in ("format_id", "identity_protocol"):
            with self.subTest(field=field):
                path = pathlib.Path(self.directory.name) / (field + ".sqlite")
                with Connection(self.api, path) as raw:
                    raw.exec(self.schema)
                    raw.query("INSERT INTO game_record VALUES (?,?)", ("sentinel", "73"))
                    trigger_sql = raw.scalar("SELECT sql FROM sqlite_master WHERE name=?",
                                             ("fixture_metadata_no_update",))
                    raw.exec("DROP TRIGGER fixture_metadata_no_update")
                    raw.exec("PRAGMA ignore_check_constraints=ON")
                    raw.query("UPDATE fixture_metadata SET " + field + "=?", ("incompatible",))
                    raw.exec(trigger_sql)
                    raw.exec("PRAGMA ignore_check_constraints=OFF")
                    self.assertEqual(raw.signature(), self.signature)
                before = path.read_bytes()
                with self.assertRaisesRegex(FixtureError, "format or identity protocol"):
                    FixtureStore(self.api, path, self.schema, self.signature, create=True)
                self.assertEqual(path.read_bytes(), before)
                with Connection(self.api, path) as raw:
                    self.assertEqual(raw.scalar("SELECT ruleset_key FROM game_record WHERE game_id=?",
                                                ("sentinel",)), "73")
                    self.assertEqual(raw.scalar("PRAGMA user_version"), 1)

    def test_empty_database_requires_explicit_creation(self):
        with self.assertRaises(SQLiteError):
            self.store(create=False)
        self.assertFalse(self.path.exists())
        with Connection(self.api, self.path) as raw:
            self.assertEqual(raw.scalar("PRAGMA user_version"), 0)
            self.assertEqual(raw.scalar("SELECT count(*) FROM sqlite_master"), 0)
        before = self.path.read_bytes()
        with self.assertRaises(FixtureError):
            self.store(create=False)
        self.assertEqual(self.path.read_bytes(), before)
        store = self.store()
        self.assertEqual(store.db.scalar("PRAGMA user_version"), 1)

    def test_schema_install_failure_rolls_back_ddl_and_version(self):
        with self.assertRaises(SQLiteError):
            self.store(schema=self.schema + "\nTHIS IS INTENTIONALLY INVALID SQL;")
        with Connection(self.api, self.path) as raw:
            self.assertEqual(raw.scalar("SELECT count(*) FROM sqlite_master"), 0)
            self.assertEqual(raw.scalar("PRAGMA user_version"), 0)
        # A script that succeeds but declares a wrong version must roll back too.
        with self.assertRaises(FixtureError):
            self.store(schema=self.schema + "\nPRAGMA user_version=2;")
        with Connection(self.api, self.path) as raw:
            self.assertEqual(raw.scalar("SELECT count(*) FROM sqlite_master"), 0)
            self.assertEqual(raw.scalar("PRAGMA user_version"), 0)
        self.store()  # Failed bootstrap remains retryable.


if __name__ == "__main__":
    unittest.main(verbosity=2)
# XANA: END inactive persistence regression adapter.
