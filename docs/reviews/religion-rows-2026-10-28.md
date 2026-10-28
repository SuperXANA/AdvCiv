# Religion summary rows follow-up — 2026-10-28

Source UniqueCivicsReligions: d0fc7c0f93320e112903416c17bb2a2030819d60.
Previous assistant head eba850ac55dec0bf4eec42ebbc0fe0243802c1d6; code https://github.com/SuperXANA/AdvCiv/commit/2d0c29857f820acc558a4d5f3549ff31be150819.
Read-only baseline pin remains 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## RELIGIONUI-20261028-01 — stale loop variable gates all summary rows

Affected function: [CvReligionScreen.drawReligionInfo, line 212](https://github.com/SuperXANA/AdvCiv/blob/2d0c29857f820acc558a4d5f3549ff31be150819/Python/Screens/CvReligionScreen.py#L212).
Changed XANA block: [lines 364–397](https://github.com/SuperXANA/AdvCiv/blob/2d0c29857f820acc558a4d5f3549ff31be150819/Python/Screens/CvReligionScreen.py#L364).

The original condition at line 364 tests gc.getReligionInfo(iRel).isMinorOrganization() after the preceding religion loop. iRel therefore denotes that loop's last displayed religion, rather than the religion corresponding to each later summary cell. If that last religion is minor, the entire temple/monastery/missionary summary block is skipped, hiding counts for major religions too. When the last religion is major, the inner loops do not filter minor columns. If no earlier loop supplies iRel, that stale-variable dependency can also fail; the repair removes the dependency.

The proposal builds a local majorReligions list from the whole displayed set (lines 364–366). The rows are shown when this list is nonempty. Each summary-cell loop now checks membership in that list alongside the existing founded-religion check (lines 373, 384, 395). Column advancement stays outside the condition, so a minor religion's blank column does not shift neighboring major religions. All-minor and empty lists draw no such rows. Existing row offsets, count formats and XANA 06-27-2026 boundaries remain.

The code uses ordinary list comprehension/membership available in the legacy Python language, without introducing any()/new library dependencies. Actual Python 2 execution is not claimed.

## Verification

python tests/religion-rows/check.py passed under Python 3. The fixture extracts and executes the actual marked summary block with instrumented context/UI objects and synthetic count maps. It checks mixed religion orders with a minor first/middle/last, single major/minor, empty lists, unfounded major religions, three row labels, count formats, paired active/constructing missionary values, and unchanged horizontal column positions. The original-source negative control fails immediately for [major,major,minor], producing no rows instead of the major counts.

The fixture models the preceding loop's stale variable to reproduce the original defect. It does not execute the whole drawReligionInfo method or its city/missionary counting loops. Python 2 division/runtime, imports, actual CyScreen widget behavior, layout rendering, bindings, native eligibility and gameplay remain unverified.

No workflow or DLL build was triggered. This is a Python-only repair and does not establish a native result for the branch. Only Python/Screens/CvReligionScreen.py changes in production this pass; no installation-path reorganization is performed. Existing CIVICUI-20261028-01 remains in its own report.

## Coverage

Fresh inventory showed no changed source heads. SummonCatchupDraft's head difference was already-delivered documentation. Existing assistant branch CivicScrollDraft-ChatGPT was reused. Original branches and 1.14 remain untouched. UnitStatusEffects stays deferred; the ceiling alert stays closed. Partial scopes and failed/unverified native builds remain, so the stop gate is false.
