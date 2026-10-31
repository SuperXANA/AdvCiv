# Organization defaults and reader completion — 2026-10-30

ORGLOAD-20261030-03/04/05. Read-only source UniqueCivicsReligions `d0fc7c0f93320e112903416c17bb2a2030819d60`; reused CivicScrollDraft-ChatGPT parent `bfcc3e0c5dd41a9888397f4256f4242b425fb949`. Baseline 1.14 remains read-only at `5970334b64a875b5cdb370c94fc9a98db4eacda6`. Fresh 75-branch inventory found no changed original heads against the global ledger at afb7f7ce941698df0c904a233c1120dacb177970. Prior pass-3, civic UI and readiness reports checked before review. Read the complete organization header/implementation and baseline XML boolean defaults.

[Correction and regression fixture 77b17aadc2177843c7a093834268c3a37beb31a9](https://github.com/SuperXANA/AdvCiv/commit/77b17aadc2177843c7a093834268c3a37beb31a9).

## Completed corrections

ORGLOAD-20261030-03: CvOrganizationInfo::CvOrganizationInfo, CvInfo_Organization.cpp:16. Initialize m_bMinorOrganization to false, following its declaration order after the civilization/leader prerequisites. Previously the inline isMinorOrganization() getter read an indeterminate bool before a successful XML read, including after an early base-read failure. The baseline CvXMLLoadUtility.h GetChildXmlValByName(bool*,...) default is already false for an omitted field; the constructor now has the same deterministic initial default. Explicit XML boolean parsing is unchanged.

ORGLOAD-20261030-04: CvHybridOrganizationInfo::read, CvInfo_Organization.cpp:445. Return true after the existing five successful field reads. Previously the bool function fell off the end when CvOrganizationInfo::read succeeded, yielding undefined behavior and no reliable status for its caller. Its existing false-return path after base failure is unchanged.

ORGLOAD-20261030-05: CvReligionInfo::read, CvInfo_Organization.cpp:224. Declare the local CvString szTextVal before its existing HybridOrganization lookup/staging. The original method uses this name without any declaration in scope and cannot compile. The staging operation/tag/order are unchanged.

Original XANA blocks and prior fixes remain. Three new line annotations identify these corrections. No XML tags, hybrid spread/founding mechanics, data layout, save format or prerequisite-resolution policy is invented.

## Verification

Run `python tests/organization-load/check.py`. The fixture extracts the actual complete CvOrganizationInfo and CvHybridOrganizationInfo declarations, actual constructors, hybrid destructor, base getChar getter and both complete read bodies. CvHotkeyInfo, XML calls, strings and category-ID interfaces are stand-ins. Category IDs use int aliases, so this test deliberately does not certify unrelated int-to-enum getters. The complete actual CvReligionInfo::read body is also compiled in a reduced religion shell with array initialization/XML interfaces stubbed; its actual constructor and other religion methods are not certified.

15,360 configurations passed strict C++03/ASan/UBSan: three prefilled memory patterns, all 512 combinations of nine optional fields, five values (-5, 0, 17, 100, INT_MAX), and successful/failed base reads. Placement construction in suitably aligned storage verifies deterministic constructor defaults without zero-initializing storage. Every configuration checks the reader's status, getters, untouched defaults/no XML calls after base failure, successful field values and existing two-string prerequisite staging/order.

Two additional reduced-shell religion cases check successful reading/staging of the third (hybrid) string and early base-failure rejection, with the three absent-commerce-list initialization paths. They do not test populated commerce XML or repeated owning-array loads.

Negative controls independently restore each original defect. Without the success return the extracted method fails compilation with “control reaches end of non-void function”. Without only the minor-flag initializer, UBSan reports “load of value 127, which is not a valid value for type bool”. Removing only the religion string declaration independently reproduces the compiler error “szTextVal was not declared in this scope”. These demonstrate code defects without engine execution.

Flags: `g++ -std=c++03 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined`; ASAN_OPTIONS=detect_leaks=0 and UBSAN_OPTIONS=halt_on_error=1. No warning suppression or leak claim.

## Remaining limits

No full organization translation unit, MSVC7.1/DLL, actual XML parser/schema/installation, engine ID category validation, full religion/corporation classes and commerce parsing, repeated staging, owning-array lifetime, pass-3 failure propagation, bindings, cache, save or gameplay validation. Prior pass-3 fixture remains separate; this test does not prove whole-feature native readiness. Int/enum metadata consistency and full religion/corporation lifecycle remain outside these scoped corrections. Hybrid gameplay mechanics were not implemented by this review.

Partial work uses [skip ci]; no DLL workflow triggered. Further integration review should reuse CivicScrollDraft-ChatGPT.
