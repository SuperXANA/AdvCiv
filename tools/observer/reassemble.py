#!/usr/bin/env python3
"""Reassemble a finite version-2 receiver NDJSON log into capture NDJSON."""

import argparse
import json
import sys

import receiver


def missing_ranges(first, stop, seen):
    """Return inclusive ranges without expanding the expected index space."""
    ranges = []
    for index in sorted(seen):
        if first < index:
            ranges.append([first, index - 1])
        first = index + 1
    if first < stop:
        ranges.append([first, stop - 1])
    return ranges


class Player:
    def __init__(self, index, record):
        self.index = index
        self.metadata = {field: record[field] for field in record
                         if field not in ("city_part", "city_offset", "cities")}
        self.chunks = {}
        self.city_ids = set()

    def add(self, record, line, error):
        part = record["city_part"]
        if part in self.chunks:
            error("duplicate_city_part", line, player_index=self.index, city_part=part)
        fields = [field for field in self.metadata if self.metadata[field] != record[field]]
        if fields:
            error("player_metadata_mismatch", line, player_index=self.index, fields=fields)
        if fields or part in self.chunks:
            return
        self.chunks[part] = {field: record[field] for field in ("city_part", "city_offset", "cities")}
        for city in record["cities"]:
            city_id = city["id"]
            if city_id in self.city_ids:
                error("duplicate_city_id", line, player_index=self.index, city_id=city_id)
            self.city_ids.add(city_id)

    def result(self):
        missing = missing_ranges(0, self.metadata["city_part_count"], self.chunks)
        chunks = [self.chunks[part] for part in sorted(self.chunks)]
        result = dict(self.metadata, player_index=self.index, missing_city_part_ranges=missing)
        if missing:
            result["city_chunks"] = chunks
        else:
            result["cities"] = [city for chunk in chunks for city in chunk["cities"]]
        return result


class Capture:
    def __init__(self, key, metadata, line):
        self.key = key
        self.metadata = metadata
        self.first_line = line
        self.received_records = 0
        self.errors = []
        self.players = {}
        self.player_ids = {}

    def error(self, code, line, **details):
        self.errors.append(dict(details, code=code, line=line))

    def add(self, metadata, state, line):
        self.received_records += 1
        fields = [field for field in self.metadata if self.metadata[field] != metadata[field]]
        if fields:
            self.error("capture_metadata_mismatch", line, first_line=self.first_line, fields=fields)
            return
        if not state["players"]:
            if self.received_records > 1:
                self.error("duplicate_empty_world", line, first_line=self.first_line)
            return
        index = state["player_index"]
        record = state["players"][0]
        if index not in self.players:
            player_id = record["id"]
            if player_id in self.player_ids:
                self.error("duplicate_player_id", line, player_id=player_id, player_index=index,
                           other_player_index=self.player_ids[player_id])
            self.player_ids[player_id] = index
            self.players[index] = Player(index, record)
        self.players[index].add(record, line, self.error)

    def result(self):
        session_id, world_id, capture_id = self.key
        state = {"capture_id": capture_id}
        world = {"id": world_id, "state": state}
        session = {"id": session_id, "world_instance": world}
        diagnostics = {"received_records": self.received_records}
        if self.errors:
            status = "INVALID"
            diagnostics["errors"] = self.errors
        else:
            metadata = self.metadata
            session["sequence"] = metadata["session_sequence"]
            world.update(sequence=metadata["world_sequence"], map_seed=metadata["map_seed"])
            players = [self.players[index].result() for index in sorted(self.players)]
            missing = missing_ranges(0, metadata["player_count"], self.players)
            state.update(boundary=metadata["boundary"], game_turn=metadata["game_turn"],
                         player_count=metadata["player_count"], players=players)
            diagnostics["missing_player_index_ranges"] = missing
            status = ("INCOMPLETE" if missing or any(p["missing_city_part_ranges"] for p in players)
                      else "COMPLETE")
        return {"protocol": "advciv-observer", "version": 2, "type": "capture", "status": status,
                "game_session": session, "diagnostics": diagnostics}


