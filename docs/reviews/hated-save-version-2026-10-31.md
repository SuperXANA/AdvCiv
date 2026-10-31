# Versioned hated civic/religion AI counters — 2026-10-31

HATED-20261031-07. Read-only original HatedCivicReligionDiplomacy a9c1a754b5e9b64e10ceaa22fd02fa78f3718785; reused HatedDiplomacyDraft-ChatGPT parent a1a0e57918132ca96759ef289c78c583cde79adb. Baseline 1.14 is read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6. Fresh 75-branch inventory found no changed original heads against the coverage ledger in a1a0e57918132ca96759ef289c78c583cde79adb. Prior hated diplomacy/native/workflow reports read before this queued persistence review.

## Defect and correction

CvPlayerAI::read unconditionally read m_aiHateCivicCounter and m_aiHateReligionCounter between the favorite-civic and bonus-trade arrays. CvPlayerAI::write still emitted baseline version 22. Baseline version-22 data contains neither array, so the feature reader takes subsequent arrays and fields as hated counters and displaces the stream.

[Scoped source and executable fixture commit 13278bd71472c39ec4ea9d00944b8efbe878ec74](https://github.com/SuperXANA/AdvCiv/commit/13278bd71472c39ec4ea9d00944b8efbe878ec74):
- [CvPlayerAI.cpp:23190](https://github.com/SuperXANA/AdvCiv/blob/13278bd71472c39ec4ea9d00944b8efbe878ec74/CvGameCoreDLL/CvPlayerAI.cpp#L23190), read: only consume the two new arrays when uiFlag >= 23. Older versions zero both arrays, including destination objects that previously held counters.
- [CvPlayerAI.cpp:23378](https://github.com/SuperXANA/AdvCiv/blob/13278bd71472c39ec4ea9d00944b8efbe878ec74/CvGameCoreDLL/CvPlayerAI.cpp#L23378), write: emit version 23. Existing counter write order is unchanged, as are neighboring baseline array/map operations.
- All 57 original XANA marker lines in this file remain byte-for-byte and in order. Existing assistant scoring, API/scope and workflow corrections retained. No other feature branch integrated.

Version 23 belongs to this independent feature branch. It does not imply integration with the separate GenderSpecificDiplomacy feature, which independently uses its own next version. Previously emitted hated-feature saves marked 22 already contain extra fields and are indistinguishable by version from baseline 22; they are unsupported rather than guessed at. New version-23 saves require this feature reader and are not compatible with unchanged baseline DLLs.

## Scoped verification

Run python tests/hated-save/version-check.py. It extracts the actual reader counter block, writer counter block and writer version statements from CvPlayerAI.cpp. The engine stream and expansionist-hate map serializer are stand-ins. It does not serialize the complete player or real EnumMap encoding.

252 C++03/ASan/UBSan cases passed: versions 21–23, seven value seeds, three array patterns and MAX_PLAYERS 1/2/4/19. Checks include baseline arrays, absent-counter zeroing from stale destinations, version-dependent expansionist-hate map dispatch, exact counter-block byte position, following-object sentinels, version emission and version-23 host-byte round trips. Two independently restored defects fail assertions: ungated reader displaces stream.pos past the boundary; writer version 22 violates written==23.

Compiler flags: -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined. ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression, leak guarantee or native MSVC claim from these fixtures.

## Native validation

Selected source 13278bd71472c39ec4ea9d00944b8efbe878ec74, baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6, workflow source dll-build 1cbd526fddeec564231958870aeab3f2be187a4e. Complete baseline then selected-source DLL overlay verified by recursive blob inventory: all baseline-only files retained, all baseline files outside CvGameCoreDLL unchanged, 362 DLL-tree blobs. Existing corrected feature/control files retained; production code change is limited to CvPlayerAI.cpp. Current workflow copied with previously validated failure-log guards/token retained; only feature-source provenance pin changes for this build.

Tested prepared commit 1df6f1f3fa80feabbba16a0ba719462ca4dee3b0. [Run 41206948813](https://github.com/SuperXANA/AdvCiv/actions/runs/41206948813).
Completed success on first attempt. Release and Debug each passed MSVC7.1 Rebuild with 0 Warning(s), 0 Error(s). Both job logs explicitly reported _MSC_VER == 1310. No C1854 PCH recurrence or CvPlot size assertion in this run.

All four artifact ZIPs downloaded and extracted; actual MSBuild Build.log files inspected. Verified exact provenance pins, 349 matching expected/actual root-source entries per configuration, empty source-hash diffs, and common manifest SHA-256 dc8403980c1bc3247b2fcd39f837bfb69e5f4b2b3f2eaf3dadce7091f6e9e14f. Verified MZ/PE signatures, machine 0x14c, PE32 0x10b and DLL characteristics for both binaries.

- Release DLL/log artifact 13045175164; source diagnostics 13043944429. DLL 6,565,888 bytes; SHA-256 a7c908ecd4b2889dcd796062842d043ee9ed179bd5ae967f3d64909fcaf79a28.
- Debug DLL/PDB/log artifact 13045445075; source diagnostics 13045235380. DLL 25,186,304 bytes; SHA-256 978aeb4093ef699e05b729b85f07636d5869c14775bd898f980df92f95f145ed. PDB 70,585,344 bytes.

The code commit used [skip ci] while preparing the pinned build. This final documentation/ledger update also uses [skip ci] and does not alter tested production code or workflow. Binaries and full runner logs are not committed to the repository.

## Remaining limits

This is a structural baseline-save counter-block correction. Actual complete engine saves, XML installation/defaults, leader-info cache-format compatibility, attitude cache effects, game turn execution and multiplayer synchronization remain unverified. The original user source is unchanged and is not certified by the corrected assistant build. No missing mechanics were invented, no user branches edited, no branches merged, no PR opened or force push used.
