# ObserverMCP coverage and validation ledger

## Pinned inputs

| Input | Exact commit |
| --- | --- |
| Read-only ObserverMCP source | `52bc44bf909a302c00a8a7c3e7f7c54a37c43a99` |
| Read-only AdvCiv 1.14 baseline | `5970334b64a875b5cdb370c94fc9a98db4eacda6` |
| Copied dll-build workflow | `1cc8c3d24e9fe15126485de0b9e6604167caac36` |
| Final implementation and native harness | `c68a89f633a817efd7d69d70dcca0a89c6703014` |

Work is confined to `ObserverMCP-ChatGPT`. The complete baseline supplies the
build tree; the original source branch is preserved. Original blob IDs remain
`23bfaae2dcdbc07c284788957a677eaa22930733` for README and
`f61b5c1a52c6f87ce714acfe43defedf18cb0113` for the mutex header.

## Coverage

| Area | Review or validation |
| --- | --- |
| Original branch | Complete tree inspected: README and mutex header only |
| Game boundary | Reviewed post-finalized-update hook and scalar turn capture |
| Reset/load/normal teardown | Reviewed read → reset → uninit → stop path and destructor/global teardown |
| Worker ownership | Copied bounded records only; no live game object/callback traversal |
| Synchronization | Original Windows RAII lock; copy, drop-oldest, close and concurrent access tests |
| Protocol | v1 seven-field NDJSON, 512-byte bound, uint32 IDs and signed turn values |
| Transport | Winsock2 localhost only, nonblocking connect/send, deadlines, reconnect, FIN/RST handling and joined shutdown |
| Opt-in | Default-off compile gate plus exact launch environment opt-in; both build variants |
| Receiver | Python 3 framing/schema/order validation, bounded buffering/history, reconnect and shutdown |

## Static and offline results

All passed against the final implementation source:

- Strict `g++ -std=c++03 -Wall -Wextra -pedantic -Werror` core compilation using
  the explicit test-only pthread lock adapter.
- Three executions of the real core tests, each with two producers and a
  consumer exercising 10,000 records, integrity and consumed-plus-dropped accounting.
- Copy consistency, bounded/drop-oldest queue, closure rejection and JSON numeric edges.
- Python standard JSON parsing of actual C++ exporter records, and offline
  receiver validation of three actual formatter records.
- All 11 Python receiver tests, including split/coalesced TCP frames, invalid
  JSON/metadata/types, duplicate IDs/keys, bounded memory, disconnects and stop.
- Workflow YAML parsing and Bash syntax checks.

## Native attempts

| Run | Commit | Result |
| --- | --- | --- |
| [41787645233](https://github.com/SuperXANA/AdvCiv/actions/runs/41787645233) | `67a9d8f9bbe659271fd8ba75a7662206c0c84fa7` | All four compile jobs failed at C1020 before the PCH guard was fixed |
| [41788006610](https://github.com/SuperXANA/AdvCiv/actions/runs/41788006610) | `0c1611711b748570e0a95ab0614b5ce878e7a679` | All four complete DLLs compiled, each with zero warnings/errors; enabled standalone executables could not launch with `/MD` (`0xc0000135`) |
| [41788851432](https://github.com/SuperXANA/AdvCiv/actions/runs/41788851432) | `c68a89f633a817efd7d69d70dcca0a89c6703014` | Completed successfully: all four DLLs compiled with zero warnings/errors; both enabled Windows standalone test executions passed |

### Final native matrix

| Configuration | Compile gate | Full DLL | Executed Windows observer tests | DLL/log artifact |
| --- | --- | --- | --- | --- |
| Release | Disabled | Pass, 0 warnings/errors | Not enabled | [13302169010](https://github.com/SuperXANA/AdvCiv/actions/runs/41788851432/artifacts/13302169010) |
| Release | Enabled | Pass, 0 warnings/errors | Pass | [13303250231](https://github.com/SuperXANA/AdvCiv/actions/runs/41788851432/artifacts/13303250231) |
| Debug | Disabled | Pass, 0 warnings/errors | Not enabled | [13302962163](https://github.com/SuperXANA/AdvCiv/actions/runs/41788851432/artifacts/13302962163) |
| Debug | Enabled | Pass, 0 warnings/errors | Pass | [13303700121](https://github.com/SuperXANA/AdvCiv/actions/runs/41788851432/artifacts/13303700121) |

Every final artifact was downloaded/extracted. Actual `Build.log` files confirm
the full native builds; both actual `ObserverTests.log` files explicitly report
`PASS: snapshot/JSON/queue/concurrency/Windows loopback/disconnect/shutdown`.
The selected compiler passed `_MSC_VER == 1310`; the resulting PE32 DLLs report
linker version 7.10. Standalone test executables use a static VC7.1 CRT, while
the game DLL retains the established build configuration.

All 361 verified source/test records match independently on Linux and Windows.
SHA-256 manifest digests are identical between Debug and Release for each gate:

| Gate | Expected and actual source manifest SHA-256 |
| --- | --- |
| Disabled | `32759b47dfa53ee50135228e5b71df290e5a35e078c01df265c61862718e127a` |
| Enabled | `587be05956e345e57d827fde66baf4f74bab497f03399c4a0b704e0cb7464b27` |

Binary inspection of all four DLLs confirms `WS2_32.dll`, the protocol literal
and the runtime opt-in variable are present only in enabled artifacts. They
are absent in both disabled artifacts. The committed config header remains off.

`OBS-BUILD-01` resolved: MSVC 7.1 `/Yu` cannot restore the PCH inside the
standalone include conditional. Production `.cpp` files now include it
unconditionally first, and standalone wrappers compile the same `.inl` bodies.

`OBS-BUILD-02` resolved and execution verified: native test `/MD` binaries
could not locate a dependency at launch. Only the standalone test executable
now uses `/MT`; the game DLL configuration is unchanged. The final run's actual
`ObserverTests.log` confirms execution succeeded in both enabled jobs.

Actual failure artifacts were downloaded and extracted, and their `Build.log`
and `ObserverTests.log` files inspected. Source manifests passed before all
builds; `_MSC_VER == 1310` was verified by the selected native compiler.

Documentation and separate runtime-smoke tooling after the validated code
commit do not alter its DLL, native test or workflow inputs. The original source branch and the exact
README/mutex blob IDs were rechecked after implementation and remain unchanged.

## Runtime boundary

No Civilization IV game observation, runtime VM, AutoIT integration, cdb project
or SSH-forwarding path is claimed as executed or completely tested. Standalone
Windows tests on the builder have a narrower scope. The game callback threading,
turn observations, reload session boundaries and normal game exit remain for
the user's runtime testing described in [the guide](observer.md).

## Runtime smoke-runner preparation — November 4, 2026

Added opt-in tooling on the existing assistant branch; native implementation,
receiver, native harness and workflow are preserved from the validated inputs.
See [runtime smoke-test instructions](observer-smoke-test.md).

| Area | Evidence in this preparation |
| --- | --- |
| Reused protocol | Imports the existing `Receiver`; accepted callbacks contain exact-schema Python dictionaries with real integer/text values |
| Checkpoints | Independent expected turns; uninterrupted advancement; externally attested reload plus changed session and saved turn; process-exit evidence separate from peer EOF |
| Journals | Machine-readable `passed` / `failed` / `not_run`, accepted snapshots, raw per-connection bytes and connection/error events |
| SSH | Linux remote-forward argv and cleanup tested with mocks only; no home-host access |
| Windows launcher | Configurable executable/working directory/arguments and child-only environment; explicit opt-in; source reviewed only |
| New automated tests | All 20 passed, using synthetic producers and actual Linux loopback sockets |
| Existing receiver tests | All 11 passed unchanged |
| Native validation | Existing successful four-configuration run remains applicable to unchanged DLL/native inputs; no rebuild triggered by this tooling scope |
| Civilization IV / Windows PowerShell / home tunnel | **Not executed** |

The new tests include malformed numeric types, duplicate/reordered IDs,
fragmented/coalesced frames, gaps, reconnections, turn mismatch/regression,
missing evidence, unchanged reload sessions, stale action tokens, action
failure versus unavailable actions, listener failure, bounded checkpoint
history, non-overwriting artifacts, and shutdown EOF provenance.

`OBS-SMOKE-01`: completed preparation and simulated verification. Runtime
validation remains open. Neither a running SSH process, a DLL launch, nor a
new session alone is counted as successful gameplay validation. Sender-side
refused-connect errors and DLL worker teardown need independent diagnostics
and are explicitly `not_run` in the result's unobservable-check list.

