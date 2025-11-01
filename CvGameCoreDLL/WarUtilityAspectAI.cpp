
#include "CvGameCoreDLL.h"
#include "CvXMLLoadUtility.h"
#include "WarUtilityAspectAI.h"

// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
CvWarUtilityAspectAIInfo::CvWarUtilityAspectAIInfo() : m_iAIWeight(0)
{}

CvWarUtilityAspectAIInfo::~CvWarUtilityAspectAIInfo()
{}

bool CvWarUtilityAspectAIInfo::read(CvXMLLoadUtility* pXML)
{
	if (!base_t::read(pXML))
		return false;

	pXML->GetChildXmlValByName(&m_iAIWeight, "iAIWeight", 100);
	return true;
}
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights