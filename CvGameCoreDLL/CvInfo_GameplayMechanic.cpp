#include "CvGameCoreDLL.h"
#include "CvXMLLoadUtility.h"

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration
CvGameplayMechanicInfo::CvGameplayMechanicInfo() :
	m_iLeaderType(NO_LEADER),
	m_iCivilizationType(NO_CIVILIZATION),
	m_bNoFoodPopulationGrowth(false),
	m_iElysiumTerrainAxis(NO_TERRAINAXIS),
	m_iGehennaTerrainAxis(NO_TERRAINAXIS)
{}

CvGameplayMechanicInfo::~CvGameplayMechanicInfo() :
{
// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	for (int i = 0; i < (int)m_apBonusYieldChanges.size(); ++i)
	{
		SAFE_DELETE_ARRAY(m_apBonusYieldChanges[i].second); 
	}
	m_apBonusYieldChanges.clear();
// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv

// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	m_aTerrainYieldChanges.clear();
// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
{
// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv
	for (int i = 0; i < (int)m_apFeatureYieldChanges.size(); ++i)
	{
		SAFE_DELETE_ARRAY(m_apFeatureYieldChanges[i].second); 
	}
	m_apFeatureYieldChanges.clear();
// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv
}

// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
int CvGameplayMechanicInfo::getBonusYieldChangesSize() const
{
	return m_apBonusYieldChanges.size();
}

BonusTypes CvGameplayMechanicInfo::getYieldChangeBonusType(int i) const
{
	FAssertMsg(i < (int)m_apBonusYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	
	return m_apBonusYieldChanges[i].first;
}

bool CvGameplayMechanicInfo::isBonusHasYieldChanges(int i) const
{
	FAssertMsg(i < (int)m_apBonusYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	
	return (m_apBonusYieldChanges[i].second != NULL);
}

int CvGameplayMechanicInfo::getBonusYieldChanges(int i, int j) const
{
	FAssertMsg(i < (int)m_apBonusYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	FAssertMsg(j < NUM_YIELD_TYPES, "Index out of bounds");
	FAssertMsg(j > -1, "Index out of bounds");
	
	return (m_apBonusYieldChanges[i].second ? m_apBonusYieldChanges[i].second[j] : 0);
}
// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv

// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
int CvGameplayMechanicInfo::getTerrainYieldChangesSize() const
{
	return m_aTerrainYieldChanges.size();
}

TerrainTypes CvGameplayMechanicInfo::getYieldChangeTerrainType(int i, YieldChangeLocationTypes eLocation) const
{
	FAssertMsg(i < (int)m_aTerrainYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	FAssertMsg(eLocation < NUM_YIELD_CHANGE_LOCATION_TYPES, "Index out of bounds");
	FAssertMsg(eLocation > -1, "Index out of bounds");
	
	TerrainYieldChangeData const& kStruct = m_aTerrainYieldChanges[i];
	if (kStruct.getTerrainLocationType() == eLocation)
	{
		return kStruct.getTerrainType();
	}
	return NO_TERRAIN;
}

bool CvGameplayMechanicInfo::isTerrainHasYieldChanges(int i, YieldChangeLocationTypes eLocation) const
{
	FAssertMsg(i < (int)m_aTerrainYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	FAssertMsg(eLocation < NUM_YIELD_CHANGE_LOCATION_TYPES, "Index out of bounds");
	FAssertMsg(eLocation > -1, "Index out of bounds");
	
	TerrainYieldChangeData const& kStruct = m_apTerrainYieldChanges[i];
	if (kStruct.getTerrainLocationType() == eLocation)
	{
		return (kStruct.getYieldChangesArray() != NULL);
	}
	return false;
}

int CvGameplayMechanicInfo::getTerrainYieldChanges(int i, int j, YieldChangeLocationTypes eLocation) const
{
	FAssertMsg(i < (int)m_aTerrainYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	FAssertMsg(j < NUM_YIELD_TYPES, "Index out of bounds");
	FAssertMsg(j > -1, "Index out of bounds");
	FAssertMsg(eLocation < NUM_YIELD_CHANGE_LOCATION_TYPES, "Index out of bounds");
	FAssertMsg(eLocation > -1, "Index out of bounds");
	
	TerrainYieldChangeData const& kStruct = m_aTerrainYieldChanges[i];
	if (kStruct.getTerrainLocationType() == eLocation)
	{
		return kStruct.getYieldChange(j);
	}
	return 0;
}
// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv

// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv
int CvGameplayMechanicInfo::getFeatureYieldChangesSize() const
{
	return m_apFeatureYieldChanges.size();
}

FeatureTypes CvGameplayMechanicInfo::getYieldChangeFeatureType(int i) const
{
	FAssertMsg(i < (int)m_apFeatureYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	
	return m_apFeatureYieldChanges[i].first;
}

bool CvGameplayMechanicInfo::isFeatureHasYieldChanges(int i) const
{
	FAssertMsg(i < (int)m_apFeatureYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	
	return (m_apFeatureYieldChanges[i].second != NULL);
}

int CvGameplayMechanicInfo::getFeatureYieldChanges(int i, int j) const
{
	FAssertMsg(i < (int)m_apFeatureYieldChanges.size(), "Index out of bounds");
	FAssertMsg(i > -1, "Index out of bounds");
	FAssertMsg(j < NUM_YIELD_TYPES, "Index out of bounds");
	FAssertMsg(j > -1, "Index out of bounds");
	
	return (m_apFeatureYieldChanges[i].second ? m_apFeatureYieldChanges[i].second[j] : 0);
}
// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv

bool CvGameplayMechanicInfo::read(CvXMLLoadUtility* pXML)
{
	if (!base_t::read(pXML))
		return false;

	pXML->SetInfoIDFromChildXmlVal(m_iLeaderType, "LeaderType");
	pXML->SetInfoIDFromChildXmlVal(m_iCivilizationType, "CivilizationType");
	
	pXML->GetChildXmlValByName(&m_bNoFoodPopulationGrowth, "bNoFoodPopulationGrowth");
	
	// XANA: 04-26-2025 FfH Terrain Type Changes for Advanced Civ
	pXML->SetInfoIDFromChildXmlVal(m_iGehennaTerrainAxis, "PositiveRagnarokCounterTerrainChangeType");
	pXML->SetInfoIDFromChildXmlVal(m_iElysiumTerrainAxis, "NegativeRagnarokCounterTerrainChangeType");
	// XANA: 04-26-2025 FfH Terrain Type Changes for Advanced Civ
	
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(), "BonusYieldChanges"))
	{
		if (pXML->SkipToNextVal())
		{
			int const iNumSibs = gDLL->getXMLIFace()->GetNumChildren(pXML->GetXML());
			if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
			{
				if (0 < iNumSibs)
				{
					CvString szTextVal;
					for (int j = 0; j < iNumSibs; j++)
					{
						pXML->GetChildXmlValByName(szTextVal, "BonusType");
						BonusTypes eIndex = (BonusTypes)pXML->FindInInfoClass(szTextVal);
						if (eIndex != NO_BONUS)
						{
							int* piBonusChanges = NULL;
							if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(),"BonusYields"))
							{
								pXML->SetYieldArray(&piBonusChanges);
							}
							else pXML->InitList(&piBonusChanges, NUM_YIELD_TYPES);
							m_apBonusYieldChanges.push_back(std::make_pair(eIndex, piBonusChanges));
						}
						if (!gDLL->getXMLIFace()->NextSibling(pXML->GetXML()))
							break;
					}
				}
				gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
			}
		}
		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv
	
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	for (int iLocationType = 0; iLocationType < NUM_YIELD_CHANGE_LOCATION_TYPES; ++iLocationType)
	{
		if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(),
			((iLocationType == INLAND_ONLY) ? 
			"TerrainYieldChanges" :
			"TerrainRiverYieldChanges")))
		{
			if (pXML->SkipToNextVal())
			{
				int const iNumSibs = gDLL->getXMLIFace()->GetNumChildren(pXML->GetXML());
				if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
				{
					if (0 < iNumSibs)
					{
						CvString szTextVal;
						for (int j = 0; j < iNumSibs; j++)
						{
							pXML->GetChildXmlValByName(szTextVal, "TerrainType");
							TerrainTypes eIndex = (TerrainTypes)pXML->FindInInfoClass(szTextVal);
							if (eIndex != NO_TERRAIN)
							{
								TerrainYieldChangeData kStruct(eIndex, iLocationType);
								kStruct.read(pXML);
								m_aTerrainYieldChanges.push_back(kStruct);
							}
							if (!gDLL->getXMLIFace()->NextSibling(pXML->GetXML()))
								break;
						}
					}
					gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
				}
			}
			gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
		}
	}
	// XANA: 03-15-2025 FfH Civilization Terrain Yield Changes for AdvancedCiv
	
	// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv
	if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(), "FeatureYieldChanges"))
	{
		if (pXML->SkipToNextVal())
		{
			int const iNumSibs = gDLL->getXMLIFace()->GetNumChildren(pXML->GetXML());
			if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
			{
				if (0 < iNumSibs)
				{
					CvString szTextVal;
					for (int j = 0; j < iNumSibs; j++)
					{
						pXML->GetChildXmlValByName(szTextVal, "FeatureType");
						FeatureTypes eIndex = (FeatureTypes)pXML->FindInInfoClass(szTextVal);
						if (eIndex != NO_FEATURE)
						{
							int* piFeatureChanges = NULL;
							if (gDLL->getXMLIFace()->SetToChildByTagName(pXML->GetXML(),"FeatureYields"))
							{
								pXML->SetYieldArray(&piFeatureChanges);
							}
							else pXML->InitList(&piFeatureChanges, NUM_YIELD_TYPES);
							m_apFeatureYieldChanges.push_back(std::make_pair(eIndex, piFeatureChanges));
						}
						if (!gDLL->getXMLIFace()->NextSibling(pXML->GetXML()))
							break;
					}
				}
				gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
			}
		}
		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	// XANA: 10-18-2025 FfH Civilization Feature Yield Changes for AdvancedCiv

	return true;
}

bool CvGameplayMechanicInfo::readPass3()
{
	// XANA (note): Nothing here yet.
	return true;
}
// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration