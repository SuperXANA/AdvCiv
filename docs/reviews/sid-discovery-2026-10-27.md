# Sid attribution discovery refinement — 2026-10-27

## Scope and pins

The changed head of SidSaysPatch is [8c52c7e7b85cb574ee0494611a8931efb3b20d01](https://github.com/SuperXANA/AdvCiv/commit/8c52c7e7b85cb574ee0494611a8931efb3b20d01), adding XANA-bracketed code in SelfMod.cpp/.h. This takes priority over pending first-pass branches. The original branch is preserved. The previous source head had no marked patch implementation; these are new findings, not a repeated build attempt.

Read-only baseline: 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6, root tree 47b2d29512e87bf9ce742114a669de7d6d84420f.
Named workflow source: dll-build at 058e4d0e1760f76195071823d3e2dc85c81b7285.
The isolated branch retains every baseline blob and overlays the feature's two DLL files with the scoped refinement. SelfMod.cpp's unmarked content matches pinned 1.14 ignoring whitespace; existing upstream runtime patches are unchanged.

## SID-20261027-01 — unbounded address assumptions precede every match

The [new narrow/wide scanners](https://github.com/SuperXANA/AdvCiv/blob/8c52c7e7b85cb574ee0494611a8931efb3b20d01/CvGameCoreDLL/SelfMod.cpp#L472) call memcmp across 0x00400000–0x01000000. That fixed span is not proof of the EXE's actual image extent, readable pages, or ownership by this module. A hole or inaccessible page can fault before unprotectPage is reached. Equal replacement lengths only constrain overwrite size; they do not make those reads or patch-site selection valid.

The source explicitly requests candidate-address logging before narrowing the patch. Implement that discovery stage: obtain the loaded EXE base, validate PE32/i386 headers, bound the section table and section extents against SizeOfImage, inspect read-only initialized-data sections, and copy bounded chunks using ReadProcessMemory. Failed/short reads are skipped and reported as incomplete. No raw EXE memory is dereferenced and no page protections are changed by the new locator.

## SID-20261027-02 — prefix matches are not verified UI patch sites

The source compares only the supplied label length, so it can match a longer string prefix or unrelated binary data. It overwrites every occurrence without showing that the UI uses those bytes. The four boolean OR assignments also cannot distinguish partial write failure from another successful match.

This branch deliberately replaces the speculative writer with a diagnostic-only locator. It requires terminated ANSI or aligned UTF-16LE labels; logs candidate address, RVA, encoding, EXE timestamp/checksum/size; limits detailed candidate logging to 128 lines; and never modifies the image. A candidate is not evidence of an actual UI use. Only the exact source spellings "Sid Says:" and "Sid's Tips" are searched; other case/punctuation/localization variants are not silently inferred.

## SID-20261027-03 — success state set before success or enablement

[patchSidSays](https://github.com/SuperXANA/AdvCiv/blob/8c52c7e7b85cb574ee0494611a8931efb3b20d01/CvGameCoreDLL/SelfMod.cpp#L576) sets m_bSidSaysPatched before calling applyIfEnabled. A failed patch, or a disabled operation that the base class reports as a successful no-op, therefore appears patched to callers.

The diagnostic draft never sets the success flag. It returns immediately when DISABLE_EXE_RUNTIME_MODS is enabled; otherwise the existing entry point runs discovery and explicitly reports that no strings changed. No startup caller or Python exposure is added. The source entry point remains available for controlled debugger/integration use; it is not a once-only completion guard in this diagnostic draft and should not be called every frame.

## Mechanics and integration

The intended "Sol Says:" / "Sol's Tips" attribution to Solais a Tuath is retained as a future UI change. First establish whether the EXE actually owns the displayed wording. If confirmed, use observed version-specific RVAs and surrounding bytes to define a narrow patch, validate all expected sites before mutation, preserve/restore each touched page's original protection, and expose truthful disabled/failed/applied states. If the wording comes from mod text assets, change those assets instead.

No candidate addresses or live EXE contents are available in this environment. The diagnostic DLL does not rename the UI, and no automatic memory writer is installed. No save format or gameplay mechanics change is introduced.

## Verification

Local command: `python3 tests/sid-discovery/check.py`.

The actual SidSaysLocator class, public header and patchSidSays entry point are compiled against simulated Win32 API/PE fixtures under strict C++03 with -Wall -Wextra -Werror -pedantic plus ASan/UBSan (LeakSanitizer disabled for host compatibility). Tests cover relocated module addresses, exact terminated labels, UTF-16LE block-boundary overlap without duplicate reports, longer-prefix rejection, excluded writable/executable/discardable sections and outside-image data, malformed DOS/PE extents, unreadable blocks, repeated inspection, bounded logging, disabled operation, unchanged image bytes and false patched state.

Those fixtures are not a native DLL or actual Windows API/runtime test. Native Release/Debug results are recorded below after the isolated workflow finishes. The workflow is adapted from the named dll-build source using the already validated complete-overlay harness: CvGameCoreDLL sync root, retained machine Project config, stale top-level source cleanup only, exact root-source manifest, clean outputs, MSVC 7.1 probe, forced rebuild, sequential configurations, exact artifact collection and guarded cleanup. Workflow changes are limited to this isolated branch.

Windows API references: [ReadProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory) and [IMAGE_SECTION_HEADER](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_section_header). These document accessible-range checks and section characteristic flags; they do not establish any Civ4 label location.

Native validation: pending for the first published code commit. No historical run is claimed for this change.
