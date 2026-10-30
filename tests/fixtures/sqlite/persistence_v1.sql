-- XANA: 10-30-2026 Inactive persistence protocol fixture; TEST INPUT ONLY.
-- Never install this file as Assets/SQL/CvGameDatabaseSchema.sql or change
-- SQL_SCHEMA_VERSION to activate it. No game hooks or migrations are supplied.
-- The test caller enables/verifies foreign_keys BEFORE BEGIN IMMEDIATE and
-- owns COMMIT/ROLLBACK. IDs and context encoding are supplied test inputs.

CREATE TABLE fixture_metadata (
    singleton INTEGER NOT NULL PRIMARY KEY CHECK (singleton = 1),
    format_id TEXT NOT NULL CHECK (format_id = 'mlpciv.persistence.fixture'),
    identity_protocol TEXT NOT NULL
        CHECK (identity_protocol = 'opaque-game-timeline-occurrence-v1')
);
INSERT INTO fixture_metadata VALUES
    (1, 'mlpciv.persistence.fixture', 'opaque-game-timeline-occurrence-v1');

CREATE TABLE game_record (
    game_id TEXT NOT NULL PRIMARY KEY CHECK (length(game_id) > 0),
    ruleset_key TEXT NOT NULL CHECK (length(ruleset_key) > 0)
);

CREATE TABLE timeline_record (
    game_id TEXT NOT NULL,
    timeline_id TEXT NOT NULL CHECK (length(timeline_id) > 0),
    PRIMARY KEY (game_id, timeline_id),
    FOREIGN KEY (game_id) REFERENCES game_record (game_id)
);

-- A participant is a particular game-local incarnation, not a cross-game
-- persona. XML names and slots are snapshots; neither is a durable identity.
CREATE TABLE participant_record (
    game_id TEXT NOT NULL,
    participant_id TEXT NOT NULL CHECK (length(participant_id) > 0),
    player_slot INTEGER NOT NULL
        CHECK (typeof(player_slot) = 'integer' AND player_slot BETWEEN 0 AND 2147483647),
    leader_key TEXT NOT NULL CHECK (length(leader_key) > 0),
    civilization_key TEXT NOT NULL CHECK (length(civilization_key) > 0),
    PRIMARY KEY (game_id, participant_id),
    FOREIGN KEY (game_id) REFERENCES game_record (game_id)
);

-- One externally identified observation, never a reconstruction of
-- m_mapEventsOccured. Memory changes without a random event can have their own
-- memory_observation source record. No SQL consequence follows from either.
CREATE TABLE event_record (
    game_id TEXT NOT NULL,
    timeline_id TEXT NOT NULL,
    occurrence_id TEXT NOT NULL CHECK (length(occurrence_id) > 0),
    sequence_no INTEGER NOT NULL
        CHECK (typeof(sequence_no) = 'integer' AND sequence_no BETWEEN 1 AND 2147483647),
    turn INTEGER NOT NULL
        CHECK (typeof(turn) = 'integer' AND turn BETWEEN 0 AND 2147483647),
    record_kind TEXT NOT NULL
        CHECK (record_kind IN ('event_application', 'memory_observation')),
    type_key TEXT NOT NULL CHECK (length(type_key) > 0),
    trigger_key TEXT CHECK (trigger_key IS NULL OR length(trigger_key) > 0),
    local_trigger_id INTEGER
        CHECK (local_trigger_id IS NULL OR
            (typeof(local_trigger_id) = 'integer' AND local_trigger_id BETWEEN 0 AND 2147483647)),
    actor_id TEXT NOT NULL,
    other_id TEXT,
    context_key TEXT NOT NULL,
    PRIMARY KEY (game_id, timeline_id, occurrence_id),
    UNIQUE (game_id, timeline_id, sequence_no),
    FOREIGN KEY (game_id, timeline_id)
        REFERENCES timeline_record (game_id, timeline_id),
    FOREIGN KEY (game_id, actor_id)
        REFERENCES participant_record (game_id, participant_id),
    FOREIGN KEY (game_id, other_id)
        REFERENCES participant_record (game_id, participant_id)
);

-- Directional, immutable observation of a delta, NOT a live AI memory count.
-- At most one delta for this observer/subject/type in one occurrence. Separate
-- mutations require separate occurrence IDs; retries must compare all payload.
CREATE TABLE memory_fact (
    game_id TEXT NOT NULL,
    timeline_id TEXT NOT NULL,
    occurrence_id TEXT NOT NULL,
    observer_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    memory_key TEXT NOT NULL CHECK (length(memory_key) > 0),
    delta INTEGER NOT NULL
        CHECK (typeof(delta) = 'integer' AND delta BETWEEN -2147483648 AND 2147483647 AND delta <> 0),
    PRIMARY KEY (game_id, timeline_id, occurrence_id, observer_id, subject_id, memory_key),
    FOREIGN KEY (game_id, timeline_id, occurrence_id)
        REFERENCES event_record (game_id, timeline_id, occurrence_id),
    FOREIGN KEY (game_id, observer_id)
        REFERENCES participant_record (game_id, participant_id),
    FOREIGN KEY (game_id, subject_id)
        REFERENCES participant_record (game_id, participant_id)
);

