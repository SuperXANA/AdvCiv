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


def snapshot(identifier=1, session="abc123", turn=42):
    return {"protocol": "advciv-observer", "version": 1, "type": "snapshot",
            "session_id": session, "snapshot_id": identifier,
            "boundary": "post_update", "game_turn": turn}


def frame(identifier=1, session="abc123", turn=42):
    return (json.dumps(snapshot(identifier, session, turn), separators=(",", ":")) + "\n").encode("ascii")


class ProtocolTests(unittest.TestCase):
    def test_json_round_trip_and_limits(self):
        expected = snapshot(0xffffffff, "a" * 64, -0x80000000)
        line = (json.dumps(expected) + "\n").encode()
        self.assertLessEqual(len(line), 512)
        self.assertEqual(receiver.parse_snapshot(line), expected)

    def test_reject_invalid_json_metadata_types_and_fields(self):
        bad = [b"not JSON\n", b"[]\n", b"\xff\n", frame()[:-1],
               frame().replace(b'"version":1', b'"version":1,"version":1')]
        mutations = (("version", 2), ("version", True), ("version", 1.0),
                     ("snapshot_id", True), ("snapshot_id", 0),
                     ("snapshot_id", 0x100000000), ("snapshot_id", "1"),
                     ("game_turn", False), ("game_turn", 1.0),
                     ("game_turn", 0x80000000), ("session_id", "not hex"),
                     ("session_id", ""), ("session_id", "a" * 65),
                     ("boundary", "before_update"), ("type", "command"),
                     ("protocol", "other"), ("extra", 7))
        for key, value in mutations:
            item = snapshot()
            item[key] = value
            bad.append((json.dumps(item) + "\n").encode())
        item = snapshot()
        del item["game_turn"]
        bad.append((json.dumps(item) + "\n").encode())
        for line in bad:
            with self.subTest(line=line), self.assertRaises(receiver.ProtocolError):
                receiver.parse_snapshot(line)

    def test_fragmentation_coalescing_and_bounded_framing(self):
        decoder = receiver.LineDecoder()
        self.assertEqual(list(decoder.feed(frame()[:11])), [])
        self.assertEqual(list(decoder.feed(frame()[11:] + frame(2))), [snapshot(), snapshot(2)])
        decoder.finish()
        for chunk in (b"x" * 512, b"x" * 513 + b"\n"):
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
        self.assertEqual([item["snapshot_id"] for item in accepted], [1, 5, 1])
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
            client.sendall(b"x" * 512)
            self.assertIn("512-byte", self.errors.get(timeout=1))
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
