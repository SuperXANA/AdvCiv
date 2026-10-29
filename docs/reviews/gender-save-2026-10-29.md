# Gender counter read destination — 2026-10-29

GENDER-20261029-07. Reused GenderCounterDraft-ChatGPT6c6acaf3c23cc7692a6dba8076bb1504756f1f59; original80e6ec595041cf335d5437b7bedea4fcaa61622b unchanged.

CvPlayerAI::read, CvPlayerAI.cpp:23150 uses undeclared m_aiHateHateCounter. Change only that destination to m_aiHateGenderCounter, matching actual member, allocation/reset/destructor and write at23360. Favorite/hate array ordering and stream size unchanged. Existing XANA blocks retained.

Verification: actual two array-write and two array-read statements extracted into strict C++03/ASan/UBSan fixture with MAX_PLAYERS3 and integer-vector stream stub. Distinct values in each array round-trip and a following sentinel is preserved; full stream consumed. Local execution available again for this check. No full CvPlayerAI methods, binary engine stream, old saves, MSVC DLL or game validation claimed.

Important remaining boundary: writer retains uiFlag22 (line23322), despite adding counter fields relative to baseline's existing version22. This fix removes a compile error only; it does not establish backward save compatibility. A coherent version/migration pass across affected player state is required; do not infer compatibility from isolated fixture. No native build triggered for partial save-integration draft; [skip ci].
