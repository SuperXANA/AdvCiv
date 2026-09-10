#pragma once

#ifndef CV_INFO_GAMEPLAYMECHANIC_H
#define CV_INFO_GAMEPLAYMECHANIC_H

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration
class CvPlayer;

enum YieldChangeLocationTypes
{
	INLAND_ONLY,
	RIVERSIDE_ONLY,
	NUM_YIELD_CHANGE_LOCATION_TYPES
};

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvGameplayMechanicInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvGameplayMechanicInfo : public CvInfoBase
{
	typedef CvInfoBase base_t;
public: // advc: All the const functions are exposed to Python
	CvGameplayMechanicInfo();
	~CvGameplayMechanicInfo();

	int getLeaderType() const;
	int getCivilizationType() const;
	
	bool isNoFoodPopulationGrowth() const { return m_bNoFoodPopulationGrowth; }
	
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	int getBonusYieldChangesSize() const;
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	int getTerrainYieldChangesSize() const;
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv

	// Array access:
	
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	BonusTypes getYieldChangeBonusType(int i) const;
	bool isBonusHasYieldChanges(int i) const;
	int getBonusYieldChanges(int i, int j) const;
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	TerrainTypes getYieldChangeTerrainType(int i, YieldChangeLocationTypes eLocation = INLAND_ONLY) const;
	bool isTerrainHasYieldChanges(int i, YieldChangeLocationTypes eLocation = INLAND_ONLY) const;
	int getTerrainYieldChanges(int i, int j, YieldChangeLocationTypes eLocation = INLAND_ONLY) const;
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv

	bool read(CvXMLLoadUtility* pXML);
	bool readPass3();

protected:
	int m_iLeaderType;
	int m_iCivilizationType;
	
	bool m_bNoFoodPopulationGrowth;
	
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	std::vector<std::pair<BonusTypes, int*> > m_apBonusYieldChanges;
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	std::vector<TerrainYieldChangeData> m_aTerrainYieldChanges;
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
};

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration

#endif