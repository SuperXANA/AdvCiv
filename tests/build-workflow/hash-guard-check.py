#!/usr/bin/env python3
"""Exercise the workflow's exact manifest gate without contacting the builder."""
import argparse
import pathlib
import subprocess
import tempfile
import textwrap

parser = argparse.ArgumentParser()
parser.add_argument("--workflow", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[2] / ".github/workflows/auto-dll-build.yml")
parser.add_argument("--manifest", type=pathlib.Path)
args = parser.parse_args()
workflow = args.workflow.read_text()
start = workflow.index("          test -s actual-sources.txt")
end = workflow.index("          # Add commit hashes", start)
guard = textwrap.dedent(workflow[start:end])
assert "diff -u expected-sources.txt actual-sources.txt" in guard
assert "exit 1" in guard
expected = args.manifest.read_bytes() if args.manifest else (
    ("0" * 64 + "  ./Alpha.cpp\n" + "1" * 64 + "  ./Beta.h\n").encode()
)
assert expected and expected.endswith(b"\n")
rows = expected.splitlines(keepends=True)
first = rows[0]
bad_hash = (b"1" if first[:1] != b"1" else b"0") + first[1:]
case_name = first[:68] + first[68:].swapcase()
added = b"f" * 64 + b"  ./ExtraSource.cpp\n"
cases = [
    ("matching", expected, True),
    ("changed_hash", bad_hash + b"".join(rows[1:]), False),
    ("missing_source", b"".join(rows[1:]), False),
    ("extra_source", expected + added, False),
    ("changed_name_case", case_name + b"".join(rows[1:]), False),
    ("empty_remote_manifest", b"", False),
]
for name, actual, accepted in cases:
    with tempfile.TemporaryDirectory(prefix="source-hash-guard-") as temp:
        root = pathlib.Path(temp)
        (root / "expected-sources.txt").write_bytes(expected)
        (root / "actual-sources.txt").write_bytes(actual)
        (root / "source-verification.txt").write_text("status=collecting\n")
        script = "set -euo pipefail\n" + guard + "\nprintf reached > compiler-reached.txt\n"
        result = subprocess.run(["bash", "-c", script], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reached = (root / "compiler-reached.txt").exists()
        assert (result.returncode == 0) == accepted, (name, result.returncode)
        assert reached == accepted, (name, "unexpected continuation state")
        status = (root / "source-verification.txt").read_text()
        if accepted:
            assert status.endswith("status=passed\n")
        elif actual:
            assert status.endswith("status=failed\n")
        print(name + ": " + ("accepted" if accepted else "rejected before compiler"))
print(str(len(cases)) + " manifest-gate cases passed")
