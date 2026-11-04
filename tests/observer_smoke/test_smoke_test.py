"""Synthetic producer tests only: no Civ4, Windows VM, or real SSH access."""

import contextlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock


TOOLS = Path(__file__).resolve().parents[2] / "tools" / "observer"
sys.path.insert(0, str(TOOLS))
import smoke_test


def snapshot(identifier=1, session="abc123", turn=42):
    return {"protocol": "advciv-observer", "version": 1, "type": "snapshot",
            "session_id": session, "snapshot_id": identifier,
            "boundary": "post_update", "game_turn": turn}


def frame(identifier=1, session="abc123", turn=42):
    return (json.dumps(snapshot(identifier, session, turn)) + "\n").encode("ascii")


def action(**evidence):
    evidence = dict(completed=True, source="synthetic independent checkpoint", **evidence)
    code = ("import json,os; data=json.loads(" + repr(json.dumps(evidence)) + "); "
            "data['checkpoint']=os.environ['OBSERVER_SMOKE_CHECKPOINT']; print(json.dumps(data))")
    return [sys.executable, "-c", code]


def stage(name="initial", kind="observe", **extra):
    item = dict(name=name, kind=kind, timeout=0.4,
                expected_turn=42, reference_source="synthetic reference independent of wire")
    item.update(extra)
    return item


def statuses(result):
    return {item["name"]: item["status"] for item in result["checks"]}


class Producer:
    """Send fixture bytes through actual TCP and wait for receiver observations."""

    def __init__(self):
        self.client = None

    def connect(self, capture):
        events = [json.loads(line) for line in (capture.root / "events.ndjson").read_text().splitlines()]
        ready = next(item for item in events if item["event"] == "listener_ready")
        self.client = socket.create_connection(("127.0.0.1", ready["port"]), timeout=1)

    def wait(self, capture, predicate):
        deadline = time.monotonic() + 1
        with capture.changed:
            while not predicate():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AssertionError("synthetic receiver observation timed out")
                capture.changed.wait(remaining)

    def send(self, capture, data, expected_count=None, expected_errors=None):
        self.client.sendall(data)
        if expected_count is not None:
            self.wait(capture, lambda: capture.total >= expected_count)
        if expected_errors is not None:
            self.wait(capture, lambda: capture.protocol_errors >= expected_errors)

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None


class SmokeRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.producer = Producer()

    def tearDown(self):
        self.producer.disconnect()
        self.temporary.cleanup()

    def args(self, **values):
        defaults = dict(output_dir=str(self.root / "result"), port=0,
                        idle_timeout=1, ssh_host=None, remote_port=37631,
                        allow_actions=True, interactive=False)
        defaults.update(values)
        return SimpleNamespace(**defaults)

    def run_plan(self, stages, hook=None, **args):
        plan = smoke_test.validate_plan({"stages": stages})
        result = smoke_test.run_capture(self.args(**args), plan, scope="simulated", stage_hook=hook)
        self.assertEqual(result["scope"], "simulated")
        persisted = json.loads((self.root / "result" / "result.json").read_text())
        self.assertEqual(persisted, result)
        self.assertTrue(all(item["status"] in ("passed", "failed", "not_run") for item in result["checks"]))
        return result

    def test_real_loopback_complete_checkpoint_sequence_and_typed_objects(self):
        stages = [stage(), stage("advance", "advance", min_snapshots=2, expected_turn=44),
                  stage("reload", "reload", action=action(reload_completed=True)),
                  stage("shutdown", "shutdown", action=action(process_exited=True))]

        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                # Non-one first ID and fragmented JSON are valid.
                data = frame(3)
                self.producer.send(capture, data[:19])
                self.producer.send(capture, data[19:], expected_count=1)
            elif item["kind"] == "advance":
                self.producer.send(capture, frame(7, turn=43) + frame(9, turn=44), expected_count=3)
            elif item["kind"] == "reload":
                self.producer.disconnect()
                self.producer.connect(capture)
                self.producer.send(capture, frame(4, "def456", 42), expected_count=4)
            else:
                self.producer.disconnect()

        result = self.run_plan(stages, hook)
        self.assertEqual(result["exit_code"], 0, result)
        self.assertEqual(result["summary"]["failed"], 0)
        self.assertEqual(result["summary"]["not_run"], 0)
        self.assertEqual(result["accepted_snapshots"], 4)
        self.assertEqual(result["connections"], 2)
        checks = statuses(result)
        for name in ("initial.expected_turn", "advance.turn_advance", "advance.same_session",
                     "reload.session_change", "reload.expected_turn", "shutdown.peer_eof",
                     "shutdown.process_exit", "receiver_shutdown", "snapshot_order"):
            self.assertEqual(checks[name], "passed")
        objects = [json.loads(line) for line in (self.root / "result" / "snapshots.ndjson").read_text().splitlines()]
        self.assertEqual(objects, [snapshot(3), snapshot(7, turn=43), snapshot(9, turn=44), snapshot(4, "def456", 42)])
        for item in objects:
            for field in ("version", "snapshot_id", "game_turn"):
                self.assertIs(type(item[field]), int)
            self.assertIs(type(item["session_id"]), str)
        self.assertEqual((self.root / "result" / "wire-0001.bin").read_bytes(),
                         frame(3) + frame(7, turn=43) + frame(9, turn=44))

    def test_quoted_integer_is_rejected_and_retained_as_wire_evidence(self):
        bad = snapshot()
        bad["game_turn"] = "42"
        wire = (json.dumps(bad) + "\n").encode()

        def hook(item, capture, checkpoint):
            self.producer.connect(capture)
            self.producer.send(capture, wire, expected_errors=1)
            self.producer.disconnect()
            self.producer.connect(capture)
            self.producer.send(capture, frame(2), expected_count=1)

        result = self.run_plan([stage()], hook)
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(statuses(result)["protocol_validation"], "failed")
        self.assertEqual(result["accepted_snapshots"], 1)
        self.assertEqual((self.root / "result" / "wire-0001.bin").read_bytes(), wire)
        self.assertIn("signed 32-bit", (self.root / "result" / "events.ndjson").read_text())

    def test_duplicate_snapshot_id_fails_order_across_reconnections(self):
        def hook(item, capture, checkpoint):
            self.producer.connect(capture)
            self.producer.send(capture, frame(5), expected_count=1)
            self.producer.disconnect()
            self.producer.connect(capture)
            self.producer.send(capture, frame(5), expected_errors=1)
            self.producer.disconnect()
            self.producer.connect(capture)
            self.producer.send(capture, frame(8), expected_count=2)

        result = self.run_plan([stage(min_snapshots=2)], hook)
        self.assertEqual(statuses(result)["snapshot_order"], "failed")
        self.assertEqual(result["accepted_snapshots"], 2)
        self.assertEqual(result["connections"], 3)
        self.assertEqual(result["exit_code"], 1)

    def test_one_record_in_each_session_does_not_establish_increasing_ids(self):
        def hook(item, capture, checkpoint):
            self.producer.connect(capture)
            self.producer.send(capture, frame(1, "abc123") + frame(1, "def456"), expected_count=2)

        result = self.run_plan([stage(min_snapshots=2)], hook)
        self.assertEqual(statuses(result)["protocol_validation"], "passed")
        self.assertEqual(statuses(result)["snapshot_order"], "not_run")

    def test_no_traffic_fails_collection_and_cannot_claim_structural_success(self):
        result = self.run_plan([stage(timeout=0.1)])
        checks = statuses(result)
        self.assertEqual(checks["initial.collection"], "failed")
        self.assertEqual(checks["initial.python_types"], "not_run")
        self.assertEqual(checks["protocol_validation"], "not_run")
        self.assertEqual(checks["snapshot_order"], "not_run")
        self.assertEqual(result["exit_code"], 1)

    def test_reference_mismatch_is_failure(self):
        def hook(item, capture, checkpoint):
            self.producer.connect(capture)
            self.producer.send(capture, frame(turn=41), expected_count=1)

        result = self.run_plan([stage(timeout=0.1)], hook)
        self.assertEqual(statuses(result)["initial.collection"], "passed")
        self.assertEqual(statuses(result)["initial.expected_turn"], "failed")

    def test_missing_external_reload_evidence_is_incomplete_even_after_session_change(self):
        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                self.producer.send(capture, frame(), expected_count=1)
            else:
                self.producer.send(capture, frame(1, "def456"), expected_count=2)

        result = self.run_plan([stage(), stage("reload", "reload")], hook)
        self.assertEqual(statuses(result)["reload.reload"], "not_run")
        self.assertNotIn("reload.session_change", statuses(result))
        self.assertEqual(result["exit_code"], 2)

    def test_reported_reload_without_changed_session_fails(self):
        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                self.producer.send(capture, frame(), expected_count=1)
            else:
                self.producer.send(capture, frame(2), expected_count=2)

        result = self.run_plan([stage(), stage("reload", "reload", timeout=0.2,
                                              action=action(reload_completed=True))], hook)
        self.assertEqual(statuses(result)["reload.session_change"], "failed")
        self.assertEqual(result["exit_code"], 1)

    def test_regressing_turn_fails_advance(self):
        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                self.producer.send(capture, frame(), expected_count=1)
            else:
                self.producer.send(capture, frame(2, turn=40) + frame(3, turn=43), expected_count=3)

        result = self.run_plan([stage(), stage("advance", "advance", expected_turn=43, min_snapshots=2)], hook)
        self.assertEqual(statuses(result)["advance.expected_turn"], "passed")
        self.assertEqual(statuses(result)["advance.turn_advance"], "failed")
        self.assertEqual(result["exit_code"], 1)

    def test_overflowed_checkpoint_window_cannot_pass_full_advance_continuity(self):
        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                self.producer.send(capture, frame(), expected_count=1)
            else:
                data = b"".join(frame(index + 1, turn=42 + index) for index in range(1, 514))
                self.producer.send(capture, data, expected_count=514)

        result = self.run_plan([stage(), stage("advance", "advance", timeout=1,
                                              min_snapshots=512, expected_turn=555)], hook)
        self.assertEqual(result["accepted_snapshots"], 514)
        self.assertEqual(statuses(result)["advance.evidence_window"], "not_run")
        self.assertEqual(statuses(result)["advance.turn_advance"], "not_run")
        self.assertEqual(statuses(result)["advance.same_session"], "not_run")

    def test_eof_before_shutdown_checkpoint_is_not_reused_as_shutdown_evidence(self):
        def hook(item, capture, checkpoint):
            if item["kind"] == "observe":
                self.producer.connect(capture)
                self.producer.send(capture, frame(), expected_count=1)
                self.producer.disconnect()
                self.producer.wait(capture, lambda: capture.active_connection is None)

        result = self.run_plan([stage(), stage("shutdown", "shutdown", timeout=0.1,
                                              action=action(process_exited=True))], hook)
        self.assertEqual(statuses(result)["shutdown.process_exit"], "passed")
        self.assertEqual(statuses(result)["shutdown.peer_eof"], "not_run")
        self.assertEqual(result["exit_code"], 2)

    def test_actions_need_explicit_opt_in(self):
        marker = self.root / "action-ran"
        command = [sys.executable, "-c", "from pathlib import Path; Path(" + repr(str(marker)) + ").touch()"]
        result = self.run_plan([stage(action=command)], allow_actions=False)
        self.assertEqual(statuses(result)["initial.action"], "not_run")
        self.assertFalse(marker.exists())
        self.assertEqual(result["exit_code"], 2)

    def test_executed_action_failure_differs_from_unavailable_action(self):
        cases = [([sys.executable, "-c", "raise SystemExit(7)"], "failed"),
                 ([sys.executable, "-c", "import time; time.sleep(2)"], "failed"),
                 ([sys.executable, "-c", "print('invalid evidence JSON')"], "failed"),
                 ([str(self.root / "missing-executable")], "not_run")]
        for index, (command, expected_status) in enumerate(cases):
            with self.subTest(command=command):
                plan = {"stages": [stage(timeout=0.1, action=command)]}
                result = smoke_test.run_capture(self.args(output_dir=str(self.root / str(index))), plan,
                                                scope="simulated")
                self.assertEqual(statuses(result)["initial.action"], expected_status)
                self.assertEqual(result["exit_code"], 1 if expected_status == "failed" else 2)

    def test_action_evidence_must_have_fresh_checkpoint_and_integer_reference(self):
        capture_root = self.root / "evidence"
        capture_root.mkdir()
        capture = smoke_test.Capture(capture_root)
        try:
            for payload, reason in (({"completed": True, "source": "test", "checkpoint": "stale"}, "echo"),
                                    ({"completed": True, "source": "test", "checkpoint": "token", "expected_turn": "42"}, "integer")):
                command = [sys.executable, "-c", "print(" + repr(json.dumps(payload)) + ")"]
                evidence, error = smoke_test.get_evidence(dict(action=command), self.args(), capture,
                                                         "token", time.monotonic() + 1)
                self.assertEqual(evidence, {})
                self.assertEqual(error[0], "failed")
                self.assertIn(reason, error[1])
                for output in capture_root.glob("token.*"):
                    output.unlink()
        finally:
            capture.close()

    def test_listener_bind_failure_is_not_reported_as_runtime_pass(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            stages = [stage(), stage("advance", "advance"), stage("reload", "reload"),
                      stage("shutdown", "shutdown")]
            result = self.run_plan(stages, port=occupied.getsockname()[1])
        self.assertEqual(statuses(result)["runner_setup"], "not_run")
        self.assertEqual(statuses(result)["protocol_validation"], "not_run")
        for item in stages:
            self.assertEqual(statuses(result)[item["name"] + ".execution"], "not_run")
        self.assertEqual(result["exit_code"], 2)

    def test_output_directory_is_never_overwritten(self):
        output = self.root / "result"
        output.mkdir()
        prior = output / "prior.json"
        prior.write_text("keep prior evidence\n")
        with self.assertRaises(FileExistsError):
            smoke_test.run_capture(self.args(), {"stages": [stage()]}, scope="simulated")
        self.assertEqual(prior.read_text(), "keep prior evidence\n")
        self.assertEqual(list(output.iterdir()), [prior])

    def test_ssh_remote_forward_argv_and_cleanup_without_contacting_a_host(self):
        process = mock.Mock(pid=1234, returncode=0)
        process.poll.return_value = None
        process.wait.return_value = 0

        def hook(item, capture, checkpoint):
            self.producer.connect(capture)
            self.producer.send(capture, frame() + frame(2), expected_count=2)

        with mock.patch.object(smoke_test.subprocess, "Popen", return_value=process) as popen:
            result = self.run_plan([stage(min_snapshots=2)], hook,
                                   ssh_host="runtime-test-alias", remote_port=40000)
        argv = popen.call_args.args[0]
        self.assertEqual(argv[:2], ["ssh", "-NT"])
        self.assertIn("BatchMode=yes", argv)
        self.assertIn("ExitOnForwardFailure=yes", argv)
        self.assertEqual(argv[-1], "runtime-test-alias")
        forward = argv[argv.index("-R") + 1]
        self.assertRegex(forward, r"^127\.0\.0\.1:40000:127\.0\.0\.1:[0-9]+$")
        self.assertNotIn("shell", popen.call_args.kwargs)
        process.terminate.assert_called_once()
        self.assertEqual(statuses(result)["ssh_lifetime"], "passed")
        self.assertNotIn("runtime-test-alias", (self.root / "result" / "result.json").read_text())


class PlanAndOptInTests(unittest.TestCase):
    def test_invalid_plans(self):
        bad = [{}, {"stages": []}, {"stages": [stage()], "unknown": True},
               {"stages": [stage(), stage()]}, {"stages": [stage(kind="unknown")]},
               {"stages": [stage(timeout=True)]}, {"stages": [stage(timeout=float("nan"))]},
               {"stages": [stage(min_snapshots=True)]}, {"stages": [stage(min_snapshots=513)]},
               {"stages": [stage(expected_turn="42")]}, {"stages": [stage(reference_source="")]},
               {"stages": [stage(action="shell text")]}, {"stages": [stage(action=[""])]}]
        for plan in bad:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                smoke_test.validate_plan(plan)

    def test_duplicate_keys_and_nonfinite_values_rejected(self):
        for text in ('{"stages":[],"stages":[]}', '{"value":NaN}', '{"value":Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                smoke_test.read_json(text)

    def test_live_opt_in_precedes_any_listener_tunnel_or_plan_read(self):
        with tempfile.TemporaryDirectory() as directory:
            output = str(Path(directory) / "unused")
            with mock.patch.object(smoke_test, "run_capture") as capture, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    smoke_test.main(["--plan", "not-a-real-plan", "--output-dir", output])
                self.assertEqual(raised.exception.code, 2)
                capture.assert_not_called()
            self.assertFalse(Path(output).exists())


if __name__ == "__main__":
    unittest.main()
