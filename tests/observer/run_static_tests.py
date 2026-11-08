#!/usr/bin/env python3
"""Compile/run the C++03 copied-data core and validate its actual NDJSON output.

Run on Linux with: python3 tests/observer/run_static_tests.py
This uses a pthread test lock adapter; it does not execute Windows transport,
MSVC, Civilization IV, a Windows VM, or an SSH tunnel. The native workflow runs
the same C++ tests with the original Windows critical-section implementation.
"""

import importlib.util
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


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
        spec = importlib.util.spec_from_file_location(
            "observer_receiver", root / "tools/observer/receiver.py")
        receiver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(receiver)
        expected_ids = [1, 2, 4294967295]
        expected_turns = [0, -2147483648, 2147483647]
        for index, line in enumerate(lines):
            record = receiver.parse_snapshot(line)
            session = record["game_session"]
            world = session["world_instance"]
            state = world["state"]
            if session["id"] != "abc012" or world["id"] != "89abcdef-00000001":
                raise AssertionError("C++ output has incorrect session/world identity")
            if state["snapshot_id"] != expected_ids[index]:
                raise AssertionError("C++ output has incorrect snapshot ID")
            if state["game_turn"] != expected_turns[index]:
                raise AssertionError("C++ output has incorrect signed game turn")
            player = state["players"][0]
            if player["total_population"] != 3 or player["cities"][0]["population"] != 3:
                raise AssertionError("C++ output lost copied city/population values")
        print("PASS: consumer parsed all actual C++ v2 records and numeric edges")


if __name__ == "__main__":
    main()
