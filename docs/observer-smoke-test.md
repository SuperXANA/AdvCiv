# ObserverMCP runtime smoke test

The smoke runner collects evidence from the hierarchical version-2 observer. It
imports `tools/observer/receiver.py`; it does not replace the receiver, create
a second protocol, send commands to the DLL, or deploy a DLL. Its purpose is to
answer separate questions: did valid typed snapshots arrive, did their IDs
increase, did their turns match independent Civ4 readings, and did the expected
session and connection transitions occur?

The successful native validation remains recorded in
[observer-validation.md](observer-validation.md). The runner's simulated tests
exercise the Linux scripts and real loopback sockets. They do not establish
that Civilization IV, the home Windows VM, or the SSH path was exercised.

## Requirements and opt-in

- Linux controller with Python 3.8 or newer and OpenSSH. The Python runner uses only the
  standard library.
- An observer-enabled DLL installed in the intended mod by the operator. Both
  the compile gate and `CV_OBSERVER_ENABLE=1` in the actual game process are
  required. The committed default stays disabled.
- The existing Windows runtime VM, SSH account configuration, and interactive
  game desktop or AutoIT arrangement. GitHub access supplies none of these.
- A fresh local output directory and a local test plan. Keep host aliases,
  installation paths, automation commands, and results on the controller;
  do not commit credentials or machine-specific configuration.

The runner requires `--enable-live` before opening a listener. Optional action
commands require the additional `--allow-actions` flag. The Windows launcher
requires its own `-EnableObservation` switch.

Plans contain 1–32 uniquely named stages. Each stage timeout is 0.1–3600
seconds; `min_snapshots` is 1–512. An expected turn must be a JSON integer in
the signed 32-bit range, with a nonempty `reference_source` in the plan.

## Start the controller and tunnel

Prepare a local plan using the example below, then run from the repository root:

For a plan whose turns are supplied at each interactive checkpoint, first copy
`tools/observer/smoke-plan.example.json` to `tools/observer/runtime.local.json`.

```sh
python3 tools/observer/smoke_test.py \
  --enable-live \
  --plan tools/observer/runtime.local.json \
  --output-dir tools/observer/results/manual-001 \
  --ssh-host WINDOWS_RUNTIME_ALIAS \
  --interactive
```

`WINDOWS_RUNTIME_ALIAS` is an alias configured in the operator's own SSH
configuration. Use normal key/agent authentication and host-key verification.
The runner initiates a remote forward in this direction:

```sh
ssh -NT -o BatchMode=yes -o ExitOnForwardFailure=yes \
  -R 127.0.0.1:37631:127.0.0.1:37631 WINDOWS_RUNTIME_ALIAS
```

The Windows observer connects to Windows `127.0.0.1:37631`; SSH carries that
connection to Linux `127.0.0.1:37631`. The SSH server must permit remote
forwarding. `--remote-port` changes the Windows endpoint, while `--port`
changes the Linux listener. Set the launcher's `-Port` to the remote port.
Both endpoints stay on loopback.

An SSH process remaining alive establishes only startup evidence. Valid
snapshots crossing it establish received traffic. The runner records SSH
startup/exit errors and cleans up the SSH process it created. It does not
modify SSH server settings or authentication configuration. If a suitable
tunnel already exists, omit `--ssh-host`; manage that tunnel separately.
Do not run another receiver on the selected Linux port at the same time.

## Launch the observed process on Windows

Run the launcher in the Windows runtime VM's existing game desktop/session:

```powershell
.\tools\observer\start_observed_game.ps1 `
  -EnableObservation `
  -ExecutablePath 'C:\YOUR\INSTALL\Civ4BeyondSword.exe' `
  -WorkingDirectory 'C:\YOUR\INSTALL' `
  -ArgumentLine 'mod="YOUR MOD NAME"' `
  -Port 37631 `
  -ResultPath 'C:\YOUR\LOCAL\RESULTS\observer-launch.json'
```

Replace the paths and argument string locally. `-ArgumentLine` is the complete
Windows argument string for the chosen executable, including its required
quoting. The script can instead launch an AutoIT executable which starts Civ4;
its child must inherit the observer environment. Launch evidence for AutoIT
identifies that process, so confirm the actual Civ4 process independently.
Launching from SSH alone does not establish access to the interactive desktop.

The launcher sets observer variables only in the child environment. Optional
`-Queue`, `-RetryMilliseconds`, and `-TimeoutMilliseconds` configure the
existing supported settings. It does not alter a machine-wide environment,
install files, copy a DLL, or terminate a running game. Its JSON result proves
the requested process was launched; it does not prove the observer DLL loaded.

## Manual checkpoint plan

Save this example locally as `tools/observer/runtime.local.json`. Adjust the
timeouts to the VM and choose expected turn values from the intended scenario.
The examples use saved turn 42 and advanced turn 45; these are placeholders,
not values inferred from observer output.

```json
{
  "stages": [
    {
      "name": "initial",
      "kind": "observe",
      "timeout": 180,
      "min_snapshots": 1,
      "expected_turn": 42,
      "reference_source": "Independent Civ4 getGameTurn reading after loading the test save"
    },
    {
      "name": "advance",
      "kind": "advance",
      "timeout": 180,
      "min_snapshots": 1,
      "expected_turn": 45,
      "reference_source": "Independent Civ4 getGameTurn reading after AutoIT advances turns"
    },
    {
      "name": "reload",
      "kind": "reload",
      "timeout": 180,
      "min_snapshots": 1,
      "expected_turn": 42,
      "reference_source": "The saved test game was independently recorded at getGameTurn 42"
    },
    {
      "name": "exit",
      "kind": "shutdown",
      "timeout": 90
    }
  ]
}
```

Collection starts before each stage action, so snapshots sent while the
operator or automation performs that action can be checked. In interactive
mode the runner reads one JSON evidence object per stage. Complete the action
first, then enter the evidence requested by the prompt. Input and collection
share the stage timeout; use enough time for both. For example:

```json
{"completed":true,"source":"Operator: independently read CyGame().getGameTurn() as 42","expected_turn":42}
```

Use a Civ4 Python `CyGame().getGameTurn()` reading, cdb inspection of the actual
game value, or another independent game-state reading. Record a source and
checkpoint context that can be reviewed later. The visible calendar year or
an AutoIT click count alone may not equal `getGameTurn()`. Do not copy the
observer's received `world_instance.state.game_turn` into the expectation and call that a comparison.

For a complete manual scenario:

1. Start the runner, then launch Civ4 with the launcher. Load or create the test
   game, independently read its game turn, and save it. Supply initial-stage
   evidence. Use a new game/save made with the selected DLL as appropriate.
2. At the advance stage, advance enough turns for a changed value. Independently
   read the resulting turn and supply its evidence. Pause autoplay at the
   intended checkpoint so the expected value is observable.
3. At the reload stage, reload the earlier saved game. Confirm the operation
   completed and independently check the loaded turn. Include the action flag:

   ```json
   {"completed":true,"source":"Operator: reloaded the saved game and read its turn","reload_completed":true,"expected_turn":42}
   ```

4. At shutdown, exit Civ4 normally and independently confirm the actual game
   process exited. Include the process flag:

   ```json
   {"completed":true,"source":"Operator: Civ4 process exited after normal Exit Game","process_exited":true}
   ```

The reload check requires the external reload evidence, a new session token,
and the expected saved turn. A changed token alone proves only a new observer
session. The shutdown checks keep external process-exit evidence separate from
socket EOF and receiver-thread shutdown. A closed socket alone cannot prove
that Civ4 exited cleanly. The shutdown EOF check follows the connection active
at the start of that checkpoint. With no active connection it is `not_run`;
an idle connection already closed by the receiver cannot supply exit evidence.

## Use existing automation

Each stage can optionally contain an `action` array: the local executable and
its arguments, passed with `shell=False`. This can invoke an existing Linux
wrapper which uses the operator's SSH/AutoIT/cdb setup. The runner does not
provide new game-control logic. Enable configured actions with
`--allow-actions`; review the local plan before running them.

A stage with an `action` uses that adapter instead of interactive input. If
actions are not enabled, its action check is `not_run`. An observe or advance
stage can also run unattended using the independent expected turn already in
the plan; reload and shutdown additionally require the external action evidence.

An action must finish within the stage timeout and write exactly one JSON
evidence object to stdout. Send diagnostics to stderr. The runner passes a
fresh stage token in `OBSERVER_SMOKE_CHECKPOINT`; return it as `checkpoint`
to associate the evidence with this execution. For example, a local wrapper
can return:

```json
{"checkpoint":"TOKEN_FROM_ENVIRONMENT","completed":true,"source":"Local AutoIT/cdb wrapper and independently recorded game turn","expected_turn":45}
```

