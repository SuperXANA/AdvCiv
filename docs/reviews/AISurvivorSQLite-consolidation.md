# AISurvivorSQLite branch consolidation

Older: AISurvivorSQLiteFixes-ChatGPT at b38cc2a2cfb4cafa2460ab5b96bd677504105663, last worked 2026-10-27T16:16:45Z.
Newer: AISurvivorSQLiteBuild-ChatGPT at c14b70d183f00d8a1d0cdcf811102e3f7460c766, last worked 2026-10-28T14:11:26Z.

Histories were unrelated (GitHub reports no common ancestor). The consolidation
uses both heads as parents, with the newer tree as the starting point. It retains
all newer-only files and resolves overlaps as listed below.

- CvGameCoreDLL/CvGame.cpp: keep_newer_active_file
- CvGameCoreDLL/CvGlobals.h: keep_newer_active_file
- docs/SQLiteBuildIntegration.md: keep_newer_active_file
- docs/SQLiteSafetyReview.md: keep_newer_active_file

All older-only files are imported. Older conflicting documentation is preserved
under docs/branch-history/AISurvivorSQLiteFixes-ChatGPT/docs/. Older conflicting C++ versions remain
reachable through the second parent; active newer compilation fixes and baseline
migration code are retained. 

CvGameCoreDLL, build workflow and project toolchain files are unchanged from the
newer branch. [skip ci] prevents an unnecessary DLL build. Historical success or
failure remains attached to its original tested SHA; this merge is not new DLL
or gameplay validation. The unchanged spell build failure is not retried.

The older branch is retained for manual cleanup. Once this merge is verified,
future work should use AISurvivorSQLiteBuild-ChatGPT. No original feature branch is modified.
