# CityBonusLeaderDiplomacyModifiers review

Source: `084726f21f44dda2f1e8b4e3906da7ae66ce4759`.
Read-only 1.14 baseline: `5970334b64a875b5cdb370c94fc9a98db4eacda6`.
Build workflow source: dll-build at `058e4d0e1760f76195071823d3e2dc85c81b7285`.

## Findings and refinements

**CITYBONUS-20261027-01 — narrow/wide description mismatch.**
CvGameTextMgr.h:276–277 and .cpp:16162 take char const* for the extra
description, but the call at .cpp:16332 passes CvInfoBase::getDescription(),
which returns wchar const*. There is no implicit conversion between these
pointer types, so the marked feature does not compile as written. The helper's
declaration and definition now accept wchar const*. The description remains wide
through the existing getText call; an omitted or null description becomes an
empty wide string. No lossy conversion is introduced.

**CITYBONUS-20261027-02 — unnecessary city traversal for zero modifiers.**
CvPlayerAI.cpp:8688 checks the target's hasBonus before reading the leader's
modifier. Baseline CvPlayer.cpp:4268 searches cities until one has the resource.
Both the attitude-update loop and the two display passes iterate all bonuses.
Even an entirely unconfigured leader therefore incurs repeated city scans.
The refinement reads the modifier first and returns immediately when it is zero.
For a three-resource, three-city example with no resources, the original order
can make nine city checks; the revised zero-modifier query makes none.
Nonzero modifiers retain the original availability test and value.

**CITYBONUS-20261027-03 — missing configuration/help assets.**
The source requests BonusAttitudeChanges and references two new text keys, but
its tree supplies only DLL files and README. The pinned civilization schema
does not define this list. Added an optional ordered list at the end of
LeaderHeadInfo, integer attitude values, and English entries for the two
referenced keys. Both text entries use numeric argument 1 and resource-name
argument 2, matching the actual getText call. The list may be omitted or empty.
No live leader preferences are enabled.

Original source:
[helper declaration](https://github.com/SuperXANA/AdvCiv/blob/084726f21f44dda2f1e8b4e3906da7ae66ce4759/CvGameCoreDLL/CvGameTextMgr.h#L273),
[helper and caller](https://github.com/SuperXANA/AdvCiv/blob/084726f21f44dda2f1e8b4e3906da7ae66ce4759/CvGameCoreDLL/CvGameTextMgr.cpp#L16159),
[query](https://github.com/SuperXANA/AdvCiv/blob/084726f21f44dda2f1e8b4e3906da7ae66ce4759/CvGameCoreDLL/CvPlayerAI.cpp#L8685),
[XML read](https://github.com/SuperXANA/AdvCiv/blob/084726f21f44dda2f1e8b4e3906da7ae66ce4759/CvGameCoreDLL/CvInfo_Civilization.cpp#L1070).

## Preserved mechanic and configuration example

This is directional: the observing AI's personality supplies the modifier for
each resource. It applies once if **any** target city has access to that
resource, as defined by existing CvCity::hasBonus. It is not a count of copies,
connected cities or resource plots. A resource outside the capital's network
can still qualify through another city. Different resources add independently.
No availability rule, attitude-cache refresh schedule, war adjustment or save
format has been changed.

For example, append the following after a leader's DiplomacyMusicWar element.
This example is documentation only; it is not activated in live leader data:

```xml
<BonusAttitudeChanges>
    <BonusAttitudeChange>
        <BonusType>BONUS_HORSE</BonusType>
        <iAttitudeChange>2</iAttitudeChange>
    </BonusAttitudeChange>
    <BonusAttitudeChange>
        <BonusType>BONUS_IVORY</BonusType>
        <iAttitudeChange>-1</iAttitudeChange>
    </BonusAttitudeChange>
</BonusAttitudeChanges>
```

The preferences remain absolute attitude points, rather than percentages.
Resource names come from the existing translated bonus descriptions.

## Construction and verification

The complete current 1.14 baseline is retained. All XANA blocks in the six
selected DLL files were overlaid, with unmarked differences reconciled back
to 1.14. Original 05-11-2025 markers remain. The refinement adds the optional
schema, separate English text and focused regression checks. The copied workflow
retains the compiler probe, shared build concurrency, exact source manifest,
stale-root-source protection and generated-output cleanup already validated by
FamilyRelationsBuild-ChatGPT. No unrelated feature code is imported.

`python3 tests/city-bonus/check.py` passed under strict C++03 with warnings
as errors. It compiles the actual new declarations, getter, query and help
method against stubs, using the actual baseline hasBonus method. It checks
null/zero configuration, missing/present resources, positive/negative modifiers,
multiple cities without multiplication, city-scan counts, both display passes,
wide accented descriptions, null/omitted descriptions, text-key selection,
zero entries and attitude totals.

The XDR structure was checked for optional placement, child order, unique
definitions and integer values, and against the child ordering of all 54
unchanged baseline leaders. Text placeholder numbering was checked.
ASan/UBSan also passed with halt-on-error and
`ASAN_OPTIONS=detect_leaks=0`. LeakSanitizer itself is unavailable under this
host's ptrace environment. These tests do not run Civ4's Microsoft XML validator
or its real text translator.

Native build commit: `60d88bfa0edf155d542cd24cb4853b2651897b0f`.
[Run 40575245169](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169)
uses this exact commit and completed successfully. Both Release and Debug
verified MSVC 7.1 (`_MSC_VER == 1310`), rebuilt with **zero warnings and zero
errors**, uploaded the requested exact DLL file, and completed generated-output
cleanup. GitHub reports both jobs successful.

| Configuration | Job | Artifact |
|---|---|---|
| Release | 122439805171 | [DLL 12767885725](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169/artifacts/12767885725) |
| Debug | 122439804572 | [DLL/PDB 12766979488](https://github.com/SuperXANA/AdvCiv/actions/runs/40575245169/artifacts/12766979488) |

Artifact metadata names the exact code SHA above and reports both archives
unexpired. Validation covers compiler/linker logs, the source-manifest check,
and exact-file artifact uploads; no downloaded PE inspection was performed.
All 872 baseline files remain; the six selected DLL files and civilization
schema are the only modified baseline files. This final results update changes
documentation only, so the workflow's path filter avoids rebuilding unchanged
DLL source.

Game startup, localized rendering, resource acquisition/loss cache timing,
real-save behavior and multiplayer remain untested. English entries are
provided; no additional translations are claimed. The disabled legacy binary
info-cache path is retained but not enabled or validated.

## Coverage checkpoint

Reviewed every XANA block in CityBonusLeaderDiplomacyModifiers' six DLL files.
Its heads and the previously reviewed feature/assistant heads were unchanged.
The separate rebellious-team branch was inventoried for a future rotation;
no findings are claimed for code not yet read. Existing assistant work was
left untouched, including FamilyRelationsBuild-ChatGPT.
