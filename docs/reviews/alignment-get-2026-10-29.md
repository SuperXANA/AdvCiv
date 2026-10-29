# Wide alignment query aggregation — 2026-10-29

Existing ReputationWindowDraft-ChatGPT head 3975b09ca3ffd4393dece6ae11bf12134b2a54fa reused. Original RealisticAIDecisions remains f7cfe6fd1c1c6f19fc832352ddd01d6409c08b4e.

ALIGNMENT-20261029-02: AlignmentScore::get(), AlignmentScore.cpp:93 onward. Original int sample sums and base+permanent additions can overflow even though each stored field is representable. Accumulate/average/add in product_int_type<int,int>::type, baseline TypeChoice.h's existing signed __int64 type. Clamp only final results to MIN_INT..MAX_INT, preserving averaging and cancellation before conversion. Ten int samples fit this wide range; no class layout or save format change.

Verification: actual revised method and actual class header compiled under strict C++03/ASan/UBSan across 5,390 combinations: count0..10, head0..9, seven extreme/base values for each axis. Circular samples and independent long-width reference expected values checked. Fixture uses 64-bit Linux long as stand-in for baseline product_int_type; asserts width>=8. Existing constructor reorder warning suppressed. Private visibility exposed for test state setup; no engine dependencies. Restoring original method produces UBSan signed-overflow failure. No native MSVC7.1/DLL/game result; partial draft [skip ci].

Baseline TypeChoice.h was read and confirms product_int_type<int,int>::type is signed __int64, included by CvGameCoreDLL.h. Not a new dependency. Invalid persisted count/head validation and decay arithmetic remain out of scope.
