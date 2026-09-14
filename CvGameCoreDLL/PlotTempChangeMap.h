#pragma once

#ifndef CVPLOTCHANGEMAP_H
#define CVPLOTCHANGEMAP_H

#include "CvMap.h"

class FDataStreamBase;

class PlotTempChangeMap
{
public:
	void reset()
	{
		m_RealTerrainTypeMap.reset();
		m_RealFeatureTypeMap.reset();
		m_RealFeatureVarietyMap.reset();
		m_RealBonusTypeMap.reset();
		m_RealImprovementTypeMap.reset();
		m_RealRouteTypeMap.reset();
		
		m_TempTerrainTypeMap.reset();
		m_TempFeatureTypeMap.reset();
		m_TempFeatureVarietyMap.reset();
		m_TempBonusTypeMap.reset();
		m_TempImprovementTypeMap.reset();
		m_TempRouteTypeMap.reset();
		
		m_TempTerrainTimerMap.reset();
		m_TempFeatureTimerMap.reset();
		m_TempBonusTimerMap.reset();
		m_TempImprovementTimerMap.reset();
		m_TempRouteTimerMap.reset();
	}
	void read(FDataStreamBase* pStream)
	{
		m_RealTerrainTypeMap.read(pStream);
		m_RealFeatureTypeMap.read(pStream);
		m_RealFeatureVarietyMap.read(pStream);
		m_RealBonusTypeMap.read(pStream);
		m_RealImprovementTypeMap.read(pStream);
		m_RealRouteTypeMap.read(pStream);
		
		m_TempTerrainTypeMap.read(pStream);
		m_TempFeatureTypeMap.read(pStream);
		m_TempFeatureVarietyMap.read(pStream);
		m_TempBonusTypeMap.read(pStream);
		m_TempImprovementTypeMap.read(pStream);
		m_TempRouteTypeMap.read(pStream);
		
		m_TempTerrainTimerMap.read(pStream);
		m_TempFeatureTimerMap.read(pStream);
		m_TempBonusTimerMap.read(pStream);
		m_TempImprovementTimerMap.read(pStream);
		m_TempRouteTimerMap.read(pStream);
	}
	void write(FDataStreamBase* pStream) const
	{
		m_RealTerrainTypeMap.write(pStream);
		m_RealFeatureTypeMap.write(pStream);
		m_RealFeatureVarietyMap.write(pStream);
		m_RealBonusTypeMap.write(pStream);
		m_RealImprovementTypeMap.write(pStream);
		m_RealRouteTypeMap.write(pStream);
		
		m_TempTerrainTypeMap.write(pStream);
		m_TempFeatureTypeMap.write(pStream);
		m_TempFeatureVarietyMap.write(pStream);
		m_TempBonusTypeMap.write(pStream);
		m_TempImprovementTypeMap.write(pStream);
		m_TempRouteTypeMap.write(pStream);
		
		m_TempTerrainTimerMap.write(pStream);
		m_TempFeatureTimerMap.write(pStream);
		m_TempBonusTimerMap.write(pStream);
		m_TempImprovementTimerMap.write(pStream);
		m_TempRouteTimerMap.write(pStream);
	}
	TerrainTypes getRealTerrainType(CvPlot const& kPlot) const
	{
		return getRealTerrainType(kPlot.plotNum());
	}
	std::pair<FeatureTypes,int> getRealFeatureType(CvPlot const& kPlot) const
	{
		return getRealFeatureType(kPlot.plotNum());
	}
	BonusTypes getRealBonusType(CvPlot const& kPlot) const
	{
		return getRealBonusType(kPlot.plotNum());
	}
	ImprovementTypes getRealImprovementType(CvPlot const& kPlot) const
	{
		return getRealImprovementType(kPlot.plotNum());
	}
	RouteTypes getRealRouteType(CvPlot const& kPlot) const
	{
		return getRealRouteType(kPlot.plotNum());
	}
	int getTempTerrainTimer(CvPlot const& kPlot) const
	{
		return getTempTerrainTimer(kPlot.plotNum());
	}
	int getTempFeatureTimer(CvPlot const& kPlot) const
	{
		return getTempTerrainTimer(kPlot.plotNum());
	}
	int getTempBonusTimer(CvPlot const& kPlot) const
	{
		return getTempBonusTimer(kPlot.plotNum());
	}
	int getTempImprovementTimer(CvPlot const& kPlot) const
	{
		return getTempImprovementTimer(kPlot.plotNum());
	}
	int getTempRouteTimer(CvPlot const& kPlot) const
	{
		return getTempRouteTimer(kPlot.plotNum());
	}
	
