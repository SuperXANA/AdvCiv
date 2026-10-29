# First-impression metadata continuation — 2026-10-29

Reviewed existing FirstImpressionDraft-ChatGPT b3441eda5865a7a7b7035f416eceafe4937297c4; original source cc764ad80e89f751f809998a61a23225254109f2 unchanged. Complete inventory returned 75 branches; source heads and dll-build unchanged. Known assistant documentation/code heads reconciled in ledger; no repeated builds.

No additional production correction demonstrated in this scope:
- CvInfo_Civilization.cpp:502 initializes m_piFirstImpressionModifier NULL; copy at540 allocates independent storage; destructor560 releases it.
- Cache read813–815 deletes/reallocates before reading; write924 supplies matching count/order. Actual cache stream execution and compatibility with old cache files are not certified.
- CvInfo_Civilization.h:237 declares readPass2; CvXMLLoadUtilitySet.cpp:696 enables two-pass loading for leaders, consistent with cross-leader references.
- CvInfo_Civilization.cpp:1099 loads FirstImpressionChanges after types can be registered.
- Supplied schema declares signed integer values at201 and the pair/list elements at202–207, with a LeaderHeadInfo element at318.
- AI_getFirstImpressionAttitude, CvPlayerAI.cpp:8512–8520 adds the modifier keyed by the other player's personality. Signed values preserved.
- Supplied leader XML has no FirstImpressionChanges occurrences. Do not invent custom leader values or claim demonstrated game behavior.

Prior readPass2 syntax fix remains. No new tests were needed for this read-only evaluation; previous fixture evidence is unchanged. No full DLL, engine XML/cache or in-game validation claimed. Eligible validation work remains; repository stop gate false.

Existing assistant branch reused for review documentation only; [skip ci]. No user branch modified.
