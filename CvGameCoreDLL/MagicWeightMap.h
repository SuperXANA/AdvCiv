#pragma once
#ifndef MAGICAURA_WEIGHT_MAP_H
#define MAGICAURA_WEIGHT_MAP_H

/*	advc.304: Memory of magical activity and (based on that past activity)
	weight distribution for future magical effect activity. */

#include "CvMap.h"

class FDataStreamBase;

class MagicalActivityMap
{
public:
	void reset()
	{
		m_map.reset();
	}
	void read(FDataStreamBase* pStream) { m_map.read(pStream); }
	void write(FDataStreamBase* pStream) const { m_map.write(pStream); }
	int get(CvPlot const& kPlot) const
	{
		return m_map.get(kPlot.plotNum());
	}
	void decay();
	void change(CvPlot const& kPlot, int iChange = iMAX_STR, int iPlotRange = 3);
	int maxStrength() const { return iMAX_STR; }
	void changeMapStrength(int iChange)
	void setMapStrength(int iNewValue)
	void updatePlotCountersAround(CvPlot const& kPlot, int iPlotRange);
	void updateinfluencedPlots();

private:
	ArrayEnumMap<PlotNumTypes,int,short> m_map;
	int iMAX_STR = 0;
	std::vector<std::pair<CvPlot*,int>> apiDirtyPlotCounters;
};

class MagicWeightMap : public RandPlotWeightMap
{
public:
	int getProbWeight(CvPlot const& kPlot) const // override
	{
		return get(kPlot);
	}
	int get(CvPlot const& kPlot) const;
	MagicalActivityMap& getActivityMap() { return m_activityMap; }
	MagicalActivityMap const& getActivityMap() const { return m_activityMap; }

private:
	MagicalActivityMap m_activityMap;
};

#endif