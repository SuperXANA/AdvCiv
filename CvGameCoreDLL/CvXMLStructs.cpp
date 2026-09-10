#include "CvGameCoreDLL.h"
#include "CvXMLStructs.h"
#include "CvXMLLoadUtility.h"


// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
int TerrainYieldChangeData::getTerrainType() const
{
	return iTerrain;
}

int TerrainYieldChangeData::getTerrainLocationType() const
{
	return iTerrainLocationType;
}

int* TerrainYieldChangeData::getYieldChangesArray() const
{
	return piTerrainChanges;
}

int TerrainYieldChangeData::getYieldChange(YieldTypes eYield) const
{
	return piTerrainChanges ? piTerrainChanges[eYield] : 0;
}

bool TerrainYieldChangeData::read(CvXMLLoadUtility* pXML)
{
	if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(), "TerrainYields"))
	{
		pXML->SetYieldArray(&piTerrainChanges);
	}
	else pXML->InitList(&piTerrainChanges, NUM_YIELD_TYPES);
	return true;
}
// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
