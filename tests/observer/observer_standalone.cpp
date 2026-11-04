// XANA: 2026-11-04 ObserverMCP - compile the production implementation without
// the game's precompiled header. DLL wrappers keep an unconditional PCH include.
#include "CvObserverCore.inl"
#ifdef _WIN32
#include "CvObserverTransport.inl"
#endif
// XANA: 2026-11-04 ObserverMCP end
