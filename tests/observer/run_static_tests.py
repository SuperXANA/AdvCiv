#!/usr/bin/env python3
"""Compile/run the C++03 copied-data core and validate its actual NDJSON output.

Run on Linux with: python3 tests/observer/run_static_tests.py
This uses a pthread test lock adapter; it does not execute Windows transport,
MSVC, Civilization IV, a Windows VM, or an SSH tunnel. The native workflow runs
the same C++ tests with the original Windows critical-section implementation.
"""

import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError("duplicate JSON field: " + key)
        result[key] = value
    return result


def main():
    root = Path(__file__).resolve().parents[2]
    compiler = shlex.split(os.environ.get("CXX", "g++"))
    with tempfile.TemporaryDirectory(prefix="advciv-observer-tests-") as directory:
        executable = Path(directory) / "observer_tests"
        command = compiler + [
            "-std=c++03", "-Wall", "-Wextra", "-pedantic", "-Werror", "-pthread",
            "-DCV_OBSERVER_ENABLE", "-DCV_OBSERVER_TEST_POSIX",
            "-DCV_OBSERVER_STANDALONE", "-I", str(root / "CvGameCoreDLL"),
            str(root / "tests/observer/observer_standalone.cpp"),
            str(root / "tests/observer/observer_tests.cpp"),
            "-o", str(executable),
        ]
        subprocess.run(command, check=True, timeout=60)
        # Repeat actual producer/consumer interleavings, including overflow.
        for _ in range(3):
            subprocess.run([str(executable)], check=True, timeout=20)
        output = subprocess.run(
            [str(executable), "--emit-json"], check=True, capture_output=True,
            timeout=10,
        ).stdout
        lines = output.splitlines(keepends=True)
        if len(lines) != 3:
            raise AssertionError("expected three actual C++ formatter records")
        expected_ids = [1, 2, 4294967295]
        expected_turns = [0, -2147483648, 2147483647]
        for index, line in enumerate(lines):
            if not line.endswith(b"\n") or len(line) > 512:
                raise AssertionError("invalid NDJSON framing")
            record = json.loads(line.decode("ascii"), object_pairs_hook=unique_object)
            expected = {
                "protocol": "advciv-observer", "version": 1, "type": "snapshot",
                "session_id": "abc012", "snapshot_id": expected_ids[index],
                "boundary": "post_update", "game_turn": expected_turns[index],
            }
            if record != expected:
                raise AssertionError("C++ output did not match the v1 schema")
        print("PASS: Python json parsed all actual C++ formatter records and numeric edges")


if __name__ == "__main__":
    main()
