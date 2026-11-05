# Observer allocation policy correction draft — November 4, 2026

Source: [ObserverMCP-ChatGPT at dd9c176e8f799dfe414bb19b800f4829cc369715](https://github.com/SuperXANA/AdvCiv/blob/dd9c176e8f799dfe414bb19b800f4829cc369715/CvGameCoreDLL/CvObserver.cpp).

OBS-POLICY-20261104-01: start() uses explicit try/catch (...), contrary to the repository review's no-explicit-exception-handlers requirement. Successful compilation does not close this policy finding.

Proposed replacement for the allocation/handler block, with <new> included after the existing PCH include:

```cpp
g_transport = new (std::nothrow) CvObserverTransport(config);
if (g_transport == NULL)
{
    FAssertMsg(false, "Observer transport allocation failed");
    OutputDebugStringA("ObserverMCP: allocation failed; disabled until reset.\n");
    return;
}
if (!g_transport->start())
{
    delete g_transport;
    g_transport = NULL;
    OutputDebugStringA("ObserverMCP: transport start failed; disabled until reset.\n");
    return;
}
```

This is a review draft, not an applied production correction. The reviewed CvGameCoreDLLDefNew.h has its historical new macro commented out. The transport constructor embeds the queue and two critical sections; std::nothrow addresses allocation failure only and does not establish initialization-failure behavior for those members. Check that boundary with the supported native environment and preserve matched allocation/deallocation before adoption. No new explicit exception handler is proposed.

The existing validation report records tested implementation c68a89f633a817efd7d69d70dcca0a89c6703014 and run 41788851432 passing four native configurations, with executed Windows standalone tests in enabled jobs. This pass read that report; it did not re-download its artifacts. The draft has no native validation and does not inherit the existing run's result. Actual Civ4/SSH/save-reload verification remains open.
