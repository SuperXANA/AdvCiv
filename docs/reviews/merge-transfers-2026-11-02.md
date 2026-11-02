# Scoped DLL transfer readiness — 2 November 2026

Updated the 34 assistant/source endpoint and ancestry checks against the fresh 75-head inventory. Original feature-source commits and read-only 1.14 remain unchanged; dll-build has adopted the already reviewed split preparation/build workflow. No additional overlapping assistant branches require consolidation. No user branch was merged or edited.

## Concrete transfer drafts

Five patches in transfers-2026-11-02 contain only outstanding CvGameCoreDLL changes between the pinned original source and its current assistant branch. They omit complete-baseline-only files, workflows, XML/assets, reports and tests. Each patch includes the feature's prior assistant corrections as well as its newest correction, rather than depending on an unspecified earlier patch. They are reviewable transfer drafts; no installation, runtime or whole-branch merge certification is implied.

For each draft, an isolated Git index started from the **exact original source commit**. Both git apply --cached --check and actual cached application passed. Every non-DLL path remained byte-identical to that source. Overlaying the resulting DLL files on complete 1.14 reproduced every blob in the equivalent baseline-plus-current-assistant DLL tree. All four previously built targets also matched their recorded tested DLL trees exactly. The source branch itself was never checked out for modification or advanced. Do not apply a patch blindly after its source head changes; re-evaluate overlapping user edits.

| Transfer draft (all assistant names end -ChatGPT) | Original source commit | Assistant snapshot | Changed DLL files | Result |
|---|---|---|---:|---|
| [ColonyLeaderBuild](transfers-2026-11-02/ColonyLeaderBuild-ChatGPT.patch) | `c2c8690c4854482f98ea3ceae2974586e5d1503d` | `7ecb44c226cb1e165d65419832dcb14a8a3d0dd4` | 3 | Exact recorded native DLL tree |
| [HatedDiplomacyDraft](transfers-2026-11-02/HatedDiplomacyDraft-ChatGPT.patch) | `a9c1a754b5e9b64e10ceaa22fd02fa78f3718785` | `de790fd226e6768ca83abb3ed1c428a6f9e2b6c0` | 3 | Exact recorded native DLL tree |
| [UWAIWeightsDraft](transfers-2026-11-02/UWAIWeightsDraft-ChatGPT.patch) | `d38c565a981984a7c34417a9d9529fec2bcd7165` | `21e4baf145aef96e95f3c17a7e45ba638bad2725` | 7 | Exact recorded native DLL tree |
| [GenderCounterDraft](transfers-2026-11-02/GenderCounterDraft-ChatGPT.patch) | `80e6ec595041cf335d5437b7bedea4fcaa61622b` | `f127d03db270afba4c72f0df764b3ec6dec002ff` | 9 | Exact recorded native DLL tree |
| [PreferenceFrameworkDraft](transfers-2026-11-02/PreferenceFrameworkDraft-ChatGPT.patch) | `aac03388283a5ac316f6a19f6e3754a7435b6511` | `61c5ae3119e06b97098e7ccd3c629f06b61b5b39` | 8 | Source draft; full DLL gate remains |

The manifest records patch SHA256, exact changed paths, source/assistant commits, matched blob counts, tested commits and existing run links. These are content/application checks, not fresh compiler or runtime tests. Existing run statuses were freshly confirmed as completed/success on their exact tested commits. Previously recorded artifact Build.log/manifest/binary verification was consulted; those ZIPs were not downloaded again in this pass.

## Transfer constraints confirmed in actual code

| Branch and code | Required coherent transfer | Remaining integration gate |
|---|---|---|
| Colony: CvInfo_Civilization.cpp:1088–1096, readPass2 | Keep explicit optional DerivativeLeader loading and the associated declaration/consumer changes captured by the three-file patch. The existing base helper treats prior index zero specially; replacing this code with its old call reintroduces the omission problem. | Installed modular XML, actual colony eligibility/selection and UI remain unexecuted. |
| Hated religion: CvPlayer.cpp:9449–9461, setLastStateReligion | Transfer the observer refresh together with the feature metadata getter/attitude consumer. Religionless observers with a hated religion must still invalidate both attitude directions on conversion. | Actual conversion and diplomacy UI behavior; no new mechanics policy supplied. |
| UWAI: UWAI.h:62–74 and CvInfo_Civilization.cpp:661 onward | Keep explicit release-mode invalid-index returns alongside assertions and the matching enum/info registration/loader changes. Assertions alone are insufficient protection. | The DLL-only patch does **not** install XML. Preserve the corrected assistant Assets/XML/GameInfo/CIV4WarUtilityAspectAIInfos.xml and matching active schema changes; do not restore the old GameInfos directory. Actual engine parser/default/localization/game evidence remains separate. |
| Gender: CvEnumMacros.h:167 onward; CvPlayer.h/CvPlayer.cpp and associated interfaces | Retain the basic-info alias and reconciled 1.14 count widths/stream logic together. The patch includes all outstanding source changes, including earlier scoped counter/UI/metadata fixes. Whole-file source differences include documented baseline restoration, not newly designed Gender behavior. | External basic-info schema and localization installation, new-game play/save/reload, UI/gameplay remain unverified. |
| Preferences: CvInfo_Civilization.cpp:1575, CvInfo_RandomEvent.cpp:2110, CvInfo_Unit.cpp:2568 | All three explicit copy declarations and implementations must travel together, retaining deep owning-map copies and default construction of the base. Actual 1.14 CvInfo_Base.cpp:9–12 has an unsupported copy constructor; do not reintroduce base_t(kOther). | This patch is **not DLL-certified**. Missing Event/Unit preference assets and Unit schema remain the exact-source implementation gate. No XML profiles or schema were fabricated. |

These constraints reference existing corrected findings, not new defect reports. Actual changed code and the baseline constructor contract were read in this pass. No new production C++ was needed or introduced, and no exception constructs were added. XANA annotations in the current assistant snapshots are retained exactly by the patches.

## Existing native evidence associated with the transfer drafts

| Transfer | Exact tested DLL commit | Existing successful run |
|---|---|---|
| ColonyLeaderBuild-ChatGPT | `0f66179997115e5c4c49715033f643fe282dd243` | https://github.com/SuperXANA/AdvCiv/actions/runs/41359029328 |
| HatedDiplomacyDraft-ChatGPT | `ebccd9c32ef9644762d280489dc3ba949832d55d` | https://github.com/SuperXANA/AdvCiv/actions/runs/41344075881 |
| UWAIWeightsDraft-ChatGPT | `b9c0c192e98a02d8003e88bf6f4e8741225a7494` | https://github.com/SuperXANA/AdvCiv/actions/runs/41402811119 |
| GenderCounterDraft-ChatGPT | `5b122549e6df54bc61bcfbb19b7482cc9bec756e` | https://github.com/SuperXANA/AdvCiv/actions/runs/41328157020 |

No new build was triggered: four DLL source trees are byte-identical to existing tested overlays, and the preference implementation gate remains. Documentation and patch artifacts use [skip ci] and live outside workflow-triggering production paths. No whole-branch merge is certified, no new bug is claimed, and no unresolved integration item is silently marked complete. Older superseded branches remain recorded and absent from the current inventory; none were recreated or deleted.

The machine-readable 34-pair audit retains every current source head and remaining integration gate. The master ledger preserves prior finding IDs, build results, exact-source skips and the user's fresh-game validation policy. Runtime-only gaps do not justify speculative DLL edits or redundant unchanged builds. Future relevant source changes and independently eligible integration work remain reviewable.
