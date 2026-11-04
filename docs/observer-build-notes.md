# Observer native build validation

The isolated `.github/workflows/auto-dll-build.yml` is based on `dll-build`
commit `1cc8c3d24e9fe15126485de0b9e6604167caac36`. It expects the complete
AdvCiv 1.14 source tree from `5970334b64a875b5cdb370c94fc9a98db4eacda6`,
with the ObserverMCP implementation overlaid. The original ObserverMCP input
is `52bc44bf909a302c00a8a7c3e7f7c54a37c43a99`.

The workflow runs four serialized configurations:

| DLL configuration | Observer compile gate | Native observer tests |
| --- | --- | --- |
| Release | disabled | not run |
| Release | enabled | compiled and executed |
| Debug | disabled | not run |
| Debug | enabled | compiled and executed |

The committed header remains disabled. For enabled entries only, the runner
uncomments the one `CV_OBSERVER_ENABLE` marker in its checkout before syncing
sources and calculating source hashes. It never edits the VM's
`Project/Makefile.user`, Makefile, or project configuration.

The existing `civ4-dll-chatgpt-workspace` concurrency group and one-at-a-time
matrix limit are retained. A Windows process check refuses source sync when
`cl`, `link`, `nmake`, `MSBuild`, or `fastdep` is already running. This is an
additional collision check; processes started outside these workflows must
still be coordinated by their operator.

Each entry independently compares SHA-256 hashes of the root `.c`, `.cpp`,
`.h`, and `.inl` files and the exact `observer_tests.cpp` and `observer_standalone.cpp` inputs on Linux and
Windows. The manifest and provenance record the source commit and the gate
variant. Root source deletion remains scoped to source extensions; Project
and machine-local configuration are excluded. Fresh compiler outputs are
removed before rebuilding. Build logs carry a run/attempt/configuration/gate/
commit token before they can be collected.

The selected compiler must pass `_MSC_VER == 1310` before MSBuild runs. The
standalone test target uses that same `$(CPP)`, the selected Toolkit/SDK
include and library paths, and `ws2_32.lib`. Only this standalone test harness
uses `/MT` to link the VC7.1 CRT statically; the game DLL retains its established
`/MD` runtime configuration. This avoids depending on a VC7.1 runtime DLL in the
builder process search path when executing the standalone tests. It compiles `observer_standalone.cpp` and the actual observer tests with
`CV_OBSERVER_STANDALONE`, then executes the resulting Windows executable.
The standalone wrapper includes the same `CvObserverCore.inl` and
`CvObserverTransport.inl` bodies as the production translation units. Production
wrappers include the game PCH unconditionally first, as required by MSVC 7.1
when `/Yu` restores preprocessor state.
`ObserverTests.log` is collected alongside `Build.log`; variant names keep
disabled and enabled DLL artifacts distinct.

Workflow YAML and Bash syntax were checked locally. Native results must be
reported against the exact published commit and Actions run. Successful DLL
compilation and standalone tests do not establish that Civilization IV,
the user's Windows runtime VM, or the SSH forwarding path have been tested.
