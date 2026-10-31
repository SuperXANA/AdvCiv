#include "CvGameCoreDLL.h"
#include "CvXMLStructs.h"
#include "CvXMLLoadUtility.h"
#include <cstring>
#include "CvInfo_Tech.h"
#include "CvInfo_RandomEvent.h"
#include "CvInfo_Unit.h"

// XANA: 10-31-2026 Validate preference key categories (ChatGPT)
namespace
{
	template<class EnumType>
	bool readPreferenceInfoID(CvXMLLoadUtility* pXML, int& iResult,
		char const* szTag, int iInfoCount)
	{
		iResult = -1;
		CvString szType;
		if (!pXML->GetChildXmlValByName(szType, szTag))
			return false;
		int const iCandidate = GC.getInfoTypeForString(szType.c_str());
		if (iCandidate < 0)
			return false;
		if (iCandidate >= iInfoCount)
		{
			FAssertMsg(false, "Preference type index is outside its info category");
			return false;
		}
		char const* szCanonicalType = GC.getInfo(static_cast<EnumType>(iCandidate)).getType();
		if (szCanonicalType == NULL || std::strcmp(szCanonicalType, szType.c_str()) != 0)
		{
			FAssertMsg(false, "Preference type belongs to a different info category");
			return false;
		}
		iResult = iCandidate;
		return true;
	}
}
// XANA: 10-31-2026 Validate preference key categories (ChatGPT)



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

bool TechPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool TechPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	if (!readPreferenceInfoID<TechTypes>(pXML, iTech, "TechType", GC.getNumTechInfos()))
		return false;
	pXML->GetChildXmlValByName(&iTechValueModifierPercent, "iTechValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
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
	// Caller already positioned the XML cursor on this preference record.
	if (!readPreferenceInfoID<EventTypes>(pXML, iEvent, "Event", GC.getNumEventInfos()))
		return false;
	pXML->GetChildXmlValByName(&iEventValueModifierPercent, "iEventValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process


// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
int UnitCombatPreferenceData::getUnitCombatType() const
{
	return iUnitCombat;
}

int UnitCombatPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitCombatPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitCombatPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitCombatPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	if (!readPreferenceInfoID<UnitCombatTypes>(pXML, iUnitCombat, "UnitCombatType", GC.getNumUnitCombatInfos()))
		return false;
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}

int UnitClassPreferenceData::getUnitClassType() const
{
	return iUnitClass;
}

int UnitClassPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitClassPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitClassPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitClassPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	if (!readPreferenceInfoID<UnitClassTypes>(pXML, iUnitClass, "UnitClassType", GC.getNumUnitClassInfos()))
		return false;
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}

int UnitPreferenceData::getUnitType() const
{
	return iUnit;
}

int UnitPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	if (!readPreferenceInfoID<UnitTypes>(pXML, iUnit, "UnitType", GC.getNumUnitInfos()))
		return false;
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}
// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
