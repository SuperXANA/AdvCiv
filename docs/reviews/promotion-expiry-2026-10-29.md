# Promotion expiry control flow — 2026-10-29

Source PromotionTimedExpireTurns at 5f0e1235780e19a81a09aba91234bb0487489fcf. Baseline read only, unchanged at 5970334b64a875b5cdb370c94fc9a98db4eacda6.
Existing assistant branch inventory checked: no branch for this feature existed.

EXPIRY-20261029-01: CvUnit::applyEvent, original CvUnit.cpp:11718–11729.
The original one-line promotion guard did not enclose the XANA expiry block. The expiry local iExpireTurn was then used outside its lexical scope, and the setter was unconditional even when the event used NO_PROMOTION. Enclose promotion application and expiry processing within the valid-promotion guard; keep the setter inside the nonzero-duration scope. Zero duration leaves the normal promotion metadata timing untouched; positive durations retain existing train-percent scaling and absolute-turn calculation.

EXPIRY-20261029-02: CvUnit::doExpireTempPromotions (721–736) calls getPromotionExpireTurns at 728, but the declared getter is singular getPromotionExpireTurn (CvUnit.h:1077). Correct the call and declare doExpireTempPromotions alongside the other XANA expiry methods (header:1082). No per-turn scheduling change.

Verification: actual revised applyEvent promotion/expiry block compiled and executed under strict C++03, -Wall -Wextra -Werror -pedantic, ASan/UBSan. Sixty combinations cover NO_PROMOTION/two valid IDs, durations 0–4, speeds 50/100/150/200. Assertions check promotion calls, setter calls and deadline values. Interfaces are stubs; the full applyEvent method and doExpireTempPromotions are not compiled by this fixture. No full DLL/MSVC/game result claimed.

Remaining: zero in the expiry map can currently mean no scheduled expiry yet is treated as an elapsed deadline in doExpireTempPromotions; infinite event durations are scaled as signed durations rather than handled like the promotion metadata's -1 sentinel. These need a separate coherent semantics/persistence pass. Absolute-turn arithmetic range, member lifecycle, map serialization/version compatibility, info/XML schema and text paths remain unverified. No invented save format or new expiry policy in this draft. CI skipped.
