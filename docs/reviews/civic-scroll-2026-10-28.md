# Civic scroll drawing review — 2026-10-28

Source branch: UniqueCivicsReligions at d0fc7c0f93320e112903416c17bb2a2030819d60.
Proposed code: https://github.com/SuperXANA/AdvCiv/commit/fa34c89ad3d8507235a3d4c082b6710e305f5265
Read-only baseline: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6, unchanged in fresh inventory.

## CIVICUI-20261028-01 — undefined row coordinate aborts civic drawing

Function: CvCivicsScreen.drawAllButtons.
Original: https://github.com/SuperXANA/AdvCiv/blob/d0fc7c0f93320e112903416c17bb2a2030819d60/Python/Screens/CvCivicsScreen.py#L189
Repair: https://github.com/SuperXANA/AdvCiv/blob/fa34c89ad3d8507235a3d4c082b6710e305f5265/Python/Screens/CvCivicsScreen.py#L229

The XANA 06-27-2026 block initializes iRelY to zero at line 223 and advances it by twice TEXT_MARGIN for each visible civic at line 230. Both addCheckBoxGFCAt (line 232) and setLabelAt (line 234) instead reference iButtonY, which has no definition in this module. The first visible civic therefore raises NameError while drawing. The proposed repair changes exactly those two arguments to iRelY, the intended coordinate relative to the scroll panel.

This keeps the existing per-player isCivicVisible filter, per-column coordinate reset, paired checkbox/label placement, and scroll-panel deletion before redraw. It does not change civic eligibility, adoption weights, native bindings or XML. Original XANA markers and dates remain unchanged.

The baseline Assets/Python/Screens/CvCivicsScreen.py was read for comparison: it draws civic controls directly using fY rather than this feature's new scroll-relative layout. The undefined iButtonY is in the feature block, not an upstream baseline finding. The draft retains the feature branch's Python/ and XML/ paths as supplied; packaging into an installed mod is not validated.

## Verification

Ran python tests/civic-scroll/check.py successfully. The fixture extracts and executes the actual drawAllButtons and isCivicVisible methods under Python 3 with instrumented global context, player, art and screen dependencies. It checks two visible rows at y=30 and y=60, paired checkbox/label coordinates, a separate column starting at y=30, hidden civics, switching to a player with a different allow-list, empty columns, empty redraw and requested panel deletion.

Negative control: executing the same test against the original source raises NameError: name 'iButtonY' is not defined on the first draw. The repaired source passes. The fixture simulates child-widget deletion; actual engine ownership and widget rendering were not exercised. Python 2 numeric-division behavior, imported modules, full screen interaction, C++ permission/binding behavior and in-game visual layout remain unverified. No claim of full-module or Civ4 runtime validation.

No workflow was added. No DLL build was triggered, and this Python-only repair does not establish a DLL result for UniqueCivicsReligions. Any future DLL validation must use the authorized complete pinned-base overlay with the named dll-build workflow.

All source blobs remain present. Exactly one source file changes by two identifiers; the only other code addition is the regression fixture. No changes to 1.14, the original source branch, settings, or other feature branches.

## Coverage retained and remaining work

Fresh branch inventory showed no changed source heads. ReputationWindowDraft's different head is the previously delivered documentation commit, recorded here without reopening its findings.

This pass evaluates the civic-screen XANA drawing/visibility blocks. Marked CvPlayer permission/adoption callers, civic/organization metadata readers, and religion-screen consumers were read for context, but are not certified by this UI fixture. Further native eligibility, hybrid-organization behavior, metadata lifecycle, bindings, XML, cache and religion-screen review should reuse CivicScrollDraft-ChatGPT rather than create another branch for this source.

Two first-pass source branches remain pending: UnitStatusEffects and alert-autofix-1. Partial scopes and unverified native states remain, so the stop gate is false.
