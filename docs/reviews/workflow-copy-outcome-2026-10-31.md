# Compiled DLL artifact copy-outcome guard — 2026-10-31

WORKFLOW-20261031-08. Reviewed changed read-only dll-build source 733140746ebe7a488db066aa85d299897ff6e0e0 against 1cbd526fddeec564231958870aeab3f2be187a4e after fresh 75-branch inventory and global ledger 8fdddb020c1f880e751eb35420c35516f07a07a8. dll-build is the only changed original head. Existing HatedDiplomacyDraft-ChatGPT reused at f843027233b4cacee3709a5de80b16506189a5d0; no competing feature-specific assistant branch created.

The new source adopts the earlier strict log removal, invocation token and always/build_started failure-log guards. It moves source diagnostics after failure-log upload and makes missing diagnostics an error. Those user edits are retained, not reported again as new defects. Hash/build commands and C++ code are unchanged in the source delta. The existing staged-source mtime mitigation from tested assistant commit 4d4672665066214036fb57678e13a6b8990db2ec is retained in this prepared derivative, together with BuildTiming.log; its precise relationship to earlier C1854 remains unconfirmed as previously recorded.

## New defect

The source adds if: always() && steps.build.outcome == 'success' to Upload Compiled DLL Artifact. This ignores failure of the preceding Copy DLL files Over To Linux step. A successful compiler run followed by failed/partial SCP can therefore still invoke upload-artifact. Its if-no-files-found:error is not a completeness check: one partial DLL or one existing artifact path is enough to satisfy the action's file discovery. Debug also previously checked only the DLL's nonempty status, allowing an empty transferred PDB to pass.

This is an artifact-publication guard regression, separate from compiler success and the already corrected failure-log path.

## Committed correction

[Prepared implementation/test commit cb7d75b4d03077b644f24f4b41647f53f06a4a64](https://github.com/SuperXANA/AdvCiv/commit/cb7d75b4d03077b644f24f4b41647f53f06a4a64), .github/workflows/auto-dll-build.yml:
- [Copy step ID, line 286](https://github.com/SuperXANA/AdvCiv/blob/cb7d75b4d03077b644f24f4b41647f53f06a4a64/.github/workflows/auto-dll-build.yml#L286): name the transfer step copy_dll.
- [Local cleanup, line 297](https://github.com/SuperXANA/AdvCiv/blob/cb7d75b4d03077b644f24f4b41647f53f06a4a64/.github/workflows/auto-dll-build.yml#L297): remove existing local DLL and PDB before transfer.
- [Debug symbol check, line 305](https://github.com/SuperXANA/AdvCiv/blob/cb7d75b4d03077b644f24f4b41647f53f06a4a64/.github/workflows/auto-dll-build.yml#L305): require a nonempty PDB after successful Debug SCP.
- [Upload guard, line 311](https://github.com/SuperXANA/AdvCiv/blob/cb7d75b4d03077b644f24f4b41647f53f06a4a64/.github/workflows/auto-dll-build.yml#L311): require both build.outcome and copy_dll.outcome to equal success, retaining always() so an unrelated earlier diagnostic failure does not suppress a completed current transfer.

No C++/DLL source or XANA marker change. User-owned dll-build and 1.14 remain unchanged.

## Local checks

python tests/build-workflow/copy-check.py executes the actual DLL-copy Bash with local SCP stand-ins:
1. Release succeeds with current DLL and no leftover PDB.
2. Debug succeeds with current DLL and PDB.
3. A partial DLL transfer returning failure rejects the copy.
4. A partial PDB transfer returning failure rejects the copy.
5. Empty DLL with successful SCP rejects the copy.
6. Empty Debug PDB with successful SCP rejects the copy.

The script statically checks the exact upload expression and step ID. It does not emulate or execute the GitHub Actions expression engine. Three negative controls restore the build-only upload guard, omit the new PDB nonempty check, or omit local binary cleanup; each fails the corresponding assertion. The guard control is a structural regression check, not a remote artifact-upload experiment.

Five actual-block log-collection cases and six source-manifest guard cases also pass with stand-ins, including missing optional BuildTiming.log. YAML parsed by these fixtures. No network/native/Actions-expression result is implied by the local checks.

## Full native validation

Read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6; selected source f843027233b4cacee3709a5de80b16506189a5d0; actual workflow source 733140746ebe7a488db066aa85d299897ff6e0e0. Selected DLL code previously passed at 1df6f1f3fa80feabbba16a0ba719462ca4dee3b0; that older run is only the control.

Recursive inventory confirms complete baseline plus selected DLL overlay with all baseline-only files retained, all baseline files outside CvGameCoreDLL unchanged, and 362 DLL-tree blobs. Only workflow/test preparation changes are applied on the existing assistant branch; no feature mixing or protected VM Project edits.

Exact tested commit cb7d75b4d03077b644f24f4b41647f53f06a4a64. [Run 41221093729](https://github.com/SuperXANA/AdvCiv/actions/runs/41221093729).
Completed success. Release and Debug both passed full MSVC7.1 Rebuild with 0 warnings / 0 errors. Both job logs explicitly report _MSC_VER == 1310. Copy DLL files and guarded Upload Compiled DLL Artifact succeeded in both configurations. No build/compiler failure occurred in this run.

Downloaded/extracted all four ZIPs and inspected both actual Build.log and BuildTiming.log files. Verified exact tested commit/configuration/baseline/source/workflow pins, 349 matching expected/actual root source records per configuration, empty hash diffs and common manifest SHA-256 dc8403980c1bc3247b2fcd39f837bfb69e5f4b2b3f2eaf3dadce7091f6e9e14f, identical to the previous passing code control. Verified MZ/PE signatures, x86 machine 0x14c, PE32 0x10b and DLL characteristic in both binaries.

- Release DLL/log/timing artifact 13050395813; source diagnostics 13050206391. DLL 6,565,888 bytes, SHA-256 24c5fce00e1a1953e561221b0fd2f13e1d81ec76e8317e66aca702dcc62f682a.
- Debug DLL/PDB/log/timing artifact 13050575771; source diagnostics 13050371213. DLL 25,186,304 bytes, SHA-256 d634a5b4e7d3e1468b42152f8897fa15aeb28b3c91860bd63f35ab9bcb6324a6. PDB 70,585,344 bytes.

No binary, PDB, full runner log or credentials committed. DLL source and XANA markers remain unchanged.

The remote false copy-outcome path is not fault-injected by this normal validation run. A passing normal matrix validates successful transfer/upload and the actual complete native build for its exact commit; transfer-failure behavior is covered by local Bash cases plus the static Actions guard check. No gameplay/save/metadata certification from this workflow validation. Final evidence/ledger commit uses [skip ci].
