# Updated DLL workflow review — 2026-10-28

Reviewed dll-build at 33b1f40e1ba564ab88950b3688425efb334126d1, including
parent cff8f1b9e5af2de1c5cccf7ffb127f38bf3583ce.
This changed source takes precedence over unchanged feature review rotation.
The source fixes the parent's duplicate && and introduces sequential Release/Debug,
compiler probing, source manifest checking and artifact provenance.

Demonstration commit ac7fa3cd3d1457ee3944616a11d526692a6bc076 on reused PartnerDiplomacyBuild-ChatGPT.
Commit includes [skip ci]. C++ files unchanged; dll-build preserved.
The earlier native code result on this branch remains historical evidence for
0b80d617ec269caff3241245ea7af1eb285d4c38, not validation of this new workflow.

## Findings (source .github/workflows/auto-dll-build.yml line numbers)

WORKFLOW-20261028-01 — build invocation, lines 68 and 70.
The same command runs before try and again inside try; only the second exit
status is checked. This duplicates work and can mask a first failed invocation
if the second succeeds. Remove the first call; retain the checked try/finally
call at draft line 70.

WORKFLOW-20261028-02 — source sync, lines 109–116.
After syncing CvGameCoreDLL and validating the remote root source manifest,
the workflow syncs ./ to the same destination. This introduces repository-root
content and a nested CvGameCoreDLL after validation, contrary to the intended
DLL-only overlay. Remove that final sync. Two scoped DLL syncs remain, before
the manifest check. Machine-local Project exclusion is retained.

WORKFLOW-20261028-03 — artifact name, line 151.
Release and Debug use the same immutable upload-artifact v5 name. Sequential
execution does not make uploads with a duplicate name valid. Include
matrix.configuration (draft 144), preserving distinct binaries and provenance.

WORKFLOW-20261028-04 — log paths, lines 67 and 139.
The command cds to Project and gives relative filenames JustErrors.log and
JustWarnings.log. The copy step instead searches Project/$CONFIG/*.log.
The draft makes the full log filename explicit as Build.log, removes old
copies of those three logs before invocation, and copies exactly those names
from Project (draft 130–132). Cleanup of old log files avoids presenting stale
logs as current output. Remote logger behavior still needs native validation.

## Provenance and preserved settings

Filled baseline, feature and workflow-source placeholders for this reused
branch's existing overlay: baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6,
feature source d37d0ca0adcaef748e0c7b32ccd90568dbee05e0, workflow source
33b1f40e1ba564ab88950b3688425efb334126d1.
These values must be replaced when copying to another target. github.sha
identifies the exact derivative commit. Existing feature refinements remain
in branch history; feature_source records the original overlay source.

Preserved the new -t:go target, logger options, branch-ignore, matrix,
shared concurrency, compiler probe, pinned Actions and PDB copy. The remote
project target definition was not inspected; this review does not certify
whether go forces the desired complete rebuild. The proposed Windows 11
game harness is still described as in progress, and was not invoked.

## Verification limits

YAML BaseLoader parse, Release/Debug matrix assertions, single command call,
two DLL-scoped syncs, configuration-specific artifact name, explicit provenance
and log paths, plus bash -n for all Bash run blocks passed.
Reproducible check: python tests/workflow-review/check.py (PyYAML required).
These are static/syntax checks, not mock or actual remote build execution.
PowerShell/pwsh is unavailable locally. No SSH, MSBuild, compiler or DLL load
was executed. No new DLL result is claimed, nor any reuse of old run results
to certify this changed workflow.

All proposal and documentation commits use [skip ci]. No settings changed,
no original branch edited, no new branch created. Existing coverage/skip
gates and prior verified DLL evidence are retained.
