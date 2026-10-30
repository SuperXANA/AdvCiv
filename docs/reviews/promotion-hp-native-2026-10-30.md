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

## Verified follow-up result

Exact compiled commit: f809096d101f8ddf4f155c5d89999237010f12d5.
Run: https://github.com/SuperXANA/AdvCiv/actions/runs/41026141850 — completed, success.
Release job 123964598759 and Debug job 123964598464 both passed the _MSC_VER == 1310 compiler probe and full Rebuild. Both actual extracted MSBuild Build.log files report Build succeeded, 0 Warning(s), 0 Error(s).

Downloaded both GitHub artifact ZIPs through the artifact endpoint, unzipped them and inspected their Build.log, provenance, source manifests and binaries. Provenance matches the exact commit, configuration, pinned base, feature snapshot and workflow source. actual-sources.txt equals expected-sources.txt in each package. Both DLLs have valid MZ/PE signatures, x86 machine 0x14c, PE32 optional header 0x10b and IMAGE_FILE_DLL flag.

| Configuration | Artifact ID | DLL bytes | DLL SHA-256 |
| --- | ---: | ---: | --- |
| Release | 12964370350 | 6569984 | 9928066274b66546d488377b76787639ac44c23d292c9f47355383f65655c325 |
| Debug | 12963343212 | 25194496 | 9620e164cdde81dfe1b48ae40050f75ea255a836f12e6b228671d6e51001515f |

Release artifact: https://github.com/SuperXANA/AdvCiv/actions/runs/41026141850/artifacts/12964370350
Debug artifact: https://github.com/SuperXANA/AdvCiv/actions/runs/41026141850/artifacts/12963343212
Debug package also contains CvGameCoreDLL.pdb (70634496 bytes). Archive metadata sizes are 2355286 and 18575650 bytes respectively.

The previously blocked native attempt and compiler failure are retained as history, superseded by this exact tested commit's success. No further code change was required beyond the baseline default-argument restoration. This verifies full DLL compilation/linking and artifact contents for the prepared overlay; no Civilization IV game session, actual-save loading, XML/cache loading or gameplay HP bounds/overflow/combat behavior is certified. Documentation-only result commit uses [skip ci].
