# Colony leader configuration integration

Source branch: LeaderSpecificColonySplitVassal at c2c8690c4854482f98ea3ceae2974586e5d1503d.
Read-only base: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Workflow source: dll-build at 058e4d0e1760f76195071823d3e2dc85c81b7285.

## Finding COLONY-XML-01

The XANA 05-25-2025 Leader-Specific Colony Split loader reads DerivativeLeader
during the second leader-info pass. The source branch supplies no XML schema
extension, and the pinned base's CIV4CivilizationsSchema.xml declares no such
element. The feature therefore lacks a matching schema configuration contract.

The refinement adds a text-only DerivativeLeader definition and one optional
occurrence at the end of LeaderHeadInfo. Existing records can omit it; the
constructor and XML lookup preserve NO_LEADER in that case. The C++ feature,
second-pass loading, Python getter and XML-cache fields are retained.

## Configuration example

In Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml, locate LEADER_ELIZABETH.
At the end of that existing LeaderHeadInfo record, after DiplomacyMusicWar and
before its closing tag, add:

```xml
<!-- XANA: 05-25-2025 Leader-Specific Colony Split -->
<DerivativeLeader>LEADER_WASHINGTON</DerivativeLeader>
<!-- XANA: 05-25-2025 Leader-Specific Colony Split -->
```

This is an inactive documentation example. The build branch leaves all live
leader records unchanged. Omission leaves the preference disabled; an explicit
NONE can clear the value using the existing lookup convention.

## Mechanics retained

The preferred leader receives +1000 on top of the existing random score 1..100.
The preferred civilization independently receives +1000. Matching both gives
+2000. A leader-only and civilization-only candidate therefore share a priority
tier, with their random scores deciding between them.

The preference is applied after existing eligibility filtering: the parent
civilization is excluded, ever-used civilizations and leaders are excluded, and
leader/civilization compatibility is enforced unless Lead Any Civ is enabled.
Naming a successor from the parent's own civilization will not make that
civilization eligible. The choice uses the parent's leader identity, preserving
the source branch's behavior under Random Personalities.

No selection policy, game save stream, or live XML leader preference is changed.

## Base reconciliation and build

The selected DLL files are overlaid onto the complete pinned base while
retaining base-only files. Older unmarked differences in the selected snapshot
are reconciled to pinned 1.14; the XANA feature blocks are retained. All original
branches remain unchanged. The copied workflow changes only the rsync source to
./CvGameCoreDLL/ for the complete-base layout.

The schema and baseline leader XML were parsed locally. Structural checks
confirmed the definition, optional child occurrence, its position, omission by
all existing baseline leaders, and that the example's leader names exist.
This is structural inspection, not execution of Civ4's XDR validator.

The triggered Windows workflow is the full DLL compilation check. Its exact
commit, run result and artifact are reported with the review. XML loading,
XML-cache-enabled builds, actual colony creation and gameplay remain untested.

## MSVC 7.1 build confirmation — 2026-10-28

The successful [DLL build run 40527777945](https://github.com/SuperXANA/AdvCiv/actions/runs/40527777945)
for `ColonyLeaderBuild-ChatGPT` at commit
`26b6ff5428b9bff6d7f79ea2892e424a7444cf4a` completed Release compilation,
linking and DLL artifact upload. This proves that the assistant-refactored code
at that revision builds under MSVC 7.1 (the Visual Studio 2003 C/C++ compiler).

The remote environment initializes Visual Studio 2010's `vcvarsall.bat` and
uses MSBuild to invoke the NMake project. The machine-local
`R:\CvGameCoreDLL\Project\Makefile` and `Makefile.user` select the VS2003
compiler/toolchain. Visual Studio 2010 supplies the build tool environment;
the DLL's C/C++ compilation uses MSVC 7.1.