class Session:
    def __init__(self):
        self.captures = {}
        self.snapshots = {}
        self.last_snapshot_id = 0

    def observe(self, capture, snapshot_id, line):
        capture_id = capture.key[2]
        first_capture = self.captures.setdefault(capture_id, capture)
        if first_capture is not capture and capture.received_records == 0:
            first_capture.error("capture_id_reused", line, other_world_id=capture.key[1])
            capture.error("capture_id_reused", line, other_world_id=first_capture.key[1])

        if snapshot_id in self.snapshots:
            first, first_line = self.snapshots[snapshot_id]
            details = dict(snapshot_id=snapshot_id, first_line=first_line)
            capture.error("duplicate_snapshot_id", line, **details)
            if first is not capture:
                first.error("duplicate_snapshot_id", line, **details)
            return
        if snapshot_id < self.last_snapshot_id:
            capture.error("snapshot_id_out_of_order", line, snapshot_id=snapshot_id,
                          previous_max_snapshot_id=self.last_snapshot_id)
        self.last_snapshot_id = max(snapshot_id, self.last_snapshot_id)
        self.snapshots[snapshot_id] = (capture, line)


def read_frames(stream):
    """Read each physical line once, retaining at most one frame plus one byte."""
    limit = receiver.MAX_LINE_BYTES + 1
    line = stream.readline(limit)
    while line:
        yield line
        while len(line) == limit and not line.endswith(b"\n"):
            line = stream.readline(limit)
        line = stream.readline(limit)


def reassemble(stream):
    """Yield diagnostics and reconstructed captures from a binary receiver log."""
    captures = {}
    sessions = {}
    for line, frame in enumerate(read_frames(stream), 1):
        try:
            if len(frame) > receiver.MAX_LINE_BYTES:
                raise receiver.ProtocolError("snapshot exceeds {}-byte frame limit".format(
                    receiver.MAX_LINE_BYTES))
            snapshot = receiver.parse_snapshot(frame)
        except (receiver.ProtocolError, RecursionError) as exc:
            yield {"type": "input_error", "line": line, "message": str(exc)}
            continue

        session = snapshot["game_session"]
        world = session["world_instance"]
        state = world["state"]
        session_id = session["id"]
        key = (session_id, world["id"].lower(), state["capture_id"])
        metadata = {"session_sequence": session["sequence"], "world_sequence": world["sequence"],
                    "map_seed": world["map_seed"], "boundary": state["boundary"],
                    "game_turn": state["game_turn"], "player_count": state["player_count"]}
        if session_id not in sessions:
            sessions[session_id] = Session()
        if key not in captures:
            captures[key] = Capture(key, metadata, line)
        capture = captures[key]
        sessions[session_id].observe(capture, state["snapshot_id"], line)
        capture.add(metadata, state, line)

    for session_id, session in sessions.items():
        for gap in missing_ranges(min(session.snapshots), session.last_snapshot_id + 1, session.snapshots):
            yield {"type": "snapshot_gap", "game_session_id": session_id,
                   "missing_snapshot_id_range": gap}
    for capture in captures.values():
        yield capture.result()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="receiver NDJSON file (default stdin)")
    args = parser.parse_args(argv)
    exit_code = 0
    stream = None
    try:
        stream = sys.stdin.buffer if args.input == "-" else open(args.input, "rb")
        for result in reassemble(stream):
            print(json.dumps(result, separators=(",", ":")))
            if result["type"] == "input_error" or result.get("status") == "INVALID":
                exit_code = 1
            elif result.get("status") == "INCOMPLETE" and exit_code == 0:
                exit_code = 2
        sys.stdout.flush()
    except OSError as exc:
        print("reassemble: " + str(exc), file=sys.stderr)
        return 1
    finally:
        if stream is not None and args.input != "-":
            stream.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
