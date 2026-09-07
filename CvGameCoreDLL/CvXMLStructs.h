#pragma once

#ifndef CVXMLSTRUCTS_H
#define CVXMLSTRUCTS_H

// XANA: 04-26-2025 Favorite Technologies for Advanced Civ
struct TechPreferenceData
{
	TechPreferenceData() : iTech(NO_TECH), iTechValueModifierPercent(0), 
	bAlwaysSelectChoice(false), bNeverSelectChoice(false) {}
	
	int getTechType() const;
	int getTechValueModifierPercent() const;
	bool isAlwaysSelectChoice() const;
	bool isNeverSelectChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iTech;
	int iTechValueModifierPercent;
	bool bAlwaysSelectChoice;
	bool bNeverSelectChoice;
};
// XANA: 04-26-2025 Favorite Technologies for Advanced Civ


// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
struct EventPreferenceData
{
	EventPreferenceData() : iEvent(NO_EVENT), iAIWeightModifierPercent(0), 
	bAlwaysSelectChoice(false), bNeverSelectChoice(false) {}
	
	int getEventType() const;
	int getAIWeightModifierPercent() const;
	bool isAlwaysSelectChoice() const;
	bool isNeverSelectChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iEvent;
	int iAIWeightModifierPercent;
	bool bAlwaysSelectChoice;
	bool bNeverSelectChoice;
};
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
	
#endif	// CVXMLSTRUCTS_H
