"""Offline regression tests using synthetic version-2 observations."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_receiver import PLAYER, SESSION, STATE, WORLD, city_chunk, encode, nested, snapshot


TOOLS = Path(__file__).resolve().parents[2] / "tools" / "observer"


def record(snapshot_id, *, capture_id=1, player_index=0, player_count=1,
           player_id=0, civilization_type=1, city_count=1, city_part=0,
           session_id="abc123", session_sequence=1, world_sequence=1,
           map_seed=0x89abcdef, turn=42):
    if player_count:
        item = city_chunk(city_count, city_part)
        nested(item, PLAYER).update(id=player_id, civilization_type=civilization_type)
    else:
        item = snapshot()
        nested(item, STATE)["players"] = []
        player_index = -1

    nested(item, SESSION).update(id=session_id, sequence=session_sequence)
    nested(item, WORLD).update(id="{:08x}-{:08x}".format(map_seed, world_sequence),
                               sequence=world_sequence, map_seed=map_seed)
    nested(item, STATE).update(capture_id=capture_id, snapshot_id=snapshot_id,
                               game_turn=turn, player_count=player_count,
                               player_index=player_index)
    return item


class ReassemblyTests(unittest.TestCase):
    def run_cli(self, items=(), *, input_path=None):
        command = [sys.executable, str(TOOLS / "reassemble.py")]
        if input_path is not None:
            command.append(str(input_path))
        data = b"".join(item if isinstance(item, bytes) else encode(item) for item in items)
        result = subprocess.run(command, input=data, capture_output=True, timeout=5)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        return result.returncode, rows

    def test_receiver_output_reassembles_civilizations_and_large_empire(self):
        large_empire = dict(player_count=3, player_id=2, civilization_type=4, city_count=65)
        items = [record(part + 1, city_part=part, **large_empire) for part in range(3)]
        items.extend((record(4, player_count=3, player_index=1, player_id=7, civilization_type=9),
                      record(5, player_count=3, player_index=2, player_id=12,
                             civilization_type=13, city_count=0)))

        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "raw.ndjson"
            validated = Path(temporary) / "validated.ndjson"
            raw.write_bytes(b"".join(map(encode, items)))
            receiver = subprocess.run([sys.executable, str(TOOLS / "receiver.py"),
                                       "--validate", str(raw), "--output", str(validated)],
                                      capture_output=True, timeout=5)
            self.assertEqual(receiver.returncode, 0, receiver.stderr)
            code, (capture,) = self.run_cli(input_path=validated)

        self.assertEqual((code, capture["type"], capture["status"]), (0, "capture", "COMPLETE"))
        state = nested(capture, STATE)
        self.assertEqual((state["capture_id"], state["boundary"], state["game_turn"],
                          state["player_count"]), (1, "post_update", 42, 3))
        players = state["players"]
        self.assertEqual([(p["player_index"], p["id"], p["civilization_type"]) for p in players],
                         [(0, 2, 4), (1, 7, 9), (2, 12, 13)])
        self.assertEqual(players[0]["cities"],
                         [city for item in items[:3] for city in nested(item, PLAYER)["cities"]])
        self.assertEqual((players[0]["city_count"], players[0]["total_population"]), (65, 195))
        self.assertEqual(players[2]["cities"], [])
        self.assertEqual(capture["diagnostics"]["missing_player_index_ranges"], [])

    def test_no_alive_players_is_a_complete_empty_world(self):
        code, (capture,) = self.run_cli([record(1, player_count=0)])
        self.assertEqual((code, capture["status"]), (0, "COMPLETE"))
        self.assertEqual(nested(capture, STATE)["player_count"], 0)
        self.assertEqual(nested(capture, STATE)["players"], [])

    def test_missing_middle_chunk_preserves_received_offsets_without_inventing_cities(self):
        first = record(1, city_count=65)
        last = record(3, city_count=65, city_part=2)
        code, (gap, capture) = self.run_cli([first, last])
        self.assertEqual((gap["type"], gap["game_session_id"], gap["missing_snapshot_id_range"]),
                         ("snapshot_gap", "abc123", [2, 2]))
        self.assertEqual((code, capture["status"]), (2, "INCOMPLETE"))
        self.assertEqual(capture["diagnostics"]["missing_player_index_ranges"], [])
        player, = nested(capture, STATE)["players"]
        self.assertEqual(player["missing_city_part_ranges"], [[1, 1]])
        self.assertNotIn("cities", player)
        chunks = player["city_chunks"]
        self.assertEqual([(chunk["city_part"], chunk["city_offset"]) for chunk in chunks],
                         [(0, 0), (2, 64)])
        self.assertEqual([chunk["cities"] for chunk in chunks],
                         [nested(item, PLAYER)["cities"] for item in (first, last)])

    def test_queue_loss_leaves_missing_player_ranges_and_preserves_next_capture(self):
        # A missing prefix, an entirely absent capture, then two complete captures.
        code, (gap, *captures) = self.run_cli([
            record(4, player_count=4, player_index=3, player_id=12),
            record(8, capture_id=3, turn=44),
            record(9, capture_id=4, turn=45),
        ])
        self.assertEqual(code, 2)
        self.assertEqual((gap["type"], gap["missing_snapshot_id_range"]), ("snapshot_gap", [5, 7]))
        self.assertEqual([nested(row, STATE)["capture_id"] for row in captures], [1, 3, 4])
        self.assertEqual([row["status"] for row in captures], ["INCOMPLETE", "COMPLETE", "COMPLETE"])
        self.assertEqual(captures[0]["diagnostics"]["missing_player_index_ranges"], [[0, 2]])
        self.assertEqual([p["id"] for p in nested(captures[0], STATE)["players"]], [12])

    def test_duplicate_record_and_logical_chunk_are_invalid(self):
        for repeated, reason in ((record(1), "duplicate_snapshot_id"),
                                 (record(2), "duplicate_city_part"),
                                 (record(2, civilization_type=9), "duplicate_city_part")):
            with self.subTest(repeated=repeated):
                code, (capture,) = self.run_cli([record(1), repeated])
                self.assertEqual((code, capture["status"]), (1, "INVALID"))
                self.assertNotIn("players", nested(capture, STATE))
                self.assertIn(reason, [error["code"] for error in capture["diagnostics"]["errors"]])

    def test_conflicting_capture_and_player_metadata_are_invalid(self):
        first = record(1, player_count=2)
        second_player = dict(player_count=2, player_index=1, player_id=1)
        cases = [(first, record(2, player_count=3, player_index=1, player_id=1),
                  "capture_metadata_mismatch"),
                 (first, record(2, turn=43, **second_player), "capture_metadata_mismatch"),
                 (first, record(2, session_sequence=2, **second_player), "capture_metadata_mismatch"),
                 (record(1, city_count=33), record(2, city_count=33, city_part=1, player_id=1),
                  "player_metadata_mismatch")]
        for first, second, reason in cases:
            with self.subTest(second=second):
                code, (capture,) = self.run_cli([first, second])
                self.assertEqual((code, capture["status"]), (1, "INVALID"))
                self.assertNotIn("players", nested(capture, STATE))
                self.assertIn(reason, [error["code"] for error in capture["diagnostics"]["errors"]])

    def test_complete_city_lists_follow_offsets_and_reject_duplicate_ids(self):
        tail = record(1, city_count=33, city_part=1)
        head = record(2, city_count=33)
        code, (capture,) = self.run_cli([tail, head])
        self.assertEqual((code, capture["status"]), (0, "COMPLETE"))
        player, = nested(capture, STATE)["players"]
        self.assertEqual([city["id"] for city in player["cities"]], list(range(33)))

        nested(tail, PLAYER)["cities"][0]["id"] = 0
        code, (capture,) = self.run_cli([tail, head])
        self.assertEqual((code, capture["status"]), (1, "INVALID"))
        self.assertIn("duplicate_city_id", [error["code"] for error in capture["diagnostics"]["errors"]])

    def test_reused_player_capture_and_snapshot_ids_invalidate_affected_captures(self):
        cases = [([record(1, player_count=2), record(2, player_count=2, player_index=1)],
                  1, "duplicate_player_id"),
                 ([record(1), record(2, world_sequence=2)], 2, "capture_id_reused"),
                 ([record(1), record(1, capture_id=2)], 2, "duplicate_snapshot_id")]
        for items, count, reason in cases:
            with self.subTest(reason=reason):
                code, captures = self.run_cli(items)
                self.assertEqual((code, len(captures)), (1, count))
                for capture in captures:
                    self.assertEqual(capture["status"], "INVALID")
                    self.assertNotIn("players", nested(capture, STATE))
                    self.assertIn(reason, [error["code"] for error in capture["diagnostics"]["errors"]])

    def test_invalid_frames_have_separate_line_diagnostics(self):
        wrong_offset = record(2, city_count=33, city_part=1)
        nested(wrong_offset, PLAYER)["city_offset"] = 0
        wrong_index = record(3, city_count=33, city_part=1)
        nested(wrong_index, PLAYER).update(city_part=2, city_offset=64)
        code, rows = self.run_cli([record(1, city_count=33), wrong_offset, wrong_index, b"not JSON\n"])
        self.assertEqual(code, 1)
        errors = [row for row in rows if row["type"] == "input_error"]
        self.assertEqual([error["line"] for error in errors], [2, 3, 4])
        self.assertTrue(all(error["message"] for error in errors))
        captures = [row for row in rows if row["type"] == "capture"]
        self.assertEqual([row["status"] for row in captures], ["INCOMPLETE"])

    def test_oversize_line_is_skipped_and_truncated_line_is_reported(self):
        code, (oversize, truncated, capture) = self.run_cli([
            b"x" * 9000 + b"\n", record(1), encode(record(2, capture_id=2))[:-1],
        ])
        self.assertEqual(code, 1)
        self.assertEqual([(row["type"], row["line"]) for row in (oversize, truncated)],
                         [("input_error", 1), ("input_error", 3)])
        self.assertEqual((capture["status"], nested(capture, STATE)["capture_id"]), ("COMPLETE", 1))

    def test_map_regeneration_and_new_session_keep_captures_separate(self):
        code, (gap, *captures) = self.run_cli([
            record(1, city_count=33, turn=0),
            record(3, capture_id=2, world_sequence=2, turn=0, player_id=3),
            record(1, session_id="def456", session_sequence=2, turn=-3, player_id=4),
        ])
        self.assertEqual(code, 2)
        self.assertEqual((gap["type"], gap["game_session_id"], gap["missing_snapshot_id_range"]),
                         ("snapshot_gap", "abc123", [2, 2]))
        self.assertEqual([(nested(capture, SESSION)["id"], nested(capture, WORLD)["sequence"],
                           nested(capture, STATE)["capture_id"], capture["status"])
                          for capture in captures],
                         [("abc123", 1, 1, "INCOMPLETE"), ("abc123", 2, 2, "COMPLETE"),
                          ("def456", 1, 1, "COMPLETE")])
        worlds = [nested(capture, WORLD) for capture in captures]
        self.assertEqual(worlds[0]["id"], worlds[2]["id"])
        self.assertNotEqual(worlds[0]["id"], worlds[1]["id"])
        self.assertEqual({world["map_seed"] for world in worlds}, {0x89abcdef})
        self.assertEqual([nested(capture, STATE)["game_turn"] for capture in captures], [0, 0, -3])


if __name__ == "__main__":
    unittest.main()
