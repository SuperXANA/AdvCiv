# Dynamic rank fixed-point return conversion — 2026-10-29

RANK-20261029-02. Reuse DynamicRankDraft-ChatGPT95823f56307f3c62cd9f0aaf10ffca38dab2b48b; original source ff5560a1f2af752be1446e8bbd8d37bcdbe64a1e unchanged.

AI_getShareRelativeProgressAttitude, CvPlayerAI.cpp:8691 and8694:
- Unbounded path returns scaled rAttitude from int function. Baseline ScaledNum.h:235 explicitly comments out operator int; line236 exposes round().
- Bounded path passes scaled into range alongside int bounds. Convert to integer with rAttitude.round() before range.

Use nearest integer via existing round API, consistent with fixed-point attitude conversion; not an implicit truncation. This is an explicit conversion decision for previously ill-formed return paths. Rank normalization, counter division, threshold checks, zero-limit-unbounded convention and bound magnitude unchanged. Existing XANA markers preserved.

Verification: actual complete method and baseline ScaledNum conversion declaration inspected. Local execution environment is offline (environment_offline), so no new compiler fixture or runtime check ran. No MSVC7.1/DLL success claimed. Partial draft [skip ci]. Existing earlier fixture evidence does not certify this new change.

Remaining rank normalization integer division/denominator, threshold policy, limit abs range and metadata/save integration remain queued; no broader mechanics redesign. GitHub connector functional, so review/publication was possible despite local execution outage. Not fully blocked and recurring review remains eligible.