	void setRealTerrainType(CvPlot const& kPlot, TerrainTypes eNewValue);
	void setRealFeatureType(CvPlot const& kPlot, FeatureTypes eFeature, int iVariety);
	void setRealBonusType(CvPlot const& kPlot, BonusTypes eBonus);
	void setRealImprovementType(CvPlot const& kPlot, ImprovementTypes eImprovement);
	void setRealRouteType(CvPlot const& kPlot, RouteTypes eRoute);
	
	void setTempTerrainType(CvPlot const& kPlot, TerrainTypes eNewValue);
	void setTempFeatureType(CvPlot const& kPlot, FeatureTypes eFeature, int iVariety);
	void setTempBonusType(CvPlot const& kPlot, BonusTypes eBonus);
	void setTempImprovementType(CvPlot const& kPlot, ImprovementTypes eImprovement);
	void setTempRouteType(CvPlot const& kPlot, RouteTypes eRoute);
	
	void setTempTerrainTimer(CvPlot const& kPlot, int iNewValue);
	void setTempFeatureTimer(CvPlot const& kPlot, int iNewValue);
	void setTempBonusTimer(CvPlot const& kPlot, int iNewValue);
	void setTempImprovementTimer(CvPlot const& kPlot, int iNewValue);
	void setTempRouteTimer(CvPlot const& kPlot, int iNewValue);
	
	void changeTempTerrainTimer(CvPlot const& kPlot, int iChange);
	void changeTempFeatureTimer(CvPlot const& kPlot, int iChange);
	void changeTempBonusTimer(CvPlot const& kPlot, int iChange);
	void changeTempImprovementTimer(CvPlot const& kPlot, int iChange);
	void changeTempRouteTimer(CvPlot const& kPlot, int iChange);
	
	void update(CvPlot const& kPlot);

private:
	ArrayEnumMap<PlotNumTypes,TerrainTypes> m_RealTerrainTypeMap;
	ArrayEnumMap<PlotNumTypes,FeatureTypes> m_RealFeatureTypeMap;
	ArrayEnumMap<PlotNumTypes,int,short> m_RealFeatureVarietyMap;
	ArrayEnumMap<PlotNumTypes,BonusTypes> m_RealBonusTypeMap;
	ArrayEnumMap<PlotNumTypes,ImprovementTypes> m_RealImprovementTypeMap;
	ArrayEnumMap<PlotNumTypes,RouteTypes> m_RealRouteTypeMap;
	
	ArrayEnumMap<PlotNumTypes,TerrainTypes> m_TempTerrainTypeMap;
	ArrayEnumMap<PlotNumTypes,FeatureTypes> m_TempFeatureTypeMap;
	ArrayEnumMap<PlotNumTypes,int,short> m_TempFeatureVarietyMap;
	ArrayEnumMap<PlotNumTypes,BonusTypes> m_TempBonusTypeMap;
	ArrayEnumMap<PlotNumTypes,ImprovementTypes> m_TempImprovementTypeMap;
	ArrayEnumMap<PlotNumTypes,RouteTypes> m_TempRouteTypeMap;
	
	ArrayEnumMap<PlotNumTypes,int,short> m_TempTerrainTimerMap;
	int getTempTerrainTimer(PlotNumTypes ePlotNum) const
	{
		return m_TempTerrainTimerMap.get(ePlotNum);
	}
	
	ArrayEnumMap<PlotNumTypes,int,short> m_TempFeatureTimerMap;
	int getTempFeatureTimer(PlotNumTypes ePlotNum) const
	{
		return m_TempFeatureTimerMap.get(ePlotNum);
	}
	ArrayEnumMap<PlotNumTypes,int,short> m_TempBonusTimerMap;
	int getTempBonusTimer(PlotNumTypes ePlotNum) const
	{
		return m_TempBonusTimerMap.get(ePlotNum);
	}
	
	ArrayEnumMap<PlotNumTypes,int,short> m_TempImprovementTimerMap;
	int getTempImprovementTimer(PlotNumTypes ePlotNum) const
	{
		return m_TempImprovementTimerMap.get(ePlotNum);
	}
	
	ArrayEnumMap<PlotNumTypes,int,short> m_TempRouteTimerMap;
	int getTempRouteTimer(PlotNumTypes ePlotNum) const
	{
		return m_TempRouteTimerMap.get(ePlotNum);
	}
	TerrainTypes getRealTerrainType(PlotNumTypes ePlotNum) const
	{
		return m_RealTerrainTypeMap.get(ePlotNum);
	}
	std::pair<FeatureTypes,int> getRealFeatureType(PlotNumTypes ePlotNum) const
	{
		return std::make_pair(m_RealFeatureTypeMap.get(ePlotNum), m_RealFeatureVarietyMap.get(ePlotNum));
	}
	BonusTypes getRealBonusType(PlotNumTypes ePlotNum) const
	{
		return m_RealBonusTypeMap.get(ePlotNum);
	}
	ImprovementTypes getRealImprovementType(PlotNumTypes ePlotNum const
	{
		return m_RealImprovementTypeMap.get(ePlotNum);
	}
	RouteTypes getRealRouteType(PlotNumTypes ePlotNum) const
	{
		return m_RealRouteTypeMap.get(ePlotNum);
	}
	
	void setRealTerrainType(PlotNumTypes ePlotNum, TerrainTypes eNewValue);
	void setRealFeatureType(PlotNumTypes ePlotNum, FeatureTypes eFeature, int iVariety);
	void setRealBonusType(PlotNumTypes ePlotNum, BonusTypes eBonus);
	void setRealImprovementType(PlotNumTypes ePlotNum, ImprovementTypes eImprovement);
	void setRealRouteType(PlotNumTypes ePlotNum, RouteTypes eRoute);
	
	void setTempTerrainType(PlotNumTypes ePlotNum, TerrainTypes eNewValue);
	void setTempFeatureType(PlotNumTypes ePlotNum, FeatureTypes eFeature, int iVariety);
	void setTempBonusType(PlotNumTypes ePlotNum, BonusTypes eBonus);
	void setTempImprovementType(PlotNumTypes ePlotNum, ImprovementTypes eImprovement);
	void setTempRouteType(PlotNumTypes ePlotNum, RouteTypes eRoute);
	
	void setTempTerrainTimer(PlotNumTypes ePlotNum, int iNewValue);
	void setTempFeatureTimer(PlotNumTypes ePlotNum, int iNewValue);
	void setTempBonusTimer(PlotNumTypes ePlotNum, int iNewValue);
	void setTempImprovementTimer(PlotNumTypes ePlotNum, int iNewValue);
	void setTempRouteTimer(PlotNumTypes ePlotNum, int iNewValue);
	
	void changeTempTerrainTimer(PlotNumTypes ePlotNum, int iChange);
	void changeTempFeatureTimer(PlotNumTypes ePlotNum, int iChange);
	void changeTempBonusTimer(PlotNumTypes ePlotNum, int iChange);
	void changeTempImprovementTimer(PlotNumTypes ePlotNum, int iChange);
	void changeTempRouteTimer(PlotNumTypes ePlotNum, int iChange);
};

#endif	// CVPLOTCHANGEMAP_H
