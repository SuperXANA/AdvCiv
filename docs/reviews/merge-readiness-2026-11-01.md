# Assistant branch merge readiness — 1 November 2026

No whole-branch merge is certified by this pass. No user-owned branch or baseline was modified. This is a structural audit of all 34 extant mapped assistant/source pairs, with targeted actual-code review of CodeMacroHelpers and SidSays. Prior source/build coverage is retained; it is not newly re-executed evidence.

## New integration findings

### MERGE-20261101-01: unrelated histories and build overlays

Ten pairs have no merge base: CityBonusDiplomacyBuild, CodeMacroHelpersBuild, ColonyLeaderBuild, FamilyRelationsBuild, FreePromotionLoaderBuild, LeaderTeamSizeBuild, PromotionXPBuild, RenegadeDiplomacyBuild, SerializationHelpersBuild and UnitCombatUpgradeBuild (all ending -ChatGPT). A normal Git merge cannot proceed across these unrelated histories. Do not force unrelated-history merging to transfer the feature. Other pairs have a common ancestor but still carry hundreds of complete-baseline files. Counts below describe endpoint trees, not a simulated merge result or inevitable deletion list.

CodeMacroHelpersBuild at 9d550b45636f342480d0adc113c769910e40f96f contains 872 assistant-only paths relative to user d9908667cdc5fddef11a49e3864dfad1ecc47e92; 862 are byte-identical to pinned 1.14. The source README is absent from the assistant endpoint. Preserve it during any scoped transfer. Only three existing source paths differ; see the machine-readable audit.

Actual code reviewed: CvMemoryManager.h lines 25–44 forwards the two-dimensional delete macro to a pointer-reference helper; CvGlobals.h lines 982–1027 owns the proxy string and preserves optional-name sentinels. The forward declaration and out-of-class accessor definition must travel with the proxy correction. These changes contain no explicit try/catch/throw. Transfer the coherent changed header hunks, retaining XANA annotations; the build workflow, baseline assets and unrelated documentation are not required feature code. No claim of arbitrary allocation-failure recovery is made.

Prior native evidence: tested 63a04fb1f1f4f03f30cfb995e4f5bf3afd218c46, run https://github.com/SuperXANA/AdvCiv/actions/runs/41274710844. Existing report records Release/Debug MSVC7.1 success and inspected Build.log artifacts. This pass read that report; it did not download or revalidate the artifacts.

### MERGE-20261101-02: file-preservation gates are feature-specific

The source-only paths in JSON must be considered deliberately. README files should be retained. UnitCombatUpgrade source DLL/PCH/log files are historical build outputs, not code required by a scoped transfer. UWAI old GameInfos XML paths reflect the previously reviewed move to the actual loader GameInfo path; do not resurrect the old paths automatically. ReputationWindow removes CvAIVectorMemory.cpp/.h from the assistant endpoint; that unfinished feature remains blocked by its documented source implementation contract. An endpoint omission is not proof that a normal merge deletes the file.

### MERGE-20261101-03: SidSays completion must remain qualified

User SidSaysPatch 9a554540240cbe5b57a6a58e5b228e0a881b31c7 and assistant be355c9ea45072238bd0df8ac0db67c1e7cbbf0b diverge after their common ancestor. The newer user changes add authored XML/text content; the prior CvGame hook is preserved in the assistant endpoint. Actual SelfMod.cpp lines 438 onward implement SidSaysLocator: bounded read-only PE32 inspection and candidate logging. patchSidSays at lines 658 onward claims the discovery attempt and calls inspect; it performs no attribution string replacement. CvGame.cpp lines 629–632 reset discovery only outside construction; lines 2871–2878 invoke it after game/map readiness. Keep SelfMod.cpp, SelfMod.h and the CvGame hook together. Text asset incorporation does not establish EXE patch completion or live XML loading. Existing read-only behavior is already documented; this pass adds its transfer-readiness disposition, not a newly discovered runtime defect.

## Per-branch audit

Assistant names below omit the -ChatGPT suffix. Added counts are paths present only in the assistant endpoint, followed by those identical to baseline. The exact commits, changed existing paths, source-only paths and inherited integration gates are recorded in merge-readiness-2026-11-01.json. Native statuses are retained ledger evidence, not new builds.

