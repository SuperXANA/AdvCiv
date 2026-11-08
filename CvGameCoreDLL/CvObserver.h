#ifndef CV_OBSERVER_H
#define CV_OBSERVER_H
#include "CvObserverConfig.h"
#ifdef CV_OBSERVER_ENABLE
// XANA: 2026-11-04 ObserverMCP - ONLY call from the owning game thread
class CvGame;
namespace CvObserver
{
	void postUpdate(CvGame const& game);
	void mapRegenerated(CvGame const& game);
	void stop(CvGame const& game);
}
// XANA: 2026-11-04 ObserverMCP end
#endif
#endif
