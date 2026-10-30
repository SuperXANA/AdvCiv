# Dynamic rank native validation — 2026-10-29

Baseline5970334b64a875b5cdb370c94fc9a98db4eacda6; featuredc30163319ee795b59938417e0c4474cb5157822; workflow6343afabdc57996ea875b6e8541b69ad333d0686. Complete baseline overlay verified with zero missing base DLL files and zero feature mismatches.

Initial exact overlay558b98b64930eaf803f1ac2c4afee41216844f47 failed both Release/Debug in run40982183330 with CvPlayerAI.cpp:8686 C2975: fixp runtime expression cannot supply constant template argument. NMAKE errors propagated the compiler failure.

Fix197a968d1b24135a9c42f5f1a951bbe16903fc0e uses scaled(runtime integer expression) in AI_getShareRelativeProgressAttitude:8686. Original integer division order preserved, prior round correction retained. No formula redesign.

Run https://github.com/SuperXANA/AdvCiv/actions/runs/40982393659 passed Release123825309010 and Debug123825309279. Both logs verify MSVC7.1/_MSC_VER1310 and zero warnings/errors. Release artifact12945297909 size2353271; Debug12945433081 size18562618. DLL copy/nonempty check/uploads succeeded; artifact metadata verified, ZIPs not independently downloaded/disassembled.

Exact derivative only, not unchanged original branch. Rank normalization/truncation, threshold rank multiplier, save flag22 compatibility, actual XML/cache/game behavior remain unverified. Existing assistant branch reused; documentation followup skips CI.
