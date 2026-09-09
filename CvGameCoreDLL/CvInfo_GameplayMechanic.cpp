#include "CvGameCoreDLL.h"
#include "CvXMLLoadUtility.h"

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration
CvGameplayMechanicInfo::CvGameplayMechanicInfo() :
	m_iLeaderType(NO_LEADER),
	m_iCivilizationType(NO_CIVILIZATION),
	m_bNoFoodPopulationGrowth(false)
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
}

int CvGameplayMechanicInfo::getLeaderType() const
{
	return m_iLeaderType;
}

int CvGameplayMechanicInfo::getCivilizationType() const
{
	return m_iCivilizationType;
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
	int const* piBonusChanges = m_apBonusYieldChanges[i].second;
	if (piBonusChanges != NULL)
	{
		return piBonusChanges[j];
	}
	return 0;
}
// XANA: 10-19-2025 FfH Civilization Bonus Yield Changes for AdvancedCiv

bool CvGameplayMechanicInfo::read(CvXMLLoadUtility* pXML)
{
	if (!base_t::read(pXML))
		return false;

	pXML->SetInfoIDFromChildXmlVal(m_iLeaderType, "LeaderType");
	pXML->SetInfoIDFromChildXmlVal(m_iCivilizationType, "CivilizationType");
	
	pXML->GetChildXmlValByName(&m_bNoFoodPopulationGrowth, "bNoFoodPopulationGrowth");
	
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

	return true;
}

bool CvGameplayMechanicInfo::readPass3()
{
	// XANA (note): Nothing here yet.
	return true;
}
// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration