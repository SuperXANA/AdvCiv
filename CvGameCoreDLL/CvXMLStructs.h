#pragma once

#ifndef CVXMLSTRUCTS_H
#define CVXMLSTRUCTS_H

// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
struct EventPreferenceData
{
	EventPreferenceData() : iEvent(NO_EVENT), iEventChoiceAIWeightMod(0), 
	bAlwaysSelectChoice(false), bNeverSelectChoice(false) {}
	
	int getEventType() const;
	int getAIWeightModifier() const;
	bool isAlwaysSelectChoice() const;
	bool isNeverSelectChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iEvent;
	int iAIWeightModifier;
	bool bAlwaysSelectChoice;
	bool bNeverSelectChoice;
};
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
	
#endif	// CVXMLSTRUCTS_H
