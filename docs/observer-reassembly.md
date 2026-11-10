# Reassembling ObserverMCP version-2 captures

`tools/observer/reassemble.py` reads the receiver's NDJSON. It groups validated
frames by session ID, world instance ID, and capture ID, then assembles each
observed player's cities in chunk order. It runs offline with Python 3 and the
standard library. See the [ObserverMCP protocol](observer.md) for the input format.

Run from the repository root with a finished receiver log. The same command
accepts a saved smoke-runner observation log that uses the version-2 format.
Preserve the original record order within each session.

```sh
python3 tools/observer/reassemble.py snapshots.ndjson > captures.ndjson
```

Omit the path or use `-` to read from standard input. Use a separate output
path when redirecting. This is a batch tool for finite logs. It retains observed
records in memory and emits each capture at end of input, in the order its key
first appeared. Waiting for end of input lets it detect a repeated record even
if the capture had already appeared complete. The tool keeps session tokens as
received, matches world IDs case-insensitively, and emits world IDs in lowercase.

## Reading the output

Each output line is a JSON object. Capture objects use `type: "capture"` and
carry the source `protocol` and `version`. They have a `status`, `diagnostics`,
and the `game_session.world_instance.state` hierarchy. The capture type has a
different shape from the receiver's `snapshot` records.

| Status | Meaning | Player and city data |
| --- | --- | --- |
| `COMPLETE` | Every advertised player and city chunk arrived and passed the consistency checks. | All players and their full `cities` lists. An observed zero-city player has `cities: []`. An observed empty world has `players: []`. |
| `INCOMPLETE` | At least one advertised player or city chunk is missing. | Only observed players appear. A player with all chunks still has `cities`. A partial player has `city_chunks` preserving each received `city_part`, `city_offset`, and `cities` list. |
| `INVALID` | The records conflict or contain a duplicate. | The capture key and diagnostics identify the problem. Player data is omitted. |

Players are ordered by the wire `player_index`, which is distinct from the
game's `id`. `city_count` and `total_population` retain the game's advertised
values, including for partial players. `diagnostics.received_records` counts
all validated frames for that capture, including repeats.
`diagnostics.missing_player_index_ranges` and each observed player's
`missing_city_part_ranges` use inclusive, zero-based `[first, last]` pairs. A
range of `[[1, 1]]` identifies just index 1.

The tool reuses the receiver's per-frame parser, including its checks on chunk
indexes, offsets, and lengths. It also checks shared capture metadata and player
metadata across records, along with snapshot ordering and duplicate player or
city IDs. Duplicate snapshot or chunk records, including exact repeats, produce
an `INVALID` capture. `diagnostics.errors` carries machine-readable error codes
such as `capture_metadata_mismatch` and `duplicate_city_part`. A frame that
fails receiver validation produces a separate `type: "input_error"` line with
its 1-based `line` and `message`. Processing continues with other frames.
Capture completeness is evaluated using the validated frames.

Gaps between observed snapshot IDs produce separate `type: "snapshot_gap"`
records with `game_session_id` and an inclusive `missing_snapshot_id_range`.
These diagnostics precede the capture results and can span a world change within
one session. Queue drops, interrupted sends, and filtered logs can leave the
same gaps. Complete, consistent captures retain their status across adjacent
gaps. Missing records outside the observed ID range cannot be counted from the
IDs alone. An entirely absent capture has no observed state to reconstruct.

| Exit code | Meaning |
| --- | --- |
| `0` | Every observed capture is complete, or input is empty. |
| `1` | A frame or capture is invalid, or an I/O error occurred. This takes precedence over missing records. |
| `2` | At least one observed capture is incomplete, and no invalid input or I/O error occurred. |

For automation that consumes fully reassembled captures, select `type == "capture"`
and `status == "COMPLETE"`. The output can contain complete captures alongside
errors or partial captures.

## Verification scope

```sh
python3 -m unittest discover -s tests/observer -v
```

The reassembly regression tests use synthetic version-2 frames to exercise
multiple players, chunked empires, zero-city players, missing records, duplicates,
map regeneration, and session changes. The native DLL and transport have separate
validation evidence in the [validation ledger](observer-validation.md) and the
[November 8 build](https://github.com/SuperXANA/AdvCiv/actions/runs/42531919749).

Gameplay observations, save/reload behavior in Civilization IV, and live SSH
forwarding still require the [runtime smoke test](observer-smoke-test.md).
