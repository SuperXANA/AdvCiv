"""Focused offline/Linux TCP tests; these do not exercise the Windows DLL."""

import importlib.util
import io
import json
from pathlib import Path
import queue
import socket
import threading
import time
import unittest


SPEC = importlib.util.spec_from_file_location(
    "observer_receiver", Path(__file__).resolve().parents[2] / "tools/observer/receiver.py")
receiver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(receiver)


SESSION = ("game_session",)
WORLD = SESSION + ("world_instance",)
STATE = WORLD + ("state",)
PLAYER = STATE + ("players", 0)
CITY = PLAYER + ("cities", 0)


def snapshot(identifier=1, session="abc123", turn=42):
    return {
        "protocol": "advciv-observer", "version": 2, "type": "snapshot",
        "game_session": {
            "id": session, "sequence": 1,
            "world_instance": {
                "id": "89abcdef-00000001", "sequence": 1, "map_seed": 0x89abcdef,
                "state": {
                    "capture_id": 1, "snapshot_id": identifier, "boundary": "post_update",
                    "game_turn": turn, "player_count": 1, "player_index": 0,
                    "players": [{
                        "id": 0, "team_id": 0, "civilization_type": 1, "leader_type": 2,
                        "is_human": True, "is_barbarian": False,
                        "city_count": 1, "total_population": 3,
                        "city_offset": 0, "city_part": 0, "city_part_count": 1,
                        "cities": [{"id": 10, "x": 20, "y": 30, "population": 3}]
                    }]
                }
            }
        }
    }


def encode(item):
    return (json.dumps(item, separators=(",", ":")) + "\n").encode("ascii")


def frame(identifier=1, session="abc123", turn=42):
    return encode(snapshot(identifier, session, turn))


def nested(item, path):
    for key in path:
        item = item[key]
    return item


def mutation(path, value):
    item = snapshot()
    nested(item, path[:-1])[path[-1]] = value
    return encode(item)


