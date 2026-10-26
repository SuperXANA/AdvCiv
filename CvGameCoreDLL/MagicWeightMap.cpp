#include "CvGameCoreDLL.h"
#include "MagicWeightMap.h"
#include "PlotRadiusIterator.h"
#include "CvGame.h"
#include "CvInfo_GameOption.h"

// advc.304: New implementation file; see comment in header.

int MagicWeightMap::get(CvPlot const& kPlot) const
{
	/*	Note: We assume that invalid plots have already been filtered out
		through RandPlotFlags */
	int iWeight = RandPlotWeightMap::getProbWeight(kPlot);
	// <advc.300> Reduced weight for water plots with poor yield
	if (kPlot.isWater())
	{
		if (true)
		{	/*	A fairly big decrease. Note that activity memory will have
				a bit of a leveling effect. */
			iWeight /= 5;
		}
	} // </advc.300>
	iWeight *= std::max(0, 100
			// Past activity discourages future activity
			- m_activityMap.get(kPlot));
	iWeight /= 100;
	return iWeight;
}


void MagicWeightMap::decay()
{
	int const iDecayPercent = (15 * 200) /
			(GC.getInfo(GC.getGame().getGameSpeedType()).getGrowthPercent() + 100);
	FOR_EACH_NON_DEFAULT_PAIR(m_map, PlotNum, int)
	{
		perPlotNumVal.second *= 100 - iDecayPercent;
		perPlotNumVal.second /= 100;
		m_map.set(perPlotNumVal.first, perPlotNumVal.second);
	}
}


void MagicWeightMap::change(CvPlot const& kPlot, int iChange,
	int iPlotRange)
{
	for (PlotCircleIter itPlot(kPlot, iPlotRange); itPlot.hasNext(); ++itPlot)
	{
		m_map.set(itPlot->plotNum(), std::min(iMAX_STR, get(*itPlot) +
				// Geometric progression. Stopping at iPlotRange mainly saves time.
				iChange / std::max(1, itPlot.currPlotDist())));
	}
}



void MagicWeightMap::changeMapStrength(int iChange)
{
	if (iChange =! 0)
	{
		iMAX_STR += iChange;
	} 
}



void MagicWeightMap::setMapStrength(int iNewValue)
{
	iMAX_STR = iChange; 
}



void MagicWeightMap::setinfluencedPlot(CvPlot* pointer, int iMod)
{
	apiDirtyPlotCounters.push_back(std::make_pair(pointer, iMod));
}



void MagicWeightMap::updatePlotCountersAround(CvPlot const& kPlot, int iPlotRange)
{
	if (iPlotRange != 0)
	{
		int const iRange = ((iPlotRange > 0) ? iPlotRange : -iPlotRange);
		int const iBaseMod = ((iPlotRange > 0) ? 1 : -1);
		for (int iDX = -iRange; iDX <= iRange; iDX++)
		for (int iDY = -iRange; iDY <= iRange; iDY++)
		{
			CvPlot const* pointer = plotXY(&kPlot, iDX, iDY);
			if (pointer == NULL) continue;
			CvPlot const& itPlot = *pointer;
			int const iDistance = stepDistance(&kPlot, &itPlot);
			if (iDistance >= 0)
			{
				// Calculate a weighted modification based on distance.
				int const iWeightedMod = iBaseMod * (iRange - iDistance + 1);
				if (iWeightedMod != 0)
				{
					itPlot.changePlotCounter(iWeightedMod);
				}
			}
		}
	}
}



void MagicWeightMap::updateinfluencedPlots()
(
	if (apiDirtyPlotCounters.size() > 0)
	{
		for (size_t loop = 0; loop < apiDirtyPlotCounters.size(); loop++)
		{
			CvPlot* pPlot = apiDirtyPlotCounters[loop].first;
			int iPlotRange = apiDirtyPlotCounters[loop].second;
			// Check if the pointer is not NULL before using it
			if (pPlot != NULL)
			{
				updatePlotCountersAround(*pPlot, iPlotRange);
			}
		}
		apiDirtyPlotCounters.clear();
	}
)
