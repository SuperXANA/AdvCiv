#include "CvGameCoreDLL.h"
#include "CvPlotTempChangeMap.h"
#include "CvGame.h"

void PlotTempChangeMap::setRealTerrainType(CvPlot const& kPlot, TerrainTypes eNewValue)
{
	setRealTerrainType(kPlot.plotNum(), eNewValue);
}

void PlotTempChangeMap::setRealFeatureType(CvPlot const& kPlot, FeatureTypes eFeature, int iVariety)
{
	setRealFeatureType(kPlot.plotNum(), eFeature, iVariety));
}
void PlotTempChangeMap::setRealBonusType(CvPlot const& kPlot, BonusTypes eBonus)
{
	setRealBonusType(kPlot.plotNum(), eBonus);
}

void PlotTempChangeMap::setRealImprovementType(CvPlot const& kPlot, ImprovementTypes eImprovement)
{
	setRealImprovementType(kPlot.plotNum(), eImprovement);
}

void PlotTempChangeMap::setRealRouteType(CvPlot const& kPlot, RouteTypes eRoute)
{
	setRealRouteType(kPlot.plotNum(), eRoute);
}
void PlotTempChangeMap::setTempTerrainType(CvPlot const& kPlot, TerrainTypes eNewValue)
{
	setTempTerrainType(kPlot.plotNum(), eNewValue);
}

void PlotTempChangeMap::setTempFeatureType(CvPlot const& kPlot, FeatureTypes eFeature, int iVariety)
{
	setTempFeatureType(kPlot.plotNum(), eFeature, iVariety));
}
void PlotTempChangeMap::setTempBonusType(CvPlot const& kPlot, BonusTypes eBonus)
{
	setTempBonusType(kPlot.plotNum(), eBonus);
}

void PlotTempChangeMap::setTempImprovementType(CvPlot const& kPlot, ImprovementTypes eImprovement)
{
	setTempImprovementType(kPlot.plotNum(), eImprovement);
}

void PlotTempChangeMap::setTempRouteType(CvPlot const& kPlot, RouteTypes eRoute)
{
	setTempRouteType(kPlot.plotNum(), eRoute);
}

void PlotTempChangeMap::setTempTerrainTimer(CvPlot const& kPlot, int iNewValue)
{
	setTempTerrainTimer(kPlot.plotNum(), iNewValue);
}

void PlotTempChangeMap::setTempFeatureTimer(CvPlot const& kPlot, int iNewValue)
{
	setTempFeatureTimer(kPlot.plotNum(), iNewValue);
}
void PlotTempChangeMap::setTempBonusTimer(CvPlot const& kPlot, int iNewValue)
{
	setTempBonusTimer(kPlot.plotNum(), iNewValue);
}

void PlotTempChangeMap::setTempImprovementTimer(CvPlot const& kPlot, int iNewValue)
{
	setTempImprovementTimer(kPlot.plotNum(), iNewValue);
}

void PlotTempChangeMap::setTempRouteTimer(CvPlot const& kPlot, int iNewValue)
{
	setTempRouteTimer(kPlot.plotNum(), iNewValue);
}

void PlotTempChangeMap::changeTempTerrainTimer(CvPlot const& kPlot, int iChange)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	changeTempTerrainTimer(ePlotNum, (getTempTerrainTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempFeatureTimer(CvPlot const& kPlot, int iChange)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	changeTempFeatureTimer(ePlotNum, (getTempFeatureTimer(ePlotNum) + iChange));
}
void PlotTempChangeMap::changeTempBonusTimer(CvPlot const& kPlot, int iChange)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	changeTempBonusTimer(ePlotNum, (getTempBonusTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempImprovementTimer(CvPlot const& kPlot, int iChange)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	changeTempImprovementTimer(ePlotNum, (getTempImprovementTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempRouteTimer(CvPlot const& kPlot, int iChange)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	changeTempRouteTimer(ePlotNum, (getTempRouteTimer(ePlotNum) + iChange));
}
void PlotTempChangeMap::setRealTerrainType(PlotNumTypes ePlotNum, TerrainTypes eNewValue)
{
	m_RealTerrainTypeMap.set(ePlotNum, eNewValue);
}

void PlotTempChangeMap::setRealFeatureType(PlotNumTypes ePlotNum, FeatureTypes eFeature, int iVariety)
{
	m_RealFeatureTypeMap.set(ePlotNum, eFeature));
	m_RealFeatureVarietyMap.set(ePlotNum, iVariety));
}
void PlotTempChangeMap::setRealBonusType(PlotNumTypes ePlotNum, BonusTypes eBonus)
{
	m_RealBonusTypeMap.set(ePlotNum, eBonus);
}

void PlotTempChangeMap::setRealImprovementType(PlotNumTypes ePlotNum, ImprovementTypes eImprovement)
{
	m_RealImprovementTypeMap.set(ePlotNum, eImprovement);
}

void PlotTempChangeMap::setRealRouteType(PlotNumTypes ePlotNum, RouteTypes eRoute)
{
	m_RealRouteTypeMap.set(ePlotNum, eRoute);
}
void PlotTempChangeMap::setTempTerrainType(PlotNumTypes ePlotNum, TerrainTypes eNewValue)
{
	m_TempTerrainTypeMap.set(ePlotNum, eNewValue);
}

void PlotTempChangeMap::setTempFeatureType(PlotNumTypes ePlotNum, FeatureTypes eFeature, int iVariety)
{
	m_TempFeatureTypeMap.set(ePlotNum, eFeature));
	m_TempFeatureVarietyMap.set(ePlotNum, iVariety));
}
void PlotTempChangeMap::setTempBonusType(PlotNumTypes ePlotNum, BonusTypes eBonus)
{
	m_TempBonusTypeMap.set(ePlotNum, eBonus);
}

