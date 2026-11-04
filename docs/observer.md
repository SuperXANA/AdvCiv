# ObserverMCP first snapshot prototype

This isolated idea branch combines the complete read-only AdvCiv 1.14 baseline
`5970334b64a875b5cdb370c94fc9a98db4eacda6` with ObserverMCP input
`52bc44bf909a302c00a8a7c3e7f7c54a37c43a99`. The original branch, README and
`CvCriticalSectionMutex.h` are preserved. New integration blocks carry XANA
ObserverMCP date markers. This is a small observation transport; an MCP server
and game-control commands are future, separate work. It is independent of cdb.

To adopt the idea in a combined mod, copy the new observer implementation files
and the unchanged mutex header, then merge the three marked include/hook blocks
into your current `CvGame.cpp`. This branch's `CvGame.cpp` and native DLLs contain
the pinned 1.14 baseline plus this prototype; other independent feature branches
are outside this validation scope.

## Capture boundary and ownership

`CvGame::update()` calls `CvObserver::postUpdate(*this)` after its update loop,
only when `isFinalInitialized()` is true. The first eligible call captures the
owning thread ID; later calls on another thread are ignored. The bridge reads
`game.getGameTurn()` once, on that thread, and formats a detached value. It emits
an initial snapshot, then one whenever the observed turn changes. This labels
the end of an update call, not a guarantee that every player's turn is complete.
Several internal updates may occur before that boundary.

The queue owns fixed-size copies of the serialized messages. The worker's
entire input is the queue, immutable configuration, a stop event and its error
lock. It has no game pointer, GC traversal, Python call, game RNG call, callback,
or game-memory allocation. The mandatory DLL precompiled header is the only
game-header dependency of the transport translation unit. The original mutex
header protects the queue and transport error status; it does not protect live
game objects. All lifecycle and enqueue calls belong to the game thread.

`CvGame::uninit()` stops and joins the worker before tearing down game state.
This covers reset, save loading (read calls reset), destruction and normal
global teardown. A temporary game object cannot stop another object's observer.
The next finalized update starts a new session. No thread is created, joined,
or destroyed by DllMain, and no global observer destructor joins under the
loader lock. Normal DLL unload requires the existing game/global teardown
path to run first. Abrupt process termination cannot promise final delivery.

## Wire format

One ASCII JSON object per LF-terminated line, at most 512 bytes including LF:

```json
{"protocol":"advciv-observer","version":1,"type":"snapshot","session_id":"01abcdef","snapshot_id":1,"boundary":"post_update","game_turn":42}
```

| Field | Version 1 meaning |
| --- | --- |
| `protocol` | Always `advciv-observer` |
| `version` | Integer `1`; incompatible schemas require a different version |
| `type` | Always `snapshot` |
| `session_id` | ASCII hex correlation token; new after observer start/reset/load |
| `snapshot_id` | Positive uint32, increasing within a session; gaps allowed |
| `boundary` | Always `post_update` |
| `game_turn` | Signed 32-bit value copied from `CvGame::getGameTurn() const` |

The game token combines Windows FILETIME, process ID and an in-process start
counter. It is a practical correlation token, not a secret, save identifier or
global uniqueness guarantee. Snapshot IDs stop at uint32 maximum rather than
wrapping; a reset/new session is then needed. Neither identifier is serialized
to a save. No synchronous network call, game RNG use or observation state enters
gameplay decisions.

The configured queue holds 1–64 records and drops its oldest record when full.
Physical storage is a fixed 64-record array (about 33 KiB); the worker can hold
one additional in-flight record. An absent receiver therefore cannot grow
memory without bound or make capture wait for network I/O. A short critical
section protects each copy. Failed connects retry after an interruptible delay.
Partial sends continue only on the same connection with an overall timeout.
A failed in-flight record is discarded before reconnecting; later snapshots
can proceed. Buffered records are discarded on shutdown. There are no ACKs,
delivery guarantees or commands. Snapshot-ID gaps are expected.

The worker uses nonblocking Winsock2, checks connect completion with select and
SO_ERROR, slices network waits to at most 50 ms, and owns/cleans up its sockets.
`stop()` signals the event and joins before freeing handles, locks or queue
storage. Join has no forced timeout/termination: it waits for the worker to exit
so resources cannot be freed while still in use. OS scheduling and Winsock
provider behavior prevent a hard real-time shutdown guarantee.

## Opt in explicitly

The committed `CvObserverConfig.h` leaves `CV_OBSERVER_ENABLE` undefined in
both Debug and Release. Enable its commented define (or supply the define
consistently to every translation unit) for a deliberately selected build.
No observer Winsock linkage, worker or capture hook is active in default builds.
The native workflow exercises both header variants without changing the
committed default. See [native build notes](observer-build-notes.md).

An enabled DLL additionally requires `CV_OBSERVER_ENABLE=1` in the **game
process environment before launch**. In a Windows command prompt, for example:

```bat
set CV_OBSERVER_ENABLE=1
set CV_OBSERVER_PORT=37631
rem Launch Civ4/AutoIT from this environment so the game inherits it.
```

| Environment variable | Default | Accepted value |
| --- | --- | --- |
| `CV_OBSERVER_ENABLE` | Disabled | Exactly `1` enables capture |
| `CV_OBSERVER_PORT` | `37631` | Decimal 1–65535 |
| `CV_OBSERVER_QUEUE` | `16` | Decimal 1–64 |
| `CV_OBSERVER_RETRY_MS` | `500` | Decimal 50–30000 |
| `CV_OBSERVER_TIMEOUT_MS` | `500` | Decimal 50–5000 per connect/send |

Destination is intentionally fixed at IPv4 `127.0.0.1`; there is no DNS or
arbitrary remote address option. Invalid numeric settings disable this session
with OutputDebugString diagnostics. Settings are read once per session; reset
or relaunch to change them. `lastError()` exposes the transport's most recent
Win32/Winsock failure and a completed send clears it.

On the Linux controller:

```sh
python3 tools/observer/receiver.py --port 37631 --output snapshots.ndjson
```

To forward that listener to the Windows game VM, a Linux-initiated remote SSH
forward would have this shape, where `WINDOWS_RUNTIME_VM` is your own SSH host:

```sh
ssh -NT -o ExitOnForwardFailure=yes -R 127.0.0.1:37631:127.0.0.1:37631 WINDOWS_RUNTIME_VM
```

That command is a configuration example, not executed tunnel evidence. It
requires the Windows SSH server to permit remote forwarding. Keep both ends
bound to loopback. The receiver is standard-library Python 3, validates all
seven fields and framing, rejects duplicate keys and non-increasing IDs for
its bounded history of 64 sessions, and accepts reconnects. Ctrl-C stops it.
It never sends data to the DLL. A disconnected receiver loses incomplete frames.

## Reproduce focused checks

For opt-in gameplay checkpoints, typed Python-object evidence, save/reload
session comparisons and Linux-initiated SSH forwarding, see the
[runtime smoke-test guide](observer-smoke-test.md). Its simulated script tests
are separate from the successful native DLL validation.

```sh
python3 -m unittest discover -s tests/observer -p 'test_receiver.py' -v
python3 tests/observer/run_static_tests.py
```

The static script strictly compiles the actual shared core implementation with `g++ -std=c++03`,
warnings as errors, and a test-only pthread lock adapter. It checks copied
snapshots, JSON edge values, bounded/drop-oldest queues, closure and concurrent
record integrity, then parses actual formatter output using Python JSON.
The receiver suite checks fragmented/coalesced lines, malformed JSON/metadata,
bounded input/history, partial disconnects, reconnection, idle clients and stop.

The DLL `.cpp` wrappers include the game's precompiled header unconditionally
first, as required by MSVC 7.1 `/Yu`. Shared `.inl` files contain the core and
transport implementation; `observer_standalone.cpp` includes those same files
without the game precompiled header for focused testing.

The enabled native workflow compiles and executes `observer_tests.cpp` using
MSVC 7.1 and the real Windows critical sections/Winsock transport on the builder.
It also compiles complete DLLs in all four Debug/Release × disabled/enabled
configurations. Native transport tests cover refused connections, loopback,
graceful/abrupt disconnects, reconnection and connected/disconnected shutdown.
Offline validation also accepts recorded files:

```sh
python3 tools/observer/receiver.py --validate snapshots.ndjson
```

These checks have separate scopes. Successful Linux tests do not prove Windows
compilation. Successful native compilation/standalone builder tests do not
prove the Civ4 executable's actual callback threading, game VM observations,
normal game-exit behavior or SSH path. Those require the user's runtime test.

Suggested game-runtime checks, still awaiting the user's execution:

1. With a default DLL, confirm that setting the environment opt-in alone causes
   no observer connection. With an enabled DLL and no opt-in, expect the same.
2. Start the receiver and forwarding path, then launch the enabled DLL with the
   opt-in inherited by Civ4. Start a game and inspect the initial snapshot.
3. Advance turns and compare `game_turn` with Civ4. IDs should increase; repeated
   update calls during one turn should not create extra records.
4. Save and reload, or start a new game. Expect a new session token and IDs
   restarting at one, even when the loaded turn is earlier.
5. Stop/restart the receiver while advancing turns. Gaps are permitted, and
   Civ4 should continue without waiting for the receiver.
6. Return to the menu and exit normally. Confirm observer activity ends and
   the game exits cleanly. These are runtime expectations, not completed tests.

## Extend the idea

To add another game field, read it beside `getGameTurn()` at the same game-thread
boundary and copy it into an explicitly defined value schema. Keep game objects,
iterators and lazy callbacks out of the queue. Define what the boundary means
before combining multiple fields, and revise the protocol/parser/tests together.
Increase the fixed message limit only with corresponding bounds in both peers.

