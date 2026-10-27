# LLM diplomacy review — 2026-10-27

Reviewed `LLMDiplomacyTextGeneration` at `5d12da1af2d4e6f9048d02f7e79eccb66c39051e`.
Baseline: read-only `1.14` at `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Workflow copied from `dll-build` at `058e4d0e1760f76195071823d3e2dc85c81b7285`.
Separate custom-comment branch inspected: `CustomAIDiplomacyComments` at
`ca3531fac64b2e70ea66b98745e45733da1f0c37`; its gameplay/contact changes are not imported.
This isolated branch contains the complete baseline plus the marked feature and
review refinements. Original branches remain untouched.

## Findings and implemented changes

| ID | Source at reviewed feature head | Problem and refinement |
|---|---|---|
| LLM-001 | `CvDynamicDiploManager.h/.cpp`, `CvStructs.h/.cpp`, `Python/CvDiplomacy.py` | Compile blockers include malformed declarations/comparisons, resizing a hash map, const access/mutex issues, duplicate getter signatures, missing forward types, and Python `||`. Corrected C++03 container/API definitions and Python syntax. |
| LLM-002 | `CvStructs.cpp:636-659,672-678,844-851`; manager `:287-289` | Getters delete the objects they return; raw owning pointers are shallow-copied during vector growth; empty-string references and local `c_str()` returns dangle. Prompt, result, filter and group data now own values; UI bindings return copied strings. |
| LLM-003 | manager `:85-98`; baseline `CvMemoryManager.cpp` | Bounds/initialized checks precede locking and race reset. STL allocations on a worker can call engine memory hooks in Debug. Only the raw bounded mailbox is worker-facing; cache setup, copying, filtering and destruction are main-thread guarded. Session IDs and one-time request retirement reject old or duplicate completion. |
| LLM-004 | `Python/CvDiplomacy.py:478-503`; structs `:737-770,854-872` | Candidate enumeration reads/consumes each string twice, may shift indices, uses CyPlayer objects where bindings expect integer IDs, and can replace user-action labels. Python now asks once for an AI display value; C++ atomically filters/selects and counts only that line. Three selected displays expire it. User buttons stay authored XML. Pure inspection consumes no uses. |
| LLM-005 | `CvStructs.cpp:608-613,691-724,779-841` | Enabling one filter dimension leaves every other dimension all-false, suppressing otherwise valid lines. Malformed short vectors allow out-of-range reads. Empty dimensions now pass through; enabled dimensions allocate independently and bounds-check. |
| LLM-006 | `CvGame.cpp:49-51,613-615`; `CvEnumMacros.h:61-63`; `CvXMLLoadUtilitySet.cpp:696-698` | Construction/reset initializes against XML too early, while the load path lacks a proper post-data cache init. Construction/reset now clear only; init occurs for new games and after loaded game data. PlayerCharacter enum/XML registration has no class or storage/schema in either source; deferred that incomplete registration. |
| LLM-007 | Unmarked portions of feature `CvGame.cpp/.h`, `CvPlayer.cpp`, `CvStructs.h`, `CyInfoInterface3.cpp` | Copied upstream files predate current 1.14 and would regress save formats, renamed APIs and event Python bindings. Retained current baseline code outside XANA blocks. Installed the Python change at `Assets/Python/CvDiplomacy.py` and retained its feature source copy. |

## Worker/main-thread contract

1. On the main thread, reserve a group, construct `LLMPromptData` with the current
   nonzero session ID, fill prompt/filter values, and call `registerPrompt`.
2. The future transport owns a raw snapshot of request bytes and scalar IDs.
   It must not construct or destroy these STL-backed DLL prompt/result types on
   its worker. WinINet remains to be implemented.
3. Worker calls `submitResponse(session, player, comment, group, bytes, length)`.
   It copies at most 4096 bytes, rejects embedded NUL, stale/unregistered/duplicate
   results and full queues, and performs no allocation, game API or RNG call.
4. Main thread imports results, then the local UI getter filters against current
   AI identity, attitude and power, selects through `GC.getASyncRand`, and returns
   an owned string. Only local presentation counts change. No save/checksum or
   synchronized RNG is used by the new subsystem.
5. Transport must handle false enqueue/register returns and main-thread
   `cancelPrompt` on failure. Stop and join workers before DLL unload.

Bounds are 32 queued results, 128 pending prompt metadata objects, and 256 issued
request groups per AI/comment/session. IDs are never reused, including canceled
requests. This intentionally avoids late-result aliasing. At exhaustion XML
remains available; a future renewable transport should add monotonically unique
request tokens with bounded reusable slots. Reset/load invalidates the session.

## Remaining work and mechanics

No local model transport, background thread host, prompt producer, character-card
loader or submission caller exists in the reviewed source. The repaired cache
therefore defaults to XML until a producer is implemented. This change does not
claim live generation.

For future requests, include the authored XML line, speaker/recipient identity,
comment/event type, visible facts and a compact personality card in a main-thread
snapshot. Keep the generated prose cosmetic: the independent custom-comment
branch should select contact type/actions/timers deterministically before UI text
selection. Bragging or intimidation prose must never add friendship, threats or
trade actions by parsing model output. Bind sensitive event lines to a recipient
and context token, and add a turn/event deadline; three-use expiry alone cannot
prove factual freshness after a long delay. Current filters recheck attitude/power
but do not validate arbitrary claims about war, treaties or a third leader.

## Verification

`python3 Tests/LLMDiplomacy/run_tests.py --sanitize` passed against the actual
modified source under strict C++03, ASan and UBSan with Linux Win32/game stubs.
It exercises ownership across vector relocation, filters, three selected uses,
pure inspection, sessions/cancellation/duplicates, bounded queues, worker zero
operator-new allocations and main-only engine/RNG calls, and Python grammar/UI
fallback behavior. LeakSanitizer cannot run under this host's ptrace environment.
These tests do not establish Win32 race freedom, DLL ABI, engine runtime behavior
or multiplayer lockstep.

Native DLL validation is performed by this branch's copied/adapted workflow:
complete source overlay, protected machine-local Project configuration, stale
root-source removal and manifest check, clean outputs, MSVC 7.1 compiler probe,
and fresh sequential Release/Debug builds. Exact results are recorded after CI
completion; no historical run is substituted for this commit's validation.

### Native validation history

- Commit `ba775199e924dd06d21b48971da387276e70b13d`, run `40547868228`:
  both Release and Debug reached the MSVC 7.1 compiler and stopped on C4288,
  promoted to C2220 by `/WX`, at manager lines 417–418. MSVC's legacy for-loop
  scope conflicted with a later `iGroup` declaration. Renamed selected-group and
  selected-variant locals rather than disabling warnings or changing compiler
  flags. The import helper is also private so all completion ownership flows
  through the main-thread mailbox drain.
