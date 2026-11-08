# ObserverMCP hierarchical snapshot prototype

This isolated idea branch combines the complete read-only AdvCiv 1.14 baseline
`5970334b64a875b5cdb370c94fc9a98db4eacda6` with ObserverMCP input
`52bc44bf909a302c00a8a7c3e7f7c54a37c43a99`. The original branch, README and
`CvCriticalSectionMutex.h` are preserved. New integration blocks carry XANA
ObserverMCP date markers. This is a small observation transport; an MCP server
and game-control commands are future, separate work. It is independent of cdb.

To adopt the idea in a combined mod, copy the new observer implementation files
and the unchanged mutex header, then merge the marked include, update,
regeneration and uninitialization hook blocks into your current `CvGame.cpp`. This branch's `CvGame.cpp` and native DLLs contain
the pinned 1.14 baseline plus this prototype; other independent feature branches
are outside this validation scope.

## Capture boundary and ownership

`CvGame::update()` calls `CvObserver::postUpdate(*this)` after its update loop,
only when `isFinalInitialized()` is true. The first eligible call captures the
owning thread ID; later calls on another thread are ignored. The bridge reads
the stored map seed and turn, iterates alive players and their cities, and copies
plain values into bounded schema objects. It emits an initial capture, then one
whenever the observed turn or world changes. This labels the end of an update
call, not a guarantee that every player's turn is complete. Several internal
updates may occur before that boundary, and same-turn city changes alone do not
trigger a new capture.

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

Protocol version 2 is hierarchical: session, world, captured state, player and
city objects nest below one another. One ASCII JSON object is written per
LF-terminated line, at most 4096 bytes including LF. A typical record is:

```json
{"protocol":"advciv-observer","version":2,"type":"snapshot","game_session":{"id":"01abcdef","sequence":1,"world_instance":{"id":"89abcdef-00000001","sequence":1,"map_seed":2309737967,"state":{"capture_id":1,"snapshot_id":1,"boundary":"post_update","game_turn":42,"player_count":1,"player_index":0,"players":[{"id":0,"team_id":0,"civilization_type":1,"leader_type":2,"is_human":true,"is_barbarian":false,"city_count":1,"total_population":3,"city_offset":0,"city_part":0,"city_part_count":1,"cities":[{"id":10,"x":20,"y":30,"population":3}]}]}}}}
```

The [JSON Schema Draft 4 definition](observer-v2.schema.json) and the Python
receiver enforce the exact fields and cross-field bounds.

| Object/field | Version 2 meaning |
| --- | --- |
| `protocol`, `version`, `type` | `advciv-observer`, integer `2`, `snapshot` |
| `game_session.id` | ASCII hex correlation token; new after observer start/reset/load |
| `game_session.sequence` | Positive process-local session counter, starting at 1 |
| `world_instance.id` | Eight hexadecimal map-seed digits, hyphen, eight hexadecimal world-sequence digits |
| `world_instance.sequence` | Positive counter, incremented for each world within its session |
| `world_instance.map_seed` | Uint32 copied from `CvGame::getInitialRandSeed().first` |
| `state.capture_id` | Positive uint32 shared by every record from one capture boundary |
| `state.snapshot_id` | Positive uint32, increasing per record within a session; gaps allowed |
| `state.boundary` | Always `post_update` |
| `state.game_turn` | Signed 32-bit value copied from `CvGame::getGameTurn() const` |
| `state.player_count` | Number of alive players, including minor civilizations and Barbarians |
| `state.player_index` | Zero-based alive-player index, or -1 in the single empty-player-state record |
| `players[]` | Zero or one copied player record per line |
| `players[].city_count` | Total city count, not merely the number in this line |
| `players[].total_population` | Cached total copied from `CvPlayer::getTotalPopulation()` |
| `players[].cities[]` | Up to 32 city IDs, map coordinates and population sizes |

The session token combines Windows FILETIME, process ID and the in-process
session counter. It is a practical correlation token, not a secret, save
identifier or global uniqueness guarantee. Regeneration does not create a new
session: the post-generation `CvObserver::mapRegenerated` notification and a
seed comparison make the next finalized update increment only the world
sequence. The sequence distinguishes even a repeated seed. The observer reads
the stored map RNG seed; it never calls `CvRandom::get()` or advances game RNG.
Observer IDs are not serialized to saves and never enter gameplay decisions.

A turn/world capture emits one record per alive player when at most 32 cities
are present. Larger empires use consecutive city chunks: `city_offset` is
`city_part * 32`, `city_part_count` covers the player's full city list, and
`capture_id` reassembles all players/chunks from the same boundary. An empire
with no cities has one empty `cities` array. A game with no alive players has
one record whose `players` array is empty. IDs stop at uint32 maximum rather
than wrapping; a reset/new session is then needed.

The configured queue holds 1–64 records and drops its oldest record when full.
Physical storage is a fixed 64-record array (about 256 KiB); the worker can hold
one additional in-flight record. Consequently, consumers may see missing
players or city chunks and must not call a capture complete solely because one
of its records arrived. An absent receiver cannot grow memory without bound or
make capture wait for network I/O. A short critical section protects each copy.
Failed connects retry after an interruptible delay. Partial sends continue only
on the same connection with an overall timeout. A failed in-flight record is
discarded before reconnecting; later snapshots can proceed. Buffered records
are discarded on shutdown. There are no ACKs, delivery guarantees or commands.
Snapshot-ID gaps and incomplete capture IDs are expected.

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
bound to loopback. The receiver is standard-library Python 3, validates the
version-2 hierarchy, chunk invariants and framing, rejects duplicate keys and
non-increasing IDs for its bounded history of 64 sessions, and accepts reconnects. Ctrl-C stops it.
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
3. Advance turns and compare `state.game_turn` with Civ4. IDs should increase;
   repeated update calls during one turn should not create extra captures.
4. Regenerate the map on turn 0. Expect the same `game_session.id`, an incremented
   world sequence, a new world ID/capture, and turn-0 player/city state.
5. Save and reload, or start a new game. Expect a new session token and IDs
   restarting at one, even when the loaded turn is earlier.
6. Stop/restart the receiver while advancing turns. Gaps and partial captures are
   permitted, and Civ4 should continue without waiting for the receiver.
7. Return to the menu and exit normally. Confirm observer activity ends and
   the game exits cleanly. These are runtime expectations, not completed tests.

## Extend the schema

1. Add plain copied fields to `CvObserverSnapshot`, `CvObserverPlayer`,
   `CvObserverCity`, or a new fixed-size value struct in `CvObserverCore.h`.
2. Read the live value in `CvObserver.cpp` beside the existing game-thread
   capture. Never store a game object, iterator or callback in the value.
3. Serialize it with `CvObserverJsonWriter` in `CvObserverCore.inl`. Reuse the
   existing session/world/state nesting; add a new bounded chunk type rather
   than allowing an unbounded array into one message.
4. Update `observer-v2.schema.json`, receiver validation, C++ formatter tests,
   Python consumer tests and this document together. Compatible additions can
   retain version 2 only when all peers are updated; incompatible changes need
   a new protocol version.
5. Exercise the actual C++ formatter through `run_static_tests.py` and run the
   native enabled/disabled DLL workflow. Keep the 4096-byte producer/consumer
   bound aligned if a future schema requires a different fixed capacity.

