#include "CvGameCoreDLL.h"
#include "CvXMLStructs.h"
#include "CvXMLLoadUtility.h"


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
		pXML->SetInfoIDFromChildXmlVal(iEvent, "EventType");
		pXML->GetChildXmlValByName(&iAIWeightModifierPercent, "iAIWeightModifierPercent");
		pXML->GetChildXmlValByName(&bAlwaysSelectChoice, "bAlwaysSelectChoice");
		pXML->GetChildXmlValByName(&bNeverSelectChoice, "bNeverSelectChoice");

		gDLL->getXMLIFace()->SetToParent(pXML->GetXML());
	}
	return true;
}
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
