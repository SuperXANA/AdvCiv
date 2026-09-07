#include "CvGameCoreDLL.h"
#include "CvXMLStructs.h"
#include "CvXMLLoadUtility.h"


// XANA: 04-26-2025 Favorite Technologies for Advanced Civ
int TechPreferenceData::getTechType() const
{
	return iTech;
}

int TechPreferenceData::getTechValueModifierPercent() const
{
	return iTechValueModifierPercent;
}

bool TechPreferenceData::isAlwaysSelectChoice() const
{
	return bAlwaysSelectChoice;
}

bool TechPreferenceData::isNeverSelectChoice() const
{
	return bNeverSelectChoice;
}

bool TechPreferenceData::read(CvXMLLoadUtility* pXML)
{	
	if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
	{
		pXML->SetInfoIDFromChildXmlVal(iTech, "Tech");
		pXML->GetChildXmlValByName(&iTechValueModifierPercent, "iTechValueModifierPercent");
		pXML->GetChildXmlValByName(&bAlwaysSelectChoice, "bAlwaysSelectChoice");
		pXML->GetChildXmlValByName(&bNeverSelectChoice, "bNeverSelectChoice");

		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	return true;
}
// XANA: 04-26-2025 Favorite Technologies for Advanced Civ


// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
int EventPreferenceData::getEventType() const
{
	return iEvent;
}

int EventPreferenceData::getAIWeightModifierPercent() const
{
	return iAIWeightModifierPercent;
}

bool EventPreferenceData::isAlwaysSelectChoice() const
{
	return bAlwaysSelectChoice;
}

bool EventPreferenceData::isNeverSelectChoice() const
{
	return bNeverSelectChoice;
}

bool EventPreferenceData::read(CvXMLLoadUtility* pXML)
{	
	if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
	{
		pXML->SetInfoIDFromChildXmlVal(iEvent, "Event");
		pXML->GetChildXmlValByName(&iAIWeightModifierPercent, "iAIWeightModifierPercent");
		pXML->GetChildXmlValByName(&bAlwaysSelectChoice, "bAlwaysSelectChoice");
		pXML->GetChildXmlValByName(&bNeverSelectChoice, "bNeverSelectChoice");

		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	return true;
}
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
