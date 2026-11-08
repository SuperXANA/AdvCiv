#!/usr/bin/env python3
"""Opt-in runtime checkpoints around the existing observer Receiver (Python 3.8+).

No game commands are built in. See docs/observer-smoke-test.md for the local
plan, manual evidence and optional explicitly enabled action adapters.
"""

import argparse
from collections import OrderedDict, deque
import datetime
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import uuid

import receiver


KINDS = ("observe", "advance", "reload", "shutdown")


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != {"stages"}:
        raise ValueError("plan must contain only stages")
    stages = plan["stages"]
    if not isinstance(stages, list) or not 1 <= len(stages) <= 32:
        raise ValueError("plan requires 1-32 stages")
    names = set()
    allowed = {"name", "kind", "timeout", "min_snapshots", "expected_turn",
               "reference_source", "action"}
    for stage in stages:
        if not isinstance(stage, dict) or set(stage) - allowed:
            raise ValueError("unknown stage fields")
        name = stage.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or name in names:
            raise ValueError("stage names must be unique nonempty strings (max 80)")
        names.add(name)
        if stage.get("kind") not in KINDS:
            raise ValueError("unsupported stage kind")
        timeout = stage.get("timeout", 60)
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0.1 <= timeout <= 3600:
            raise ValueError("stage timeout must be 0.1-3600 seconds")
        count = stage.get("min_snapshots", 1)
        if type(count) is not int or not 1 <= count <= 512:
            raise ValueError("min_snapshots must be an integer from 1 to 512")
        if "expected_turn" in stage:
            if type(stage["expected_turn"]) is not int or not -0x80000000 <= stage["expected_turn"] <= 0x7fffffff:
                raise ValueError("expected_turn must be a signed 32-bit integer")
            if not isinstance(stage.get("reference_source"), str) or not stage["reference_source"].strip():
                raise ValueError("expected_turn needs an independent reference_source")
        action = stage.get("action")
        if action is not None and (not isinstance(action, list) or not action or
                                   any(not isinstance(x, str) or not x or "\x00" in x for x in action)):
            raise ValueError("action must be a nonempty argv string array")
    return plan


