#pragma once

#ifndef CVXMLSTRUCTS_H
#define CVXMLSTRUCTS_H

// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
struct TerrainYieldChangeData
{
	TerrainYieldChangeData(int iIndex, int iLocationType) : iTerrain(iIndex), iTerrainLocationType(iLocationType),
	piTerrainChanges(NULL) {}
	
	int getTerrainType() const;
	int getTerrainModifyType() const;
	
	int* getYieldChangesArray() const;
	int getYieldChange(YieldTypes eYield) const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iTerrain;
	int iTerrainLocationType;
	int* piTerrainChanges;
};
// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv

#endif	// CVXMLSTRUCTS_H
