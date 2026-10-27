# LLM diplomacy local regression checks

Run from the repository root on Linux with GCC, pthreads and Python 3.8–3.12:

```sh
python3 Tests/LLMDiplomacy/run_tests.py --sanitize
```

The runner copies the current manager and lock sources and extracts the actual
XANA diplomacy blocks from `CvStructs.h/.cpp` into a temporary build directory.
The tests do not duplicate the implementation. Generated sources and binaries
are removed afterward. `CXX` can select a compatible compiler; omit `--sanitize`
when AddressSanitizer/UndefinedBehaviorSanitizer are unavailable.

The Win32 lock shim uses recursive pthread mutexes. Instrumented game stubs
reject game API and RNG access from the worker, and a replacement `operator new`
counts worker allocations. Coverage includes value ownership during vector
relocation, filter dimensions/bounds, selected-only expiration, stale sessions,
bounded mailbox and request storage, duplicates, cancellation and main-thread
imports. Python checks parse the Python 2 source using `lib2to3` and exercise its
actual display method against API stubs.

These are standalone behavioral checks. They do not establish MSVC 7.1 ABI,
engine allocator compatibility, in-game behavior or multiplayer lockstep. ASan
and UBSan do not establish race freedom. LeakSanitizer is disabled because it
cannot run under the host's ptrace instrumentation.
