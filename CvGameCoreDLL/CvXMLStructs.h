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


// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
struct UnitPreferenceData
{
	UnitPreferenceData() : iUnitCombat(NO_UNITCOMBAT), iUnitClass(NO_UNITCLASS), iUnit(NO_UNIT),
	iUnitValueModifierPercent(0), bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitCombatType() const;
	int getUnitClassType() const;
	int getUnitType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnitCombat;
	int iUnitClass;
	int iUnit;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
	
#endif	// CVXMLSTRUCTS_H