def city_chunk(city_count, part):
    item = snapshot()
    player = nested(item, PLAYER)
    offset = part * 32
    player.update(city_count=city_count, total_population=city_count * 3,
                  city_offset=offset, city_part=part,
                  city_part_count=max(1, (city_count + 31) // 32))
    player["cities"] = [dict(id=offset + index, x=index, y=-index, population=3)
                        for index in range(max(0, min(32, city_count - offset)))]
    return item


class ProtocolTests(unittest.TestCase):
    def test_json_round_trip_scalar_limits_and_empty_world(self):
        expected = snapshot(0xffffffff, "a" * 64, -0x80000000)
        nested(expected, SESSION)["sequence"] = 0xffffffff
        nested(expected, WORLD).update(id="00000000-ffffffff", sequence=0xffffffff, map_seed=0)
        nested(expected, STATE)["capture_id"] = 0xffffffff
        self.assertEqual(receiver.parse_snapshot(encode(expected)), expected)
        self.assertEqual(receiver.parse_snapshot(frame(1, "A", 0x7fffffff)), snapshot(1, "A", 0x7fffffff))

        uppercase = snapshot()
        nested(uppercase, WORLD)["id"] = "89ABCDEF-00000001"
        self.assertEqual(receiver.parse_snapshot(encode(uppercase)), uppercase)
        empty = snapshot()
        nested(empty, STATE).update(player_count=0, player_index=-1, players=[])
        self.assertEqual(receiver.parse_snapshot(encode(empty)), empty)

    def test_reject_invalid_json_duplicates_and_exact_hierarchy(self):
        bad = [b"not JSON\n", b"[]\n", b"\xff\n", frame()[:-1],
               frame().replace(b'"version":2', b'"version":2,"version":2'),
               frame().replace(b'"capture_id":1', b'"capture_id":1,"capture_id":1'),
               frame().replace(b'"game_turn":42', b'"game_turn":NaN')]
        containers = [(), SESSION, WORLD, STATE, PLAYER, CITY]
        for path in containers:
            item = snapshot()
            nested(item, path)["extra"] = 7
            bad.append(encode(item))
            item = snapshot()
            target = nested(item, path)
            del target[next(iter(target))]
            bad.append(encode(item))
        for path in (SESSION, WORLD, STATE, STATE + ("players",), PLAYER,
                     PLAYER + ("cities",), CITY):
            bad.append(mutation(path, []))
        for line in bad:
            with self.subTest(line=line), self.assertRaises(receiver.ProtocolError):
                receiver.parse_snapshot(line)

    def test_reject_invalid_scalar_types_and_bounds(self):
        cases = [
            (("protocol",), ("other", 1)),
            (("type",), ("command", 1)),
            (("version",), (1, 3, True, 2.0)),
            (SESSION + ("id",), ("", "not hex", "a" * 65, "é", 1)),
            (SESSION + ("sequence",), (True, 0, -1, 0x100000000, 1.0)),
            (WORLD + ("id",), ("89abcdef00000001", "89abcde-00000001",
                                  "89abcdef-000000001", "gggggggg-00000001",
                                  "89abcdee-00000001", "89abcdef-00000002", 1)),
            (WORLD + ("sequence",), (False, 0, 0x100000000, 1.0)),
            (WORLD + ("map_seed",), (True, -1, 0x100000000, 1.0)),
            (STATE + ("capture_id",), (True, 0, 0x100000000, 1.0)),
            (STATE + ("snapshot_id",), (True, 0, 0x100000000, "1")),
            (STATE + ("boundary",), ("before_update", 1)),
            (STATE + ("game_turn",), (False, 1.0, -0x80000001, 0x80000000)),
            (STATE + ("player_count",), (True, -1, 0x80000000, 1.0)),
            (STATE + ("player_index",), (True, -2, 0x80000000, 1.0)),
            (PLAYER + ("is_human",), (0, 1, "true")),
            (PLAYER + ("is_barbarian",), (0, 1, "false")),
            (PLAYER + ("city_count",), (True, -1, 0x80000000)),
            (PLAYER + ("total_population",), (True, -1, 0x80000000)),
            (PLAYER + ("city_offset",), (True, -1, 0x80000000)),
            (PLAYER + ("city_part",), (True, -1, 0x80000000)),
            (PLAYER + ("city_part_count",), (True, 0, -1, 0x80000000)),
            (CITY + ("population",), (True, -1, 0x80000000))
        ]
        for field in ("id", "team_id", "civilization_type", "leader_type"):
            cases.append((PLAYER + (field,), (True, -0x80000001, 0x80000000)))
        for field in ("id", "x", "y"):
            cases.append((CITY + (field,), (True, -0x80000001, 0x80000000)))
        for path, values in cases:
            for value in values:
                with self.subTest(path=path, value=value), self.assertRaises(receiver.ProtocolError):
                    receiver.parse_snapshot(mutation(path, value))

    def test_player_presence_and_index_invariants(self):
        cases = [(0, 0, "empty"), (0, -1, "one"), (1, 0, "empty"),
                 (1, -1, "one"), (1, 1, "one"), (2, 2, "one"), (1, 0, "two")]
        for count, index, contents in cases:
            item = snapshot()
            included = nested(item, PLAYER)
            players = {"empty": [], "one": [included], "two": [included, dict(included)]}[contents]
            nested(item, STATE).update(player_count=count, player_index=index, players=players)
            with self.subTest(count=count, index=index, contents=contents), self.assertRaises(receiver.ProtocolError):
                receiver.parse_snapshot(encode(item))

    def test_city_chunk_boundaries_and_cross_field_invariants(self):
        for count in (0, 1, 32, 33, 64, 65):
            for part in range(max(1, (count + 31) // 32)):
                item = city_chunk(count, part)
                with self.subTest(valid_count=count, valid_part=part):
                    self.assertEqual(receiver.parse_snapshot(encode(item)), item)

        invalid = [city_chunk(33, 2), city_chunk(0, 1)]
        for count, part, path, value in [
                (33, 1, ("city_offset",), 0),
                (33, 1, ("city_part_count",), 1),
                (33, 1, ("cities",), []),
                (33, 0, ("cities",), [{"id": 10, "x": 20, "y": 30, "population": 3}]),
                (32, 0, ("city_part",), 1)]:
            item = city_chunk(count, part)
            nested(item, PLAYER + path[:-1])[path[-1]] = value
            invalid.append(item)
        item = city_chunk(32, 0)
        nested(item, PLAYER)["cities"].append(dict(id=99, x=0, y=0, population=1))
        invalid.append(item)
        item = city_chunk(32, 0)
        nested(item, PLAYER).update(city_part=1, city_offset=32, cities=[])
        invalid.append(item)
        for item in invalid:
            with self.subTest(player=nested(item, PLAYER)), self.assertRaises(receiver.ProtocolError):
                receiver.parse_snapshot(encode(item))

    def test_fragmentation_coalescing_and_bounded_framing(self):
        decoder = receiver.LineDecoder()
        self.assertEqual(list(decoder.feed(frame()[:11])), [])
        self.assertEqual(list(decoder.feed(frame()[11:] + frame(2))), [snapshot(), snapshot(2)])
        decoder.finish()

        base = frame()
        maximum = base[:-1] + b" " * (receiver.MAX_LINE_BYTES - len(base)) + b"\n"
        self.assertEqual(len(maximum), 4096)
        self.assertEqual(list(receiver.LineDecoder().feed(maximum)), [snapshot()])
        with self.assertRaises(receiver.ProtocolError):
            receiver.parse_snapshot(maximum[:-1] + b" \n")
        for chunk in (b"x" * 4096, b"x" * 4097 + b"\n"):
            with self.subTest(size=len(chunk)), self.assertRaises(receiver.ProtocolError):
                list(receiver.LineDecoder().feed(chunk))
        decoder = receiver.LineDecoder()
        self.assertEqual(list(decoder.feed(frame()[:-1])), [])
        with self.assertRaises(receiver.ProtocolError):
            decoder.finish()

    def test_offline_order_gaps_sessions_and_truncation(self):
        accepted = []
        data = frame() + frame(5) + frame(1, "def456", -3)
        self.assertEqual(receiver.validate_stream(io.BytesIO(data), accepted.append), 3)
        self.assertEqual([nested(item, STATE)["snapshot_id"] for item in accepted], [1, 5, 1])
        for data in (frame() + frame(), frame(5) + frame(4), frame()[:-1]):
            with self.assertRaises(receiver.ProtocolError):
                receiver.validate_stream(io.BytesIO(data), lambda item: None)

    def test_order_history_is_bounded(self):
        order = receiver.SnapshotOrder()
        for index in range(1000):
            order.accept(snapshot(session=format(index, "x")))
        self.assertEqual(len(order._last), receiver.MAX_SESSIONS)


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.messages, self.errors, self.failures = queue.Queue(), queue.Queue(), queue.Queue()
        self.server = receiver.Receiver(self.messages.put, port=0, idle_timeout=0.2,
                                        on_error=self.errors.put)

        def serve():
            try:
                self.server.serve()
            except BaseException as exc:
                self.failures.put(exc)

        self.thread = threading.Thread(target=serve, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.request_stop()
        self.thread.join(1.5)
        self.assertFalse(self.thread.is_alive(), "receiver shutdown exceeded 1.5 seconds")
        self.assertTrue(self.failures.empty(), list(self.failures.queue))

    def connect(self):
        return socket.create_connection(self.server.address, timeout=1)

    def test_tcp_split_coalesced_frames(self):
        with self.connect() as client:
            client.sendall(frame()[:19])
            client.sendall(frame()[19:] + frame(2))
            self.assertEqual(self.messages.get(timeout=1), snapshot())
            self.assertEqual(self.messages.get(timeout=1), snapshot(2))

    def test_disconnect_discards_partial_frame_and_reconnects(self):
        with self.connect() as client:
            client.sendall(frame()[:-1])
        with self.connect() as client:
            client.sendall(frame(2))
            self.assertEqual(self.messages.get(timeout=1), snapshot(2))
        self.assertTrue(self.messages.empty())

    def test_invalid_client_and_duplicate_reconnect_do_not_kill_listener(self):
        with self.connect() as client:
            client.sendall(frame())
            self.assertEqual(self.messages.get(timeout=1), snapshot())
        with self.connect() as client:
            client.sendall(frame())
            self.assertIn("did not increase", self.errors.get(timeout=1))
        with self.connect() as client:
            client.sendall(b"x" * 4096)
            self.assertIn("4096-byte", self.errors.get(timeout=1))
        with self.connect() as client:
            client.sendall(frame(3))
            self.assertEqual(self.messages.get(timeout=1), snapshot(3))

    def test_idle_receiver_accepts_later_client(self):
        with self.connect():
            self.assertIn("idle", self.errors.get(timeout=1))
        with self.connect() as client:
            client.sendall(frame())
            self.assertEqual(self.messages.get(timeout=1), snapshot())

    def test_shutdown_with_connected_silent_client(self):
        with self.connect():
            started = time.monotonic()
            self.server.request_stop()
            self.thread.join(1)
            self.assertFalse(self.thread.is_alive())
            self.assertLess(time.monotonic() - started, 1)

    def test_refuses_non_loopback_and_invalid_configuration(self):
        for kwargs in ({"host": "0.0.0.0"}, {"port": -1}, {"idle_timeout": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                receiver.Receiver(lambda item: None, **kwargs)


if __name__ == "__main__":
    unittest.main()
