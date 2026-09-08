#include "CvGameCoreDLL.h"
#include "CvXMLLoadUtility.h"

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration
CvGameplayMechanicInfo::CvGameplayMechanicInfo() :
	m_iLeaderType(NO_LEADER),
	m_iCivilizationType(NO_CIVILIZATION)
{}

CvGameplayMechanicInfo::~CvGameplayMechanicInfo() :
{
	// XANA (note): Nothing here yet.
}

int CvGameplayMechanicInfo::getLeaderType() const
{
	return m_iLeaderType;
}

int CvGameplayMechanicInfo::getCivilizationType() const
{
	return m_iCivilizationType;
}

bool CvGameplayMechanicInfo::read(CvXMLLoadUtility* pXML)
{
	if (!base_t::read(pXML))
		return false;

	pXML->SetInfoIDFromChildXmlVal(m_iLeaderType, "LeaderType");
	pXML->SetInfoIDFromChildXmlVal(m_iCivilizationType, "CivilizationType");

	return true;
}

bool CvGameplayMechanicInfo::readPass3()
{
	// XANA (note): Nothing here yet.
	return true;
}
// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration