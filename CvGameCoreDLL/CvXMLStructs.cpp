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

bool TechPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool TechPreferenceData::isbNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool TechPreferenceData::read(CvXMLLoadUtility* pXML)
{	
	if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
	{
		pXML->SetInfoIDFromChildXmlVal(iTech, "TechType");
		pXML->GetChildXmlValByName(&iTechValueModifierPercent, "iTechValueModifierPercent");
		pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
		pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");

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

int EventPreferenceData::getEventValueModifierPercent() const
{
	return iEventValueModifierPercent;
}

bool EventPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool EventPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool EventPreferenceData::read(CvXMLLoadUtility* pXML)
{	
	if (gDLL->getXMLIFace()->SetToChild(pXML->GetXML()))
	{
		pXML->SetInfoIDFromChildXmlVal(iEvent, "Event");
		pXML->GetChildXmlValByName(&iEventValueModifierPercent, "iEventValueModifierPercent");
		pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
		pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");

		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	return true;
}
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