void PlotTempChangeMap::setTempImprovementType(PlotNumTypes ePlotNum, ImprovementTypes eImprovement)
{
	m_TempImprovementTypeMap.set(ePlotNum, eImprovement);
}

void PlotTempChangeMap::setTempRouteType(PlotNumTypes ePlotNum, RouteTypes eRoute)
{
	m_TempRouteTypeMap.set(ePlotNum, eRoute);
}

void PlotTempChangeMap::setTempTerrainTimer(PlotNumTypes ePlotNum, int iNewValue)
{
	m_TempTerrainTimerMap.set(ePlotNum, std::max(0, iNewValue);
}

void PlotTempChangeMap::setTempFeatureTimer(PlotNumTypes ePlotNum, int iNewValue)
{
	m_TempFeatureTimerMap.set(kPlot.plotNum(), std::max(0, iNewValue));
}
void PlotTempChangeMap::setTempBonusTimer(PlotNumTypes ePlotNum, int iNewValue)
{
	m_TempBonusTimerMap.set(ePlotNum, std::max(0, iNewValue));
}

void PlotTempChangeMap::setTempImprovementTimer(PlotNumTypes ePlotNum, int iNewValue)
{
	m_TempImprovementTimerMap.set(ePlotNum, std::max(0, iNewValue));
}

void PlotTempChangeMap::setTempRouteTimer(PlotNumTypes ePlotNum, int iNewValue)
{
	m_TempRouteTimerMap.set(ePlotNum, std::max(0, iNewValue));
}

void PlotTempChangeMap::changeTempTerrainTimer(PlotNumTypes ePlotNum, int iChange)
{
	m_TempTerrainTimerMap.set(ePlotNum, (getTempTerrainTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempFeatureTimer(PlotNumTypes ePlotNum, int iChange)
{
	m_TempFeatureTimerMap.set(ePlotNum, (getTempFeatureTimer(ePlotNum) + iChange));
}
void PlotTempChangeMap::changeTempBonusTimer(PlotNumTypes ePlotNum, int iChange)
{
	m_TempBonusTimerMap.set(ePlotNum, (getTempBonusTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempImprovementTimer(PlotNumTypes ePlotNum, int iChange)
{
	m_TempImprovementTimerMap.set(ePlotNum, (getTempImprovementTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::changeTempRouteTimer(PlotNumTypes ePlotNum, int iChange)
{
	m_TempRouteTimerMap.set(ePlotNum, (getTempRouteTimer(ePlotNum) + iChange));
}

void PlotTempChangeMap::update(CvPlot const& kPlot)
{
	PlotNumTypes const ePlotNum = kPlot.plotNum();
	bool const bGraphicsReady = GC.IsGraphicsInitialized();
	if (getTempTerrainTimer(ePlotNum) > 0)
	{
		changeTempTerrainTimer(ePlotNum, -1);
		if (getTempTerrainTimer(ePlotNum) == 0)
		{
			TerrainTypes const eReal = getRealTerrainType(ePlotNum);
			setRealTerrainType(ePlotNum, NO_TERRAIN);
			setTempTerrainType(ePlotNum, NO_TERRAIN);
			if (bGraphicsReady)
			{
				kPlot.setTerrainType(eReal, true, true, true);
			}
		}
	}
	if (getTempFeatureTimer(ePlotNum) > 0)
	{
		changeTempFeatureTimer(ePlotNum, -1);
		if (getTempFeatureTimer(ePlotNum) == 0)
		{
			std::pair<FeatureTypes, int> kReal = getRealFeatureType(ePlotNum);
			setRealFeatureType(ePlotNum, NO_FEATURE, -1);
			setTempFeatureType(ePlotNum, NO_FEATURE, -1);
			if (bGraphicsReady)
			{
				kPlot.setFeatureType(kReal.first, kReal.second);
			}
		}
	}
	if (getTempBonusTimer(ePlotNum) > 0)
	{
		changeTempBonusTimer(ePlotNum, -1);
		if (getTempBonusTimer(ePlotNum) == 0)
		{
			BonusTypes const eReal = getRealBonusType(ePlotNum);
			setRealBonusType(ePlotNum, NO_BONUS);
			setTempBonusType(ePlotNum, NO_BONUS);
			if (bGraphicsReady)
			{
				kPlot.setBonusType(eReal);
			}
		}
	}
	if (getTempImprovementTimer(ePlotNum) > 0)
	{
		changeTempImprovementTimer(ePlotNum, -1);	
		if (getTempImprovementTimer(ePlotNum) == 0)
		{
			ImprovementTypes const eReal = getRealImprovementType(ePlotNum);
			setRealImprovementType(ePlotNum, NO_IMPROVEMENT);
			setTempImprovementType(ePlotNum, NO_IMPROVEMENT);
			if (bGraphicsReady)
			{
				kPlot.setImprovementType(eReal);
			}
		}
	}
	if (getTempRouteTimer(ePlotNum) > 0)
	{
		changeTempRouteTimer(ePlotNum, -1);
		if (getTempRouteTimer(ePlotNum) == 0)
		{
			RouteTypes const eReal = getRealRouteType(ePlotNum);
			setRealRouteType(ePlotNum, NO_ROUTE);
			setTempRouteType(ePlotNum, NO_ROUTE);
			if (bGraphicsReady)
			{
				kPlot.setRouteType(eReal);
			}
		}
	}
}