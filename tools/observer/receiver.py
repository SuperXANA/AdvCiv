#!/usr/bin/env python3
"""Receive the opt-in AdvCiv observer's version-1 NDJSON snapshots.

    python3 tools/observer/receiver.py --port 37631 --output snapshots.ndjson
    python3 tools/observer/receiver.py --validate snapshots.ndjson

Only 127.0.0.1 may be bound. Forward the Windows loopback client to this
listener using a separately configured SSH tunnel. This is an observation-only
protocol: the receiver never sends commands or acknowledgements to the game.
The offline mode needs neither Civilization IV nor a tunnel.
"""

import argparse
from collections import OrderedDict
import json
import re
import socket
import sys
import threading
import time


MAX_LINE_BYTES = 512  # Includes the terminating LF.
MAX_SESSIONS = 64  # Bound receiver-side reconnect/deduplication history.
FIELDS = frozenset(("protocol", "version", "type", "session_id", "snapshot_id",
                    "boundary", "game_turn"))


class ProtocolError(ValueError):
    """A frame does not satisfy the supported observation protocol."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_snapshot(line):
    """Validate a complete bytes frame; return a detached dictionary."""
    if not isinstance(line, bytes) or not line.endswith(b"\n"):
        raise ProtocolError("snapshot must be a complete LF-terminated bytes frame")
    if len(line) > MAX_LINE_BYTES:
        raise ProtocolError("snapshot exceeds 512-byte frame limit")
    try:
        snapshot = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as exc:
        raise ProtocolError("invalid JSON: " + str(exc)) from exc
    if not isinstance(snapshot, dict) or frozenset(snapshot) != FIELDS:
        raise ProtocolError("snapshot must have exactly the version-1 fields")
    if snapshot["protocol"] != "advciv-observer":
        raise ProtocolError("unsupported protocol")
    if type(snapshot["version"]) is not int or snapshot["version"] != 1:
        raise ProtocolError("unsupported protocol version")
    if snapshot["type"] != "snapshot" or snapshot["boundary"] != "post_update":
        raise ProtocolError("unsupported message type or capture boundary")
    session = snapshot["session_id"]
    if not isinstance(session, str) or re.fullmatch(r"[0-9a-fA-F]{1,64}", session) is None:
        raise ProtocolError("session_id must be an ASCII hex token of 1-64 characters")
    identifier = snapshot["snapshot_id"]
    if type(identifier) is not int or not 1 <= identifier <= 0xffffffff:
        raise ProtocolError("snapshot_id must be a positive 32-bit unsigned integer")
    turn = snapshot["game_turn"]
    if type(turn) is not int or not -0x80000000 <= turn <= 0x7fffffff:
        raise ProtocolError("game_turn must be a signed 32-bit integer")
    return snapshot


class LineDecoder:
    """Bounded TCP framing; instantiate anew for every connection."""

    def __init__(self):
        self._pending = bytearray()

    def feed(self, chunk):
        """Yield complete snapshots; reject long frames without retaining them."""
        # Deliberately scan bounded recv chunks. Appending a whole peer-controlled
        # stream before checking its size would defeat the frame memory bound.
        for byte in chunk:
            self._pending.append(byte)
            if len(self._pending) > MAX_LINE_BYTES:
                self._pending.clear()
                raise ProtocolError("snapshot exceeds 512-byte frame limit")
            if byte == 10:
                line = bytes(self._pending)
                self._pending.clear()
                yield parse_snapshot(line)
            elif len(self._pending) == MAX_LINE_BYTES:
                self._pending.clear()
                raise ProtocolError("snapshot has no LF within 512-byte frame limit")

    def finish(self):
        """Offline files require complete frames; TCP EOF discards partial data."""
        if self._pending:
            raise ProtocolError("incomplete snapshot at end of file")


class SnapshotOrder:
    """Check monotonic IDs while retaining only the 64 most recent sessions.

    Gaps are expected when the bounded sender queue drops old observations.
    Game turns are not compared: a new/load session can start at any turn.
    An evicted session's ordering history is intentionally forgotten.
    """

    def __init__(self):
        self._last = OrderedDict()

    def accept(self, snapshot):
        session, identifier = snapshot["session_id"], snapshot["snapshot_id"]
        if identifier <= self._last.get(session, 0):
            raise ProtocolError("snapshot_id did not increase for this session")
        self._last[session] = identifier
        self._last.move_to_end(session)
        if len(self._last) > MAX_SESSIONS:
            self._last.popitem(last=False)


def validate_stream(stream, on_snapshot):
    """Validate an offline binary NDJSON stream and return its frame count."""
    decoder, order, count = LineDecoder(), SnapshotOrder(), 0
    while True:
        chunk = stream.read(512)
        if not chunk:
            break
        for snapshot in decoder.feed(chunk):
            order.accept(snapshot)
            on_snapshot(snapshot)
            count += 1
    decoder.finish()
    return count


class Receiver:
    """Single-client loopback listener with bounded reads and prompt shutdown.

    ``on_snapshot`` must return promptly; output failures propagate to the caller.
    Invalid, idle, disconnected, or truncated clients are closed and a subsequent
    connection may continue. Partial bytes never cross connection boundaries.
    ``request_stop`` is thread-safe; socket polling normally stops within 100 ms.
    """

    def __init__(self, on_snapshot, host="127.0.0.1", port=37631,
                 idle_timeout=5.0, on_error=None):
        if host != "127.0.0.1":
            raise ValueError("receiver host must be 127.0.0.1")
        if type(port) is not int or not 0 <= port <= 65535:
            raise ValueError("invalid receiver port")
        if not 0.1 <= idle_timeout <= 300:
            raise ValueError("idle timeout must be between 0.1 and 300 seconds")
        self._on_snapshot = on_snapshot
        self._on_error = on_error or (lambda message: None)
        self._idle_timeout = idle_timeout
        self._stop = threading.Event()
        self._order = SnapshotOrder()
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listener.bind((host, port))
            self._listener.listen(1)
            self._listener.settimeout(0.1)
            self.address = self._listener.getsockname()
        except BaseException:
            self._listener.close()
            raise

    def request_stop(self):
        self._stop.set()

    def close(self):
        self.request_stop()
        self._listener.close()

    def _receive(self, connection):
        decoder = LineDecoder()
        connection.settimeout(0.1)
        deadline = time.monotonic() + self._idle_timeout
        while not self._stop.is_set():
            try:
                chunk = connection.recv(512)
            except socket.timeout:
                if time.monotonic() >= deadline:
                    self._on_error("idle client disconnected")
                    return
                continue
            except OSError as exc:
                self._on_error("client disconnected: " + str(exc))
                return
            if not chunk:
                return  # A partial final frame is intentionally discarded.
            deadline = time.monotonic() + self._idle_timeout
            try:
                for snapshot in decoder.feed(chunk):
                    self._order.accept(snapshot)
                    self._on_snapshot(snapshot)
            except ProtocolError as exc:
                self._on_error(str(exc))
                return

    def serve(self):
        try:
            while not self._stop.is_set():
                try:
                    connection, _ = self._listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._stop.is_set():
                        break
                    raise
                with connection:
                    self._receive(connection)
        finally:
            self.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("127.0.0.1",), default="127.0.0.1")
    parser.add_argument("--port", type=int, default=37631)
    parser.add_argument("--idle-timeout", type=float, default=5.0)
    parser.add_argument("--output", help="write accepted snapshots as NDJSON (default stdout)")
    parser.add_argument("--validate", metavar="FILE", help="validate an offline NDJSON file and exit")
    args = parser.parse_args(argv)
    output = None
    try:
        if not 1 <= args.port <= 65535:
            parser.error("--port must be between 1 and 65535")
        if not 0.1 <= args.idle_timeout <= 300:
            parser.error("--idle-timeout must be between 0.1 and 300")
        if args.output and args.validate:
            from pathlib import Path
            if Path(args.output).resolve() == Path(args.validate).resolve():
                parser.error("--output must not overwrite the file being validated")
        output = open(args.output, "w", encoding="utf-8", buffering=1) if args.output else sys.stdout

        def emit(snapshot):
            output.write(json.dumps(snapshot, separators=(",", ":"), ensure_ascii=True) + "\n")
            output.flush()

        if args.validate:
            with open(args.validate, "rb") as source:
                count = validate_stream(source, emit)
            print("validated {} snapshot(s)".format(count), file=sys.stderr)
        else:
            receiver = Receiver(emit, args.host, args.port, args.idle_timeout,
                                lambda message: print(message, file=sys.stderr))
            print("listening on {}:{}".format(*receiver.address), file=sys.stderr)
            try:
                receiver.serve()
            except KeyboardInterrupt:
                receiver.close()
        return 0
    except (OSError, ProtocolError) as exc:
        print("receiver: " + str(exc), file=sys.stderr)
        return 1
    finally:
        if output is not None and output is not sys.stdout:
            output.close()


if __name__ == "__main__":
    sys.exit(main())
