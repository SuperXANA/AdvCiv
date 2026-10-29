# FFHSpellCreation branch consolidation

Older: FFHSpellCreationFixes-ChatGPT at aba892958cd98a04fac5aba63a828ef717cd7c10, last worked 2026-10-26T16:49:24Z.
Newer: FFHSpellCreationBuild-ChatGPT at 581063899df1123d0a4e45f43ef1e5b346457701, last worked 2026-10-26T21:14:59Z.

Histories were unrelated (GitHub reports no common ancestor). The consolidation
uses both heads as parents, with the newer tree as the starting point. It retains
all newer-only files and resolves overlaps as listed below.

- Assets/XML/Units/CIV4PromotionInfos.xml: restore_older_feature_asset_over_unmodified_baseline
- Assets/XML/Units/CIV4UnitSchema.xml: restore_older_feature_asset_over_unmodified_baseline
- CvGameCoreDLL/AdvCiv4lerts.cpp: keep_newer_active_file
- CvGameCoreDLL/CvInfo_Terrain.h: keep_newer_active_file
- CvGameCoreDLL/CvInfo_Unit.h: keep_newer_active_file
- CvGameCoreDLL/CvPlayer.h: keep_newer_active_file
- CvGameCoreDLL/CvUnit.h: keep_newer_active_file

All older-only files are imported. Older conflicting documentation is preserved
under docs/branch-history/FFHSpellCreationFixes-ChatGPT/docs/. Older conflicting C++ versions remain
reachable through the second parent; active newer compilation fixes and baseline
migration code are retained. The two older XML files replace byte-identical baseline copies in the newer build tree, restoring feature data omitted by DLL-only overlay preparation. They parse as XML, but are not engine/schema validated.

CvGameCoreDLL, build workflow and project toolchain files are unchanged from the
newer branch. [skip ci] prevents an unnecessary DLL build. Historical success or
failure remains attached to its original tested SHA; this merge is not new DLL
or gameplay validation. The unchanged spell build failure is not retried.

The older branch is retained for manual cleanup. Once this merge is verified,
future work should use FFHSpellCreationBuild-ChatGPT. No original feature branch is modified.
