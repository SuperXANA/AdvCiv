# Promotion XP refinement

Source: PromotionAltersUnitXPValues at 09741c7206588a8fc42b1e62b90c76ecaea13a55.
Read-only base: AdvCiv 1.14 at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Build workflow: dll-build at 058e4d0e1760f76195071823d3e2dc85c81b7285.

## Findings and changes

The XANA 03-25-2025 Promotion XP Changes blocks introduce additive attack and
defense base-XP values for opponents defeating a promoted unit.

- Both unit getter definitions lacked the const qualifier in their declarations.
  Both modifier mutators were declared const but defined as non-const. The
  refinement makes getters const and mutators non-const throughout.
- Modifier totals were initialized to zero but not saved or reconstructed.
  CvUnit::read restores promotion flags directly rather than invoking
  setHasPromotion. A new updateXPValueModifiers helper clears and sums the
  promotion-derived totals after the complete unit record is read. Calling it
  repeatedly does not accumulate duplicate bonuses. The unit writer and unit
  save version remain identical to 1.14; no redundant XP totals are added.
- Schema tags are optional, but the XML reader omitted explicit defaults.
  Both XP tags now use optional zero defaults.
- The English help claimed a percentage, while attackXPValue and defenseXPValue
  add integers before existing combat strength ratios and XP limits. The wording
  now describes a change in base combat experience. The second argument uses
  s2 rather than s1, spurious percent signs are removed, and the nested localized
  strings are passed as GetCString pointers.

For example, a non-barbarian unit with base attack/defense XP of 4/2 and the
source branch's Combat I example modifiers of +3/+2 has base XP values of 7/4.
The final award still depends on the existing combat rules; it is not guaranteed
to increase by exactly 3/2 XP and is not a percentage modifier.

## Base and asset reconciliation

The selected DLL files are overlaid on the complete pinned base, retaining
base-only files. Unmarked differences from the older branch snapshot are
reconciled back to current 1.14, including combat modifier accounting, cargo
visibility, the upgradeXPChange default argument, and wide-character text
formatting. Only the XANA promotion-XP changes are introduced into those files.

The build branch keeps 1.14's 54-promotion XML roster and adds the source's
marked Combat I example (+3 attack, +2 defense). The source's 71 additional,
unmarked promotion records are outside this scoped demonstration. The source
schema additions and three localized text keys are included. This branch is a
baseline-compatible feature demonstration, not a complete MLP content package.
Original branches are untouched.

The copied workflow changes only the rsync source path to ./CvGameCoreDLL/ for
the complete-base layout.

## Verification

Run: python tests/promotion-xp/check.py

The focused C++03 fixture extracts the actual declarations and implementations
of the modifier accessors, mutators, reconstruction helper and base XP methods.
It checks construction, reconstruction, repeated reconstruction, stacking,
removal, signed changes, and existing barbarian/animal behavior. It also checks
the reconstruction call's position after promotion loading, optional XML
defaults, the Combat I data, optional schema entries, and text placeholders.
These checks passed before publishing.

The fixture uses mock promotion data and does not execute Civ4's actual save
stream, XML/XDR loader, text formatter, combat engine or EXE integration.
Real saves and gameplay remain untested, including saves using the source's
larger promotion roster. The Windows GitHub Actions run is the full DLL build
check; its exact commit, result and artifact are reported with the review.
