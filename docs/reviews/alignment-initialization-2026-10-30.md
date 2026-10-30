# Nondecaying alignment initialization — 2026-10-30

ALIGNMENT-20261030-03. Read-only RealisticAIDecisions source f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e; reused ReputationWindowDraft-ChatGPT parent 343689debf230b2e49ddbf927f62d83db0b22ac5. Full 75-branch inventory and latest coverage checked: no original heads changed. Baseline remains read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Completed correction

CvPlayer::initOtherData, CvGameCoreDLL/CvPlayer.cpp:159–165, inside the existing XANA 02-14-2026 FfH Faction Alignment block. The ALIGNMENTS_DO_NOT_DECAY branch passed only four arguments to AlignmentScore: baseHigh, baseLow, MAX_ALIGNMENT_POINTS, ALIGNMENTS_LIGHT_DARK_INDEPENDENT.

The actual constructor in AlignmentScore.h:9–25 takes baseHigh, baseLow, highDecay, lowDecay, maxDelta, independent. The short call therefore puts the configured point cap into highDecay and the boolean independence flag into lowDecay. maxDelta remains MAX_INT and independent remains false. Consequently a nondecaying axis configured with a finite cap or independent positive/negative channels silently loses those settings.

Pass 100,100 before the existing point cap and independence argument. AlignmentScore::decay at AlignmentScore.cpp:80–90 uses per100 factors, so 100 represents neutral retention if decay is invoked. The ordinary decaying branch already supplies all six arguments and is unchanged. No new metadata, cap, or coupling policy is invented; use the two configured values in their intended constructor positions. Enclosing XANA markers and all other source are preserved.

## Verification and limits

tests/alignment-arithmetic/init-check.cpp embeds the actual initialization branch, complete AlignmentScore class header (only pragma once omitted for embedding), actual bounded-change helper and both temporary alignment mutators. Metadata/stability queries and AlignmentValue storage defaults are stand-ins; test access exposes private fields solely to inspect parameter binding.

80 cases passed: both decay modes, both independence flags, limits 0/1/5/100/INT_MAX and changes 0/1/10/100. Assert base values, stored retention factors, cap and independence, plus positive/negative channel writes. Restoring the original call fails its configuration assertion.

Compiler flags: g++ -std=c++03 -Wall -Wextra -Werror -Wno-reorder -pedantic -fsanitize=address,undefined. The existing class initializer order differs from declaration order; its unrelated reorder warnings are suppressed in this scoped fixture, not repaired or claimed warning-free. Leak detection disabled as unsupported. This does not compile full CvPlayer, real metadata/XML, decay execution, engine turn scheduling, saved alignment configuration or the DLL.

Earlier arithmetic/aggregation fixes remain unchanged. Persistent head/count validity, fixed-point decay consumers, real initialization/turn/cache behavior and coherent whole-feature native validation remain outstanding. Partial draft uses [skip ci]; no DLL run triggered.
