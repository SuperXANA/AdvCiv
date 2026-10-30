# UWAI report-name character type — 2026-10-30

Finding UWAI-20261030-03. Source LeaderSpecificUWAIAspectWeights at d38c565a981984a7c34417a9d9529fec2bcd7165; reused UWAIWeightsDraft-ChatGPT parent 1664ab256e5ef0620a85dcec899b77d02df6b012. Pinned read-only baseline 5970334b64a875b5cdb370c94fc9a98db4eacda6. Full 75-branch inventory found no changed original heads against the latest global ledger.

## Correction

- CvGameCoreDLL/UWAI.h:67, UWAI::aspectName: return wchar const*, matching actual baseline CvInfo_Base.h:49 getDescription. Returning that pointer as char const* is not a C++03 conversion and prevents compilation.
- CvGameCoreDLL/WarUtilityAspect.cpp:165–176, WarUtilityAspect::aspectName: explicitly Copy the wide description into the existing static CvString before either return path. The external report interface remains char const*, matching the actual %s logging consumers in evaluate at lines 86 and 92. Muted reports return the unformatted converted string; active reports retain the existing underscore/mixed-case formatting. Do not return a pointer into a temporary converted string. XANA markers and earlier assistant corrections are preserved.

Read actual UWAI.h/UWAI.cpp, WarUtilityAspect.h/.cpp and baseline CvInfo_Base.h, CvString.h/.cpp. Baseline CvString supports Copy(wchar const*), while implicit wide-string assignment is deliberately disabled. No weight, override, RNG or gameplay rule changed.

## Verification and limits

tests/uwai-report/check.cpp contains the actual revised two method definitions with reduced engine interfaces. Strict C++03 -Wall -Wextra -Werror -pedantic and ASan/UBSan passed 98 sequences (294 returned-string comparisons): seven ASCII descriptions, both mute states, multiple aspect IDs, repeated calls and changed metadata. Wide metadata accessor pointer identity was also checked. Restoring the original methods/signature reproduces the cannot-convert-wide-pointer-to-narrow-pointer return error. Leak detection disabled as unsupported; no leak claim.

The conversion is an ASCII-only stub, not the actual CvString::Copy implementation, MSVC runtime formatting, full classes, engine rendering or full DLL. Actual baseline Copy uses sprintf %S and documents non-ASCII limitations; this refinement does not certify localization safety, multibyte buffer sizing or signed-char case conversion. The static buffer retains the baseline single-buffer/non-reentrant lifetime contract. Invalid IDs still rely on existing assertions; release-mode missing-metadata behavior remains outstanding.

This incomplete integration draft uses [skip ci]; no DLL build was triggered or claimed. Remaining scopes: enum/global/XML/cache integration, fixed-point consumers, zero override policy, invalid IDs and non-ASCII reporting. Existing UWAI-01/02 findings are retained without repeating their work.