def read_json(text):
    # Refuse duplicate evidence/plan keys rather than silently choosing one.
    return json.loads(text, object_pairs_hook=receiver._unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON: " + value)))


class Capture:
    """Disk journals plus a bounded recent window; callbacks never touch Civ4."""

    def __init__(self, root):
        self.root = root
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.events = (root / "events.ndjson").open("x", encoding="utf-8", buffering=1)
        self.snapshots = (root / "snapshots.ndjson").open("x", encoding="utf-8", buffering=1)
        self.recent = deque(maxlen=512)
        self.eofs = deque(maxlen=512)
        self.total = self.connections = self.protocol_errors = self.order_errors = 0
        self.order_comparisons = 0
        self.last_ids = OrderedDict()
        self.sequence = 0
        self.active_connection = None
        self.last = None
        self.fatal = None

    def event(self, event_kind, **fields):
        with self.changed:
            self.sequence += 1
            item = dict(event=event_kind, event_id=self.sequence, utc=utc_now(), **fields)
            self.events.write(json.dumps(item, separators=(",", ":")) + "\n")
            self.changed.notify_all()
            return item

    def accept(self, snapshot):
        with self.changed:
            self.total += 1
            item = dict(snapshot)  # Actual detached Python values from Receiver.
            session = item["game_session"]["id"]
            state = item["game_session"]["world_instance"]["state"]
            if session in self.last_ids:
                self.order_comparisons += 1
            self.last_ids[session] = state["snapshot_id"]
            self.last_ids.move_to_end(session)
            if len(self.last_ids) > receiver.MAX_SESSIONS:
                self.last_ids.popitem(last=False)
            self.snapshots.write(json.dumps(item, separators=(",", ":")) + "\n")
            event = self.event("snapshot", snapshot_index=self.total,
                               connection_id=self.active_connection, snapshot=item)
            self.recent.append((self.total, event["event_id"], item))
            self.last = item
            self.changed.notify_all()

    def error(self, message):
        with self.changed:
            if message == "idle client disconnected" or message.startswith("client disconnected:"):
                self.event("connection_notice", message=message, connection_id=self.active_connection)
            else:
                self.protocol_errors += 1
                if "snapshot_id did not increase" in message:
                    self.order_errors += 1
                self.event("rejected_frame", message=message, connection_id=self.active_connection)

    def close(self):
        self.events.close()
        self.snapshots.close()


class LoggedSocket:
    """Observe bytes/EOF while the unchanged Receiver does framing and parsing."""

    def __init__(self, connection, capture, identifier, wire):
        self.connection, self.capture, self.identifier, self.wire = connection, capture, identifier, wire

    def settimeout(self, value):
        self.connection.settimeout(value)

    def recv(self, size):
        try:
            chunk = self.connection.recv(size)
        except socket.timeout:
            raise
        except OSError as exc:
            self.capture.event("socket_error", connection_id=self.identifier, message=str(exc))
            raise
        if chunk:
            self.wire.write(chunk)
            self.wire.flush()
        else:
            with self.capture.changed:
                event = self.capture.event("peer_eof", connection_id=self.identifier)
                self.capture.eofs.append(event)
        return chunk


class LoggedReceiver(receiver.Receiver):
    def __init__(self, capture, port, idle_timeout):
        self.capture = capture
        super().__init__(capture.accept, port=port, idle_timeout=idle_timeout, on_error=capture.error)

    def _receive(self, connection):
        with self.capture.changed:
            self.capture.connections += 1
            identifier = self.capture.connections
            self.capture.active_connection = identifier
            self.capture.event("connection_open", connection_id=identifier)
        try:
            with (self.capture.root / ("wire-{:04d}.bin".format(identifier))).open("xb") as wire:
                super()._receive(LoggedSocket(connection, self.capture, identifier, wire))
        finally:
            with self.capture.changed:
                self.capture.event("connection_closed", connection_id=identifier)
                self.capture.active_connection = None


def check(checks, name, status, reason, **evidence):
    checks.append(dict(name=name, status=status, reason=reason, **evidence))


def get_evidence(stage, args, capture, checkpoint, deadline):
    """External actions are local opt-in adapters, not observer commands."""
    if stage.get("action"):
        if not args.allow_actions:
            return {}, ("not_run", "action disabled; add --allow-actions only for your reviewed local adapter")
        stdout_path = capture.root / (checkpoint + ".stdout")
        stderr_path = capture.root / (checkpoint + ".stderr")
        env = os.environ.copy()
        env["OBSERVER_SMOKE_CHECKPOINT"] = checkpoint
        # Keep command/host/path/arguments out of result.json. Local adapter logs
        # can contain private runtime details; do not commit the results folder.
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            try:
                completed = subprocess.run(stage["action"], shell=False, env=env,
                                           stdout=stdout, stderr=stderr,
                                           timeout=max(0.1, deadline - time.monotonic()))
            except (OSError, subprocess.TimeoutExpired) as exc:
                capture.event("action_error", checkpoint=checkpoint, message=str(exc))
                return {}, ("failed" if isinstance(exc, subprocess.TimeoutExpired) else "not_run",
                            "action could not finish; see local action logs")
        if completed.returncode:
            return {}, ("failed", "action returned nonzero; see local action logs")
        if stdout_path.stat().st_size > 65536:
            return {}, ("failed", "action evidence exceeds 64 KiB")
        try:
            evidence = read_json(stdout_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            return {}, ("failed", "invalid action evidence JSON: " + str(exc))
        if not isinstance(evidence, dict) or evidence.get("checkpoint") != checkpoint:
            return {}, ("failed", "action evidence must echo OBSERVER_SMOKE_CHECKPOINT")
    elif args.interactive:
        print("Checkpoint {} ({}) is collecting. Perform the action, then enter evidence JSON:".format(
            stage["name"], stage["kind"]), flush=True)
        # Timed input keeps an unattended interactive run bounded on Linux.
        import select
        ready, _, _ = select.select([sys.stdin], [], [], max(0, deadline - time.monotonic()))
        if not ready:
            return {}, ("not_run", "operator evidence deadline expired")
        line = sys.stdin.readline(65537)
        if not line:
            return {}, ("not_run", "operator input closed without checkpoint evidence")
        if len(line) > 65536:
            return {}, ("failed", "operator evidence exceeds 64 KiB")
        try:
            evidence = read_json(line)
        except ValueError as exc:
            return {}, ("failed", "invalid operator evidence JSON: " + str(exc))
    else:
        return {}, None
    if not isinstance(evidence, dict) or evidence.get("completed") is not True:
        return {}, ("failed", "evidence must be an object with completed=true")
    if not isinstance(evidence.get("source"), str) or not evidence["source"].strip():
        return {}, ("failed", "evidence needs an independent source description")
    if "expected_turn" in evidence and (type(evidence["expected_turn"]) is not int or
                                       not -0x80000000 <= evidence["expected_turn"] <= 0x7fffffff):
        return {}, ("failed", "evidence expected_turn must be a signed 32-bit integer")
    if "expected_turn" in stage and "expected_turn" in evidence and stage["expected_turn"] != evidence["expected_turn"]:
        return {}, ("failed", "evidence expected_turn disagrees with the planned reference")
    # Preserve only the small supported evidence object, never arbitrary output.
    evidence = {key: evidence[key] for key in ("completed", "source", "expected_turn", "reload_completed", "process_exited")
                if key in evidence}
    capture.event("external_evidence", checkpoint=checkpoint, evidence=evidence)
    return evidence, None


def run_stage(stage, args, capture, tunnel, checks, stage_hook=None):
    name, kind = stage["name"], stage["kind"]
    checkpoint = uuid.uuid4().hex
    deadline = time.monotonic() + stage.get("timeout", 60)
    with capture.changed:
        cursor, baseline, connection = capture.total, capture.last, capture.active_connection
        start = capture.event("checkpoint_start", checkpoint=checkpoint, name=name, kind=kind)
    if stage_hook is not None:  # Test-only synthetic producer; CLI never sets it.
        stage_hook(stage, capture, checkpoint)
    evidence, error = get_evidence(stage, args, capture, checkpoint, deadline)
    if error:
        check(checks, name + ".action", error[0], error[1], checkpoint=checkpoint)
        return
    expected = stage.get("expected_turn", evidence.get("expected_turn"))
    source = stage.get("reference_source", evidence.get("source"))
    if kind in ("advance", "reload") and baseline is None:
        check(checks, name + ".baseline", "not_run", "no earlier snapshot to compare", checkpoint=checkpoint)
        return
    if kind == "reload" and (evidence.get("reload_completed") is not True or expected is None):
        check(checks, name + ".reload", "not_run", "requires completed reload evidence and independent saved game_turn", checkpoint=checkpoint)
        return
    if kind == "shutdown" and evidence.get("process_exited") is not True:
        check(checks, name + ".process_exit", "not_run", "requires independent Civ4 process exit evidence", checkpoint=checkpoint)
        return
    while True:
        with capture.changed:
            samples = [(index, item) for index, _, item in capture.recent if index > cursor]
            if kind in ("advance", "reload"):
                samples = [(index, item) for index, item in samples
                           if (item["game_session"]["id"] == baseline["game_session"]["id"]) == (kind == "advance")]
            matched = [(index, item) for index, item in samples
                       if expected is None or item["game_session"]["world_instance"]["state"]["game_turn"] == expected]
            eofs = [event for event in capture.eofs if event["event_id"] > start["event_id"]
                    and event["connection_id"] == connection]
            ready = bool(eofs) if kind == "shutdown" else (len(samples) >= stage.get("min_snapshots", 1) and bool(matched))
            if kind == "advance":
                ready = ready and any(item["game_session"]["world_instance"]["state"]["game_turn"] >
                                      baseline["game_session"]["world_instance"]["state"]["game_turn"]
                                      for _, item in samples)
            if ready or capture.fatal or (tunnel is not None and tunnel.poll() is not None) or time.monotonic() >= deadline:
                break
            capture.changed.wait(min(0.1, max(0, deadline - time.monotonic())))
    common = dict(checkpoint=checkpoint)
    if kind == "shutdown":
        check(checks, name + ".process_exit", "passed", "external evidence reports Civ4 exited", source=evidence["source"], **common)
        check(checks, name + ".peer_eof", "passed" if eofs else ("not_run" if connection is None else "failed"),
              "EOF observed on checkpoint connection" if eofs else "no EOF observed on a connection active at checkpoint start",
              connection_id=connection, **common)
        return
    overflow = capture.total - cursor > capture.recent.maxlen
    if overflow:
        check(checks, name + ".evidence_window", "not_run",
              "more than 512 snapshots arrived during checkpoint; inspect disk journals or shorten the action",
              **common)
    check(checks, name + ".collection", "passed" if len(samples) >= stage.get("min_snapshots", 1) else "failed",
          "snapshots received after checkpoint" if samples else "no qualifying snapshots before deadline; verify opt-in, gameplay and forwarding",
          qualifying_snapshots=len(samples), total_new_snapshots=capture.total - cursor, **common)
    if samples:
        check(checks, name + ".python_types", "passed", "existing Receiver returned exact-schema dictionaries with real integers and text",
              python_types={key: type(value).__name__ for key, value in samples[-1][1].items()}, **common)
    else:
        check(checks, name + ".python_types", "not_run", "no accepted object to inspect", **common)
    if expected is None:
        check(checks, name + ".expected_turn", "not_run", "no independent game_turn reference supplied", **common)
    else:
        check(checks, name + ".expected_turn", "passed" if matched else ("failed" if samples else "not_run"),
              "matched independently supplied game_turn" if matched else "expected turn was not observed",
              expected_turn=expected, source=source,
              observed_turns=[item["game_session"]["world_instance"]["state"]["game_turn"]
                              for _, item in samples],
              matching_snapshot_indices=[index for index, _ in matched], **common)
    if kind == "advance":
        turns = [baseline["game_session"]["world_instance"]["state"]["game_turn"]]
        turns += [item["game_session"]["world_instance"]["state"]["game_turn"] for _, item in samples]
        progressed = any(turn > turns[0] for turn in turns[1:]) and all(a <= b for a, b in zip(turns, turns[1:]))
        check(checks, name + ".turn_advance", "not_run" if overflow else ("passed" if progressed else ("failed" if samples else "not_run")),
              "nondecreasing turns with advancement in the baseline session" if progressed else "no qualifying uninterrupted turn advancement",
              baseline=baseline, observed_turns=turns[1:], **common)
        with capture.lock:
            changed_session = any(item["game_session"]["id"] != baseline["game_session"]["id"]
                                  for index, _, item in capture.recent if index > cursor)
        check(checks, name + ".same_session", "failed" if changed_session else ("not_run" if overflow else ("passed" if samples else "not_run")),
              "session changed during advance" if changed_session else "advance session continuity", **common)
    if kind == "reload":
        check(checks, name + ".session_change", "passed" if samples else "failed",
              "new session after externally reported reload" if samples else "new reload session was not observed",
              previous_session=baseline["game_session"]["id"],
              observed_sessions=sorted({item["game_session"]["id"] for _, item in samples}),
              source=evidence["source"], **common)


def run_capture(args, plan, scope="live_capture", stage_hook=None):
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=False)  # Never overwrite an earlier run.
    capture = Capture(root)
    checks, server, thread, tunnel, tunnel_log = [], None, None, None, None
    entered_stages = set()
    result = dict(schema="advciv-observer-smoke/v1", scope=scope, started_utc=utc_now(),
                  checks=checks, runtime_claim="checkpoint evidence only; synthetic traffic is not Civ4 validation",
                  boundaries=["no built-in gameplay control or independent memory reader",
                              "sender refused-connect errors and worker join are not observable over this protocol",
                              "EOF alone does not prove clean game teardown"],
                  unobservable_checks=[dict(name="sender_connection_failures", status="not_run",
                                            reason="requires independent cdb/Win32 diagnostics; no sender error messages in v1"),
                                       dict(name="dll_worker_shutdown", status="not_run",
                                            reason="EOF and process exit do not inspect worker join or game teardown")],
                  artifacts={"snapshots": "snapshots.ndjson", "events": "events.ndjson", "wire": "wire-*.bin"})
    try:
        server = LoggedReceiver(capture, args.port, args.idle_timeout)
        capture.event("listener_ready", host=server.address[0], port=server.address[1])
        check(checks, "listener_bind", "passed", "existing Receiver bound IPv4 loopback", port=server.address[1])

        def serve():
            try:
                server.serve()
            except BaseException as exc:
                with capture.changed:
                    capture.fatal = str(exc)
                    capture.event("receiver_error", message=str(exc))

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        if args.ssh_host:
            tunnel_log = (root / "ssh.stderr").open("xb")
            tunnel = subprocess.Popen(["ssh", "-NT", "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes",
                                       "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=15",
                                       "-o", "ServerAliveCountMax=2", "-R",
                                       "127.0.0.1:{}:127.0.0.1:{}".format(args.remote_port, server.address[1]),
                                       args.ssh_host], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                      stderr=tunnel_log)
            capture.event("ssh_started", process_id=tunnel.pid, remote_port=args.remote_port)
        for stage in plan["stages"]:
            entered_stages.add(stage["name"])
            run_stage(stage, args, capture, tunnel, checks, stage_hook)
        if tunnel is not None:
            check(checks, "ssh_lifetime", "passed" if tunnel.poll() is None else "failed",
                  "SSH remained running; this alone does not establish forwarding or game observation" if tunnel.poll() is None else "SSH exited; inspect ssh.stderr",
                  return_code=tunnel.poll())
    except (OSError, ValueError) as exc:
        check(checks, "runner_setup", "not_run", str(exc))
        capture.event("setup_error", message=str(exc))
    except KeyboardInterrupt:
        check(checks, "interrupted", "not_run", "operator interrupted the run")
    finally:
        if server is not None:
            started = time.monotonic()
            server.request_stop()
            if thread is not None:
                thread.join(2)
            else:
                server.close()
            alive = thread is not None and thread.is_alive()
            check(checks, "receiver_shutdown", "failed" if alive else "passed",
                  "receiver stopped within 2 seconds" if not alive else "receiver thread did not stop within 2 seconds",
                  elapsed_seconds=time.monotonic() - started)
        if tunnel is not None:
            tunnel.terminate()
            try:
                tunnel.wait(timeout=3)
            except subprocess.TimeoutExpired:
                tunnel.kill()
                tunnel.wait(timeout=3)
            capture.event("ssh_stopped", return_code=tunnel.returncode)
        if tunnel_log is not None:
            tunnel_log.close()
        if capture.fatal:
            check(checks, "receiver_health", "failed", capture.fatal)
        check(checks, "protocol_validation", "failed" if capture.protocol_errors else ("passed" if capture.total else "not_run"),
              "existing parser enforces framing, exact fields, duplicate keys and numeric/text types",
              accepted_snapshots=capture.total, rejected_frames=capture.protocol_errors)
        check(checks, "snapshot_order", "failed" if capture.order_errors else ("passed" if capture.order_comparisons else "not_run"),
              "IDs increase per session; gaps allowed; Receiver retains 64 sessions",
              ordering_errors=capture.order_errors, within_session_comparisons=capture.order_comparisons)
        for stage in plan["stages"]:
            if stage["name"] not in entered_stages:
                check(checks, stage["name"] + ".execution", "not_run", "runner could not enter this checkpoint")
        kinds = {stage["kind"] for stage in plan["stages"]}
        for kind in ("advance", "reload", "shutdown"):
            if kind not in kinds:
                check(checks, kind, "not_run", "checkpoint omitted from this plan")
        result.update(completed_utc=utc_now(), accepted_snapshots=capture.total,
                      connections=capture.connections,
                      summary={status: sum(item["status"] == status for item in checks)
                               for status in ("passed", "failed", "not_run")})
        result["exit_code"] = 1 if result["summary"]["failed"] else (2 if result["summary"]["not_run"] else 0)
        capture.event("run_complete", summary=result["summary"], exit_code=result["exit_code"])
        # A stuck receiver must not write into closed streams. This is an explicit
        # failure; its daemon ends when the command exits.
        if thread is None or not thread.is_alive():
            capture.close()
        (root / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable-live", action="store_true", help="explicitly permit live loopback listening and optional SSH")
    parser.add_argument("--output-dir", required=True, help="new local evidence directory (must not exist)")
    parser.add_argument("--plan", required=True, help="local JSON checkpoint plan")
    parser.add_argument("--port", type=int, default=37631)
    parser.add_argument("--remote-port", type=int, default=37631)
    parser.add_argument("--idle-timeout", type=float, default=300)
    parser.add_argument("--ssh-host", help="your SSH config alias for the Windows runtime VM")
    parser.add_argument("--interactive", action="store_true", help="collect timed operator JSON evidence on Linux stdin")
    parser.add_argument("--allow-actions", action="store_true", help="allow reviewed local argv adapters in the plan")
    args = parser.parse_args(argv)
    if not args.enable_live:
        parser.error("--enable-live is required; no listener, tunnel or action was started")
    if not 1 <= args.port <= 65535 or not 1 <= args.remote_port <= 65535:
        parser.error("ports must be between 1 and 65535")
    if not math.isfinite(args.idle_timeout) or not 0.1 <= args.idle_timeout <= 300:
        parser.error("idle timeout must be 0.1-300 seconds")
    if args.ssh_host and (args.ssh_host.startswith("-") or any(c.isspace() for c in args.ssh_host)):
        parser.error("--ssh-host must be one SSH destination or config alias")
    try:
        plan = validate_plan(read_json(Path(args.plan).read_text(encoding="utf-8")))
        result = run_capture(args, plan)
    except (OSError, ValueError) as exc:
        print("smoke-test: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(dict(result=str(Path(args.output_dir) / "result.json"), **result["summary"])))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
