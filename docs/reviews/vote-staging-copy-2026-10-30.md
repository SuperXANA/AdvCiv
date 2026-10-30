# Updated vote staging: copy ownership — 2026-10-30

VOTE-20261030-07. Reviewed changed original LeaderSpecificVoteActionDiplomacy head 8fcfdd97329279393120aaab34c00dde84e729df, parent 4f2e7c2ea110e7859fbab1bdac32a02a27f5bb30. Current complete 75-branch inventory prioritized this original source delta. Reuse VoteCounterDraft-ChatGPT parent d9cce3faba0641b5ff84b01eb9bfcbb3c4377a5a. Baseline read-only at 5970334b64a875b5cdb370c94fc9a98db4eacda6.

## Source delta and scope

The original now stages decision text and two numeric vectors during read(CvXMLLoadUtility*) and exposes no-argument readPass3(). This removes the previous pass-3 caller signature/cursor design as the active blocker; the old skip applies only to 4f2e7c2, not this new source head. Preserve that historical record and reopen partial review.

The two changed metadata files are incorporated into the existing assistant draft as a pinned file update, not a branch merge. Other files, including the prior vote counter fixes, remain unchanged. The prior current-node GetXmlVal/syntax correction is carried to its relocated read block (revised CvInfo_Civilization.cpp:1122). The old loader fixture targets the superseded XML-argument method and does not validate this new staging design. The previous size guard must be reconsidered in the finalizer after votes are available, not copied into the early read when vote counts may still be zero.

## Committed ownership correction

CvLeaderHeadInfo copy constructor, CvInfo_Civilization.cpp:522–553; changed block:526–534. New std::vector<int> members appear in CvInfo_Civilization.h:354–355. The existing memcpy length sizeof(CvLeaderHeadInfo)-sizeof(CvInfoBase) includes these nontrivial vector objects. It shallow-copies their internal allocation pointers, allowing source and copy to mutate/free the same buffers. The inherited m_aszExtraXMLforPass3 vector (baseline CvInfo_Base.h:92) is not in that byte range and was omitted, losing staged decision names.

Retain the baseline scalar/pointer-prefix copying approach, but stop its range at the first staged derived vector. Copy the inherited text vector and both numeric vectors through ordinary vector assignment. Keep the existing allocCopy calls for all pointer arrays. This relies on the inspected layout: the two new vectors are the final nonstatic members; future nontrivial members before this boundary require revisiting the prefix strategy. A complete memberwise rewrite remains outside this scoped correction. XANA date/tag markers preserved.

## Verification

tests/vote-loader/copy-check.cpp embeds the entire revised actual copy-constructor definition and actual allocCopy behavior. A reduced class layout supplies the same named pointer fields, virtual base/text vector and the two trailing vectors; it is not the full engine class/layout. All 33 staging lengths 0–32 passed strict C++03 (-Wall -Wextra -Werror -pedantic), ASan and UBSan. Cases check staged content, independent mutation of each vector, deep copies of all 16 pointer arrays, a second-generation copy and destruction before continued source access.

The original constructor fails staged-text equality. A second negative control adding only text copying reproduces numeric-vector aliasing: changing the clone changes the source. No observed double-free is claimed from those assertion-terminating controls; shared ownership also makes destruction unsafe. Leak detection disabled as unsupported. No MSVC7.1/full DLL/game result.

## Remaining new finalizer work

The supplied readPass3 scaffold still references undefined iNumPlayerVotes instead of its declared iNumPlayerVoteTypes; array initialization is commented out before indexed writes; staged numeric lengths and final vote capacity are unchecked. GC.getInfoTypeForString is not an appropriate resolver for fixed negative PlayerVoteTypes ballot names: the established four explicit ballot strings should remain a separate domain rather than admitting an unrelated XML info such as UNIT_WARRIOR. These are recorded for continued implementation/review, not certified fixed by this ownership pass.

Do not build this incomplete draft or fabricate a keyed schema. Native review remains pending. No new skip is imposed on this changed source while its supplied staging implementation is under review. Original branch untouched; partial draft uses [skip ci].