-- Reject mutation/retraction through ordinary DML. These guards are not a
-- security boundary against a connection allowed to alter/drop the schema.
-- REPLACE's implicit deletes need not fire DELETE triggers in SQLite 3.7.5;
-- reject duplicate keys before insertion, including the sequence UNIQUE key.
-- Exact retries belong in the adapter's SELECT-and-compare transaction.
CREATE TRIGGER fixture_metadata_no_replace BEFORE INSERT ON fixture_metadata
WHEN EXISTS (SELECT 1 FROM fixture_metadata WHERE singleton = NEW.singleton)
BEGIN SELECT RAISE(ABORT, 'duplicate fixture metadata'); END;
CREATE TRIGGER game_record_no_replace BEFORE INSERT ON game_record
WHEN EXISTS (SELECT 1 FROM game_record WHERE game_id = NEW.game_id)
BEGIN SELECT RAISE(ABORT, 'duplicate game identity'); END;
CREATE TRIGGER timeline_record_no_replace BEFORE INSERT ON timeline_record
WHEN EXISTS (SELECT 1 FROM timeline_record
    WHERE game_id = NEW.game_id AND timeline_id = NEW.timeline_id)
BEGIN SELECT RAISE(ABORT, 'duplicate timeline identity'); END;
CREATE TRIGGER participant_record_no_replace BEFORE INSERT ON participant_record
WHEN EXISTS (SELECT 1 FROM participant_record
    WHERE game_id = NEW.game_id AND participant_id = NEW.participant_id)
BEGIN SELECT RAISE(ABORT, 'duplicate participant identity'); END;
CREATE TRIGGER event_record_no_replace BEFORE INSERT ON event_record
WHEN EXISTS (SELECT 1 FROM event_record
    WHERE game_id = NEW.game_id AND timeline_id = NEW.timeline_id
    AND (occurrence_id = NEW.occurrence_id OR sequence_no = NEW.sequence_no))
BEGIN SELECT RAISE(ABORT, 'duplicate event identity or sequence'); END;
CREATE TRIGGER memory_fact_no_replace BEFORE INSERT ON memory_fact
WHEN EXISTS (SELECT 1 FROM memory_fact
    WHERE game_id = NEW.game_id AND timeline_id = NEW.timeline_id
    AND occurrence_id = NEW.occurrence_id AND observer_id = NEW.observer_id
    AND subject_id = NEW.subject_id AND memory_key = NEW.memory_key)
BEGIN SELECT RAISE(ABORT, 'duplicate memory identity'); END;
CREATE TRIGGER fixture_metadata_no_update BEFORE UPDATE ON fixture_metadata
BEGIN SELECT RAISE(ABORT, 'immutable fixture metadata'); END;
CREATE TRIGGER fixture_metadata_no_delete BEFORE DELETE ON fixture_metadata
BEGIN SELECT RAISE(ABORT, 'immutable fixture metadata'); END;
CREATE TRIGGER game_record_no_update BEFORE UPDATE ON game_record
BEGIN SELECT RAISE(ABORT, 'immutable game identity'); END;
CREATE TRIGGER game_record_no_delete BEFORE DELETE ON game_record
BEGIN SELECT RAISE(ABORT, 'immutable game identity'); END;
CREATE TRIGGER timeline_record_no_update BEFORE UPDATE ON timeline_record
BEGIN SELECT RAISE(ABORT, 'immutable timeline identity'); END;
CREATE TRIGGER timeline_record_no_delete BEFORE DELETE ON timeline_record
BEGIN SELECT RAISE(ABORT, 'immutable timeline identity'); END;
CREATE TRIGGER participant_record_no_update BEFORE UPDATE ON participant_record
BEGIN SELECT RAISE(ABORT, 'immutable participant identity'); END;
CREATE TRIGGER participant_record_no_delete BEFORE DELETE ON participant_record
BEGIN SELECT RAISE(ABORT, 'immutable participant identity'); END;
CREATE TRIGGER event_record_no_update BEFORE UPDATE ON event_record
BEGIN SELECT RAISE(ABORT, 'immutable event record'); END;
CREATE TRIGGER event_record_no_delete BEFORE DELETE ON event_record
BEGIN SELECT RAISE(ABORT, 'immutable event record'); END;
CREATE TRIGGER memory_fact_no_update BEFORE UPDATE ON memory_fact
BEGIN SELECT RAISE(ABORT, 'immutable memory fact'); END;
CREATE TRIGGER memory_fact_no_delete BEFORE DELETE ON memory_fact
BEGIN SELECT RAISE(ABORT, 'immutable memory fact'); END;

-- SQLite 3.7.5 user_version is transactional. Set only after all DDL succeeds.
PRAGMA user_version = 1;
-- XANA: END inactive persistence fixture.
