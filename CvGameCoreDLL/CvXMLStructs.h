#pragma once

#ifndef CVXMLSTRUCTS_H
#define CVXMLSTRUCTS_H

// XANA: 04-26-2025 Favorite Technologies for Advanced Civ
struct TechPreferenceData
{
	TechPreferenceData() : iTech(NO_TECH), iTechValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getTechType() const;
	int getTechValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iTech;
	int iTechValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 04-26-2025 Favorite Technologies for Advanced Civ


// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
struct EventPreferenceData
{
	EventPreferenceData() : iEvent(NO_EVENT), iEventValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getEventType() const;
	int getEventValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iEvent;
	int iEventValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
	
#endif	// CVXMLSTRUCTS_H