Reload actions also return `reload_completed:true`; shutdown actions return
`process_exited:true` only after confirming that the Civ4 process exited.
Do not use the launcher's process-start result as game-exit evidence.
Keep authentication material out of argv, plans, stdout and stderr. Use the
existing private SSH configuration. Run artifacts may contain local paths,
diagnostics and game state; review them before sharing.

A disabled or unlaunchable action is `not_run`; an action that starts and then
times out, returns nonzero, or returns invalid evidence is `failed`. An action
timeout stops the local adapter process. Its remote work may still be running;
the local adapter is responsible for remote cancellation and bounded commands.

## Interpret the evidence

| Artifact | Meaning |
| --- | --- |
| `result.json` | Machine-readable check outcomes and summary |
| `events.ndjson` | Stage markers, evidence, connection lifecycle and errors |
| `snapshots.ndjson` | Accepted detached Python dictionaries serialized back to JSON |
| `wire-0001.bin`, `wire-0002.bin`, … | Per-connection bytes received, including malformed or partial frames |
| `ssh.stderr`, when forwarding is requested | Tunnel process errors, separate from game-state checks |
| Per-action `.stdout` and `.stderr` files, when actions are requested | Evidence and diagnostics from the local adapter |

Each check is `passed`, `failed`, or `not_run`. `not_run` means required
evidence or a prerequisite was unavailable; it is not a pass. The exit code is
0 when every requested check passes, 1 when a check fails, and 2 when the run is
incomplete without a failed check. Omitting advance, reload or shutdown marks
that scenario `not_run`, so an observe-only plan intentionally remains
incomplete. Read individual checks, especially when some observations succeed
while independent runtime evidence is missing.

The separate `unobservable_checks` array always labels sender-side connection
failures and DLL worker shutdown as `not_run`. Those limits do not enter the
requested-check exit-code summary. They require independent diagnostics.
The order check needs at least one received pair within the same session;
two single records from different sessions leave that check `not_run`.

The existing receiver validates complete NDJSON frames, the exact version-2
session/world/state/player/city hierarchy, fixed text values, integer/boolean
types, city-chunk invariants, bounded values, duplicate keys, and increasing
snapshot IDs within its bounded session history. Quoted numbers,
booleans in integer fields, malformed JSON and out-of-order IDs are rejected
before they enter the accepted snapshot callback. Accepted snapshots therefore
provide evidence about actual Python values, beyond a successful TCP bridge.

Important limits when interpreting a run:

- An initial snapshot is followed by snapshots only when the captured turn
  changes. A paused game can be silent. Silence is not a heartbeat failure.
- Snapshot-ID gaps and skipped turns are allowed because the sender drops
  queued records under pressure. Do not require a received session to begin
  with ID 1 or each received turn to advance by exactly one.
- The runner sets the existing receiver's idle timeout to 300 seconds by
  default; `--idle-timeout` accepts 0.1–300 seconds. An idle timeout can close
  an otherwise valid paused-game connection. EOF, reconnection, and a new
  observer session are distinct events.
- Connection opens/closes, peer EOF, socket errors and reconnections are
  journaled. The runner does not deliberately break the tunnel or game
  connection. A separate operator-controlled reconnect experiment can use
  these records, but it must not be reported as a built-in fault-injection test.
- Sender-side refused-connect errors cannot be observed through a receiver
  which was absent. They need independent cdb/diagnostic evidence; the runner
  must not infer them from silence.
- A JSON/schema pass covers the received records. It does not establish that
  every turn was delivered or that unobserved game fields were correct.
- Checkpoint comparisons retain at most 512 recent snapshots in memory. A
  longer action that overflows this window is marked incomplete; complete
  records remain in the disk journals for inspection.

Revalidate accepted records with the unchanged receiver if desired:

```sh
python3 tools/observer/receiver.py --validate tools/observer/results/manual-001/snapshots.ndjson
```

## Repeat local checks

```sh
python3 -m unittest discover -s tests/observer_smoke -v
python3 -m unittest discover -s tests/observer -p 'test_receiver.py' -v
```

The smoke suite is kept outside `tests/observer` so adding Python smoke tests
does not trigger the native DLL workflow's existing path filter. The existing
native implementation, standalone tests and successful validation inputs are
preserved. Actual gameplay, save/reload and Windows-to-Linux forwarding remain
unvalidated until this runner is executed against the runtime VM and its
result artifacts are reviewed.