| Assistant | User source | Assistant head | Common ancestry | Added / baseline-identical | Retained native status |
|---|---|---|---|---:|---|
| AISurvivorSQLiteBuild | AISurvivorStatTracking | 3520c1e04d | yes | 887 / 868 | linked_build_commit_passed |
| CityBonusDiplomacyBuild | CityBonusLeaderDiplomacyModifiers | b7cdc0447e | **no** | 871 / 865 | linked_build_commit_passed |
| CodeMacroHelpersBuild | CodeMacroHelpers | 9d550b4563 | **no** | 872 / 862 | exact_overlay_Release_Debug_passed_all_artifacts_logs_hashes_symbols_verified |
| ColonyLeaderBuild | LeaderSpecificColonySplitVassal | d3c5e6aeb2 | **no** | 869 / 866 | linked_build_commit_passed |
| EquipmentGatesDraft | FFHEquipmentTypes | 1fc3d59b08 | yes | 3 / 0 | draft_only_no_dll_build |
| FamilyRelationsBuild | LeaderFamilyRelations | 56e2a1c319 | **no** | 870 / 863 | historical_runner_success_related_binaries_and_Debug_symbols_verified_missing_Build_log_and_source_hashes |
| FFHSpellCreationBuild | FFHSpellTypes | 9c7ff06e4c | yes | 753 / 743 | recorded_historical_build_failure |
| FreePromotionLoaderBuild | PerUnitCombatFreePromotionTraits | cd3316f9b4 | **no** | 867 / 864 | linked_build_commit_passed |
| GenderCounterDraft | GenderSpecificDiplomacy | db3c3e16df | yes | 16 / 0 | scoped_gender_fixtures_and_versioned_ai_stream_region_only_no_dll |
| LeaderTeamSizeBuild | LeaderSpecificTeamSizeAttitude | a2f0110068 | **no** | 871 / 868 | linked_build_commit_passed |
| LLMDiplomacyTextBuild | LLMDiplomacyTextGeneration | 0d76c106aa | yes | 871 / 859 | linked_build_commit_passed |
| PartnerDiplomacyBuild | PartnerLeaderCivSpecificDiplomacyText | 4f38c94e22 | yes | 877 / 864 | linked_build_commit_passed |
| PartyWrapperDraft | CvPartyGroup | 85e2d6f28e | yes | 3 / 0 | draft_only_no_dll_build |
| PlotTimerDraft | LeaderCivilizationVariantMechanics | fea29629a5 | yes | 12 / 0 | not_built_exact_source_head_inconsistent_axis_metadata |
| PromotionXPBuild | PromotionAltersUnitXPValues | 9230eeb926 | **no** | 868 / 865 | linked_build_commit_passed |
| RaceDemographicsDraft | FFHRaceTypes | 45256362fe | yes | 8 / 0 | draft_only_no_dll_build |
| RenegadeDiplomacyBuild | LeaderSpecificRebelliousTeamDiplomaticDecisions | 6660adfd28 | **no** | 875 / 867 | linked_build_commit_passed |
| SerializationHelpersBuild | SerializationHelpers | bea54776ac | **no** | 877 / 871 | linked_build_commit_passed |
| SidSaysDiscoveryBuild | SidSaysPatch | be355c9ea4 | yes | 882 / 867 | Release_Debug_build_logs_sources_binaries_and_matching_Debug_symbols_verified |
| SummonCatchupDraft | LeaderCivilizationSummoningRandomEvents | 9408469df1 | yes | 15 / 0 | not_built_missing_unit_and_triggered_event_integration |
| UnitCombatUpgradeBuild | PerUnitCombatUpgradeCostModifers | cb5e560613 | **no** | 865 / 863 | linked_build_commit_passed |
| VoteCounterDraft | LeaderSpecificVoteActionDiplomacy | a4bf7f3e45 | yes | 881 / 865 | corrected_overlay_release_debug_passed_artifact_Build_logs_inspected |
| ReputationWindowDraft | RealisticAIDecisions | 1ae7ec4015 | yes | 18 / 0 | not_built_changed_head_missing_memory_implementation |
| CivicScrollDraft | UniqueCivicsReligions | a7a1290aa2 | yes | 868 / 848 | failed_native_missing_user_unhappiness_timer_implementation_no_DLL |
| SimpleStorageChangeDraft | FSimpleDataStorage | d9571efb9c | yes | 20 / 0 | complete_header_cpp03_fno_exceptions_ASan_UBSan_no_DLL |
| HatedDiplomacyDraft | HatedCivicReligionDiplomacy | a13d837a06 | yes | 877 / 861 | latest_diagnostic_only_head_not_built_prior_exact_DLL_results_retained |
| FirstImpressionDraft | FirstImpressionDiplomacyModifiers | dd773ace6f | yes | 876 / 867 | exact_overlay_release_debug_passed |
| PreferenceFrameworkDraft | LeaderCivilizationDecisionPreferences | 5012475e85 | yes | 19 / 0 | actual_record_helper_cpp03_fno_exceptions_ASan_UBSan_only_no_DLL |
| CityPopulationDraft | CityPopulationTrait | f159c2c47d | yes | 4 / 0 | extracted_Cpp03_fixture_only |
| UWAIWeightsDraft | LeaderSpecificUWAIAspectWeights | f1d3125c0f | yes | 873 / 860 | release_debug_corrected_overlay_passed |
| PromotionExpiryDraft | PromotionTimedExpireTurns | 45dabe719c | yes | 875 / 862 | exact_overlay_release_debug_passed |
| PromotionHPDraft | PromotionAltersUnitHPValues | 185a4a161d | yes | 874 / 867 | exact_overlay_release_debug_passed_artifact_logs_inspected |
| FavoriteUnitCombatDraft | LeaderSpecificFavoriteUnitCombats | 7e5e7a04a8 | yes | 877 / 868 | exact_overlay_release_debug_passed |
| DynamicRankDraft | LeaderSpecificDynamicRankBonusDiplomacy | 6173663f4e | yes | 876 / 867 | fractional_overlay_release_debug_passed_artifact_Build_logs_inspected |

## Disposition

No additional overlapping assistant branches require consolidation in the current 75-head inventory. Historical SQLite/spell consolidations remain recorded; their retired branches are absent and were not recreated. Missing implementation skips remain in force, including UnitStatusEffects. No DLL or workflow was changed and no build was triggered for this documentation audit. Do not treat partial reviews or prior successful overlays as whole-feature gameplay/save/XML certification. Remaining integration work is preserved in the existing ledger rather than marking the global stop gate satisfied.
