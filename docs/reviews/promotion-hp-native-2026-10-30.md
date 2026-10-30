# Promotion HP native validation — 2026-10-30

Prepared on existing PromotionHPDraft-ChatGPT.

- Read-only original source: PromotionAltersUnitHPValues at d64fade8bb53d8c4bd92521c6a606b323af91025.
- Pinned complete 1.14 base: 5970334b64a875b5cdb370c94fc9a98db4eacda6.
- Feature/refinement snapshot overlaid: f67d2df605582d9946f8466ff8ca60d82c2b80a2.
- Actual workflow source: dll-build at af5c2f130e195c23a011a5aed35fcff212389f2e.

Complete base retained; every supplied feature blob is overlaid without deleting base-only DLL files. Workflow provenance placeholders populated; matrix Release/Debug and shared concurrency unchanged. Native result pending publication/run observation. Earlier declaration and load-time modifier reconstruction reviews remain applicable. No runtime HP bound, actual-save or gameplay certification.

## Observed terminal result

Exact attempted overlay: ddd250d584219a24aeb6ccbe455f681f5843a6db.
Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41022387851 — completed, failure.
Release job 123952472385 and Debug job 123952472554 both failed before the compiler invocation, at source synchronization over SSH.

- Release, 2026-10-30 07:51:18 UTC: ssh: connect to host 192.168.2.252 port 22: Connection timed out; rsync connection unexpectedly closed; rsync code 255.
- Debug, 2026-10-30 07:53:37 UTC: same SSH timeout and closed connection; rsync code 12.

Artifact API checked after completion: total_count 0. There is no produced ZIP or MSBuild Build.log to download/unzip. Targeted runner-log lines were used only because this pre-build failure produced no artifact logs. The compiler probe and MSBuild were not reached; no MSVC toolset, warnings/errors, link result or DLL is verified for this commit. The Actions step's title includes MSBuild but its initial synchronization failed first.

Retain this complete pinned overlay on the existing branch. No automatic retry in this pass, no source fix inferred from a network timeout, and no machine or repository settings changed. Resume native validation after builder SSH reachability is restored; no need to prepare another branch. Other eligible repository review work remains.

Overlay checks before publication: no baseline DLL blobs missing and no feature DLL blob SHA mismatches. Native build preparation did not alter the four feature DLL blobs. Earlier extracted declaration/reconstruction checks remain their own scoped evidence and do not substitute for this missing full build.

## Retry after SSH recovery: attempt 2

The same run was explicitly retried after builder connectivity was reported restored. MSVC was reached. Both Release (job 123963298099) and Debug (job 123963298483) failed at CvUnitAI.cpp:519 with C2660: CvUnit::upgradeXPChange does not take 0 arguments. No artifacts were produced by this attempt; compiler diagnostics therefore came from targeted runner-log lines.

HP-20261030-03 — CvUnit.h:279: restore the pinned 1.14 declaration's default argument UnitTypes eUnit = NO_UNIT and its advc.131e annotation. The supplied feature header had omitted this default while the retained baseline CvUnitAI::AI_upgradePriority calls upgradeXPChange() without arguments. The actual feature and baseline implementations of upgradeXPChange have the same body, and eUnit is unused; restoring the interface default preserves baseline semantics and leaves HP behavior unchanged. This is overlay compatibility, not a change to XP mechanics. Follow-up native result pending.
