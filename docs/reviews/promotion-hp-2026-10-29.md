# Promotion HP declarations — 2026-10-29

Source PromotionAltersUnitHPValues at d64fade8bb53d8c4bd92521c6a606b323af91025.
HP-20261029-01. Existing branch inventory checked: no feature-specific assistant draft existed.

Completed:
- CvPromotionInfo constructor, CvInfo_Unit.cpp:1817: replace getMaxHPValueChange(0) with m_iMaxHPValueChange(0). The former names a method, not an initializable member.
- CvUnit::getMaxHPValueModifier, CvUnit.cpp:10487: add const to match the header and permit the existing const maxHitPoints caller.
- CvUnit.h:1097: declare changeMaxHPValueModifier(int), matching the existing definition and promotion update call.
XANA markers, HP arithmetic, metadata/cache read/write and XML tag names unchanged.

Verification: actual revised getter/mutator methods extracted into a strict C++03 fixture with ASan/UBSan. Three hundred deltas (-99..200) applied and removed through a const-reference query; no-op zero changes and initial zero checked. The fixture class/constructor/global maxHP stand-in and miniature promotion-info initialization are synthetic; this is not a full CvUnit/CvPromotionInfo compilation. Negative control restoring nonconst getter failed compilation with declaration mismatch. No MSVC7.1/DLL/game result claimed; CI skipped.

Remaining review: maxHitPoints (header:424–427) simply adds the modifier to global base. Nonpositive maximum HP and existing combat/damage/healing assumptions need coherent evaluation before allowing arbitrary negative values. Modifier persistence/reconstruction and metadata/schema integration also remain unverified. No new min/max gameplay rule invented in this declaration-only draft.
