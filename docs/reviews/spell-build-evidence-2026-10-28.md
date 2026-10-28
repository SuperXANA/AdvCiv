# Spell build evidence consolidation — 2026-10-28

This records an existing unresolved build result, not a new code finding or a new build attempt. No production source changed.

## Exact evidence

- Branch FFHSpellCreationBuild-ChatGPT, current head 581063899df1123d0a4e45f43ef1e5b346457701.
- [Run 40402742595](https://github.com/SuperXANA/AdvCiv/actions/runs/40402742595), head SHA matches, completed failure.
- [Job 121852587193](https://github.com/SuperXANA/AdvCiv/actions/runs/40402742595/job/121852587193), build-dll.
- Compiler log at 2026-10-26T21:15:12Z: CvPlot.h(988): error C2027: use of undefined type boost::STATIC_ASSERTION_FAILURE<x>.
- Follow-on NMAKE U1077 and MSBuild MSB3073 report the compiler process failure. The MSBuild summary has 0 warnings / 3 errors, including wrapper failures; this does not mean three distinct C++ source defects.
- Artifacts endpoint returned 0 artifacts for this run. No verified DLL artifact is available from it.

The actual [CvPlot.h line 988](https://github.com/SuperXANA/AdvCiv/blob/581063899df1123d0a4e45f43ef1e5b346457701/CvGameCoreDLL/CvPlot.h#L988) is:
BOOST_STATIC_ASSERT(MAX_PLOT_NUM > MAX_SHORT || sizeof(CvPlot) <= 268);

The compiler failed that assertion. The adjacent upstream comment calls this a size/optimization check and explicitly allows changing the size after considering whether growth can be avoided. It is not sufficient evidence of a mandatory EXE ABI limit. The source still has XANA magic-class combat/resist maps at lines 949–950 and a plot counter field at lines 909–911. Their presence was confirmed by reading the actual header. This record does not calculate target sizeof(CvPlot), establish the entire size delta, propose disabling the assertion, or claim that moving only those fields resolves the complete branch.

## Prior work and verification limits

The actual CvStructs.h/.cpp spell-creation ownership blocks and tests/test_spell_creation.py were read. They contain existing assistant ownership, reference-return and noncopyability refinements. That fixture compiles selected structs with XML/engine stubs and explicitly excludes XML traversal and full DLL validation. It was not rerun solely to reconfirm unchanged work.

This native failure occurs before a DLL result; it does not demonstrate that the ownership refinements caused the failure, nor that all later translation units would pass once the assertion is addressed. Historical workflow provenance was not re-certified against the current authorized complete-base build procedure. The result is recorded only as an exact historical failed run.

No workflow was triggered, no failed run retried, and no new branch created. The current build head is unchanged. FFHSpellCreationFixes-ChatGPT has no Actions runs in the branch query; that is not an independent native result.

## Coverage update

Previously these three spell rows were unverified in the ledger. The build row now records the exact failed run; source/fixes rows record a related failed overlay without attributing a standalone build to their different heads.

Initial scoped rotation is complete with UnitStatusEffects deferred. Partial source scopes and failed/unverified builds remain, so the stop gate is false. The next spell pass should perform scoped code work on the existing assistant branch before a meaningful fresh native build, preserving the pinned 1.14 baseline and all original branches.
