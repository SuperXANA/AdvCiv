//  $Header: //depot/main/Civilization4/CvGameCoreDLL/CvStructs.cpp#3 $
//------------------------------------------------------------------------------------------------
//
//  ***************** CIV4 GAME ENGINE   ********************
//
//! \file		CvStructs.cpp
//! \author		Multiple
//! \brief		Implementation of basic Civ4 structures
//
//------------------------------------------------------------------------------------------------
//  Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
//------------------------------------------------------------------------------------------------

#include "CvGameCoreDLL.h"
#include "CvStructs.h"
#include "CvUnit.h"
#include "CvPlot.h" // advc.071
#include "CvInfo_Command.h" // advc (for NukeMissionDef)

// advc.opt: For reading legacy savegames
void IDInfo::validateOwner()
{
	if (eOwner == NO_PLAYER)
	{
		if (iID == FFreeList::INVALID_INDEX)
			eOwner = BARBARIAN_PLAYER;
		else FAssert(iID == FFreeList::INVALID_INDEX);
	}
}

int EventTriggeredData::getID() const
{
	return m_iId;
}

void EventTriggeredData::setID(int iID)
{
	m_iId = iID;
}

void EventTriggeredData::read(FDataStreamBase* pStream)
{
	pStream->Read(&m_iId);
	pStream->Read((int*)&m_eTrigger);
	pStream->Read(&m_iTurn);
	pStream->Read((int*)&m_ePlayer);
	pStream->Read(&m_iCityId);
	pStream->Read(&m_iPlotX);
	pStream->Read(&m_iPlotY);
	pStream->Read(&m_iUnitId);
	pStream->Read((int*)&m_eOtherPlayer);
	pStream->Read(&m_iOtherPlayerCityId);
	pStream->Read((int*)&m_eReligion);
	pStream->Read((int*)&m_eCorporation);
	pStream->Read((int*)&m_eBuilding);
	pStream->ReadString(m_szText);
	pStream->ReadString(m_szGlobalText);
}

void EventTriggeredData::write(FDataStreamBase* pStream)
{
	pStream->Write(m_iId);
	pStream->Write(m_eTrigger);
	pStream->Write(m_iTurn);
	pStream->Write(m_ePlayer);
	pStream->Write(m_iCityId);
	pStream->Write(m_iPlotX);
	pStream->Write(m_iPlotY);
	pStream->Write(m_iUnitId);
	pStream->Write(m_eOtherPlayer);
	pStream->Write(m_iOtherPlayerCityId);
	pStream->Write(m_eReligion);
	pStream->Write(m_eCorporation);
	pStream->Write(m_eBuilding);
	pStream->WriteString(m_szText);
	pStream->WriteString(m_szGlobalText);
}

int VoteSelectionData::getID() const
{
	return iId;
}

void VoteSelectionData::setID(int iID)
{
	iId = iID;
}

void VoteSelectionData::read(FDataStreamBase* pStream)
{
	pStream->Read(&iId);
	pStream->Read((int*)&eVoteSource);
	int iSize;
	pStream->Read(&iSize);
	for (int i = 0; i < iSize; ++i)
	{
		VoteSelectionSubData kData;
		pStream->Read((int*)&kData.eVote);
		pStream->Read((int*)&kData.ePlayer);
		pStream->Read(&kData.iCityId);
		pStream->Read((int*)&kData.eOtherPlayer);
		pStream->ReadString(kData.szText);
		aVoteOptions.push_back(kData);
	}
}

void VoteSelectionData::write(FDataStreamBase* pStream)
{
	pStream->Write(iId);
	pStream->Write(eVoteSource);
	pStream->Write(aVoteOptions.size());
	for (std::vector<VoteSelectionSubData>::iterator it = aVoteOptions.begin(); it != aVoteOptions.end(); ++it)
	{
		pStream->Write(it->eVote);
		pStream->Write(it->ePlayer);
		pStream->Write(it->iCityId);
		pStream->Write(it->eOtherPlayer);
		pStream->WriteString(it->szText);
	}
}

int VoteTriggeredData::getID() const
{
	return iId;
}

void VoteTriggeredData::setID(int iID)
{
	iId = iID;
}

void VoteTriggeredData::read(FDataStreamBase* pStream)
{
	pStream->Read(&iId);
	pStream->Read((int*)&eVoteSource);
	pStream->Read((int*)&kVoteOption.eVote);
	pStream->Read((int*)&kVoteOption.ePlayer);
	pStream->Read(&kVoteOption.iCityId);
	pStream->Read((int*)&kVoteOption.eOtherPlayer);
	pStream->ReadString(kVoteOption.szText);
}

void VoteTriggeredData::write(FDataStreamBase* pStream)
{
	pStream->Write(iId);
	pStream->Write(eVoteSource);
	pStream->Write(kVoteOption.eVote);
	pStream->Write(kVoteOption.ePlayer);
	pStream->Write(kVoteOption.iCityId);
	pStream->Write(kVoteOption.eOtherPlayer);
	pStream->WriteString(kVoteOption.szText);
}

// advc.enum: Obsolete
/*void PlotExtraYield::read(FDataStreamBase* pStream) {
	pStream->Read(&m_iX);
	pStream->Read(&m_iY);
	m_aeExtraYield.clear();
	FOR_EACH_ENUM(Yield) {
		int iYield; pStream->Read(&iYield);
		m_aeExtraYield.push_back(iYield);
	}
}
void PlotExtraYield::write(FDataStreamBase* pStream) {
	pStream->Write(m_iX);
	pStream->Write(m_iY);
	for (int i = 0; i < NUM_YIELD_TYPES; ++i)
		pStream->Write(m_aeExtraYield[i]);
}
void PlotExtraCost::read(FDataStreamBase* pStream) {
	pStream->Read(&m_iX);
	pStream->Read(&m_iY);
	pStream->Read(&m_iCost);
}
void PlotExtraCost::write(FDataStreamBase* pStream) {
	pStream->Write(m_iX);
	pStream->Write(m_iY);
	pStream->Write(m_iCost);
}
void BuildingYieldChange::read(FDataStreamBase* pStream) {
	pStream->Read((int*)&eBuildingClass);
	pStream->Read((int*)&eYield);
	pStream->Read(&iChange);
}
void BuildingYieldChange::write(FDataStreamBase* pStream) {
	pStream->Write(eBuildingClass);
	pStream->Write(eYield);
	pStream->Write(iChange);
}
void BuildingCommerceChange::read(FDataStreamBase* pStream) {
	pStream->Read((int*)&eBuildingClass);
	pStream->Read((int*)&eCommerce);
	pStream->Read(&iChange);
}
void BuildingCommerceChange::write(FDataStreamBase* pStream) {
	pStream->Write(eBuildingClass);
	pStream->Write(eCommerce);
	pStream->Write(iChange);
}*/

void checkBattleUnitType(BattleUnitTypes unitType)
{
	FAssertMsg((unitType >= 0) && (unitType < BATTLE_UNIT_COUNT), "[Jason] Invalid battle unit type.");
}

CvBattleRound::CvBattleRound() :
	m_iWaveSize(0),
	m_bRangedRound(false)
{
	m_aNumKilled[BATTLE_UNIT_ATTACKER] = m_aNumKilled[BATTLE_UNIT_DEFENDER] = 0;
	m_aNumAlive[BATTLE_UNIT_ATTACKER] = m_aNumAlive[BATTLE_UNIT_DEFENDER] = 0;
}

bool CvBattleRound::isValid() const
{
	bool bValid = true;

	// Valid if no more than the wave size was killed, and didn't kill more attackers than were defenders or vv.
	bValid &= (m_aNumKilled[BATTLE_UNIT_ATTACKER] + m_aNumKilled[BATTLE_UNIT_DEFENDER] <= m_iWaveSize);
	bValid &= (m_aNumKilled[BATTLE_UNIT_ATTACKER] <= m_aNumAlive[BATTLE_UNIT_DEFENDER]);
	bValid &= (m_aNumKilled[BATTLE_UNIT_DEFENDER] <= m_aNumAlive[BATTLE_UNIT_ATTACKER]);
	return bValid;
}

bool CvBattleRound::isRangedRound() const
{
	return m_bRangedRound;
}

void CvBattleRound::setRangedRound(bool value)
{
	m_bRangedRound = value;
}

int CvBattleRound::getWaveSize() const
{
	return m_iWaveSize;
}

void CvBattleRound::setWaveSize(int size)
{
	m_iWaveSize = size;
}

int CvBattleRound::getNumKilled(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	return m_aNumKilled[unitType];
}

void CvBattleRound::setNumKilled(BattleUnitTypes unitType, int value)
{
	checkBattleUnitType(unitType);
	m_aNumKilled[unitType] = value;
}

void CvBattleRound::addNumKilled(BattleUnitTypes unitType, int increment)
{
	checkBattleUnitType(unitType);
	m_aNumKilled[unitType] += increment;
}

int CvBattleRound::getNumAlive(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	return m_aNumAlive[unitType];
}

void CvBattleRound::setNumAlive(BattleUnitTypes unitType, int value)
{
	checkBattleUnitType(unitType);
	m_aNumAlive[unitType] = value;
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvMissionDefinition::CvMissionDefinition
//! \brief      Default constructor.
//------------------------------------------------------------------------------------------------
CvMissionDefinition::CvMissionDefinition() :
	// advc.001 (from C2C): Was 0. Currently always overwritten by setMissionTime anyway.
	m_fMissionTime(-1.f),
	m_eMissionType(NO_MISSION),
	m_pPlot(NULL)
{
	for(int i=0;i<BATTLE_UNIT_COUNT;i++)
		m_aUnits[i] = NULL;
}

MissionTypes CvMissionDefinition::getMissionType() const
{
	return m_eMissionType;
}

void CvMissionDefinition::setMissionType(MissionTypes missionType)
{
	m_eMissionType = missionType;
}

float CvMissionDefinition::getMissionTime() const
{
	return m_fMissionTime;
}

void CvMissionDefinition::setMissionTime(float time)
{
	m_fMissionTime = time;
}

CvUnit *CvMissionDefinition::getUnit(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	return m_aUnits[unitType];
}

void CvMissionDefinition::setUnit(BattleUnitTypes unitType, CvUnit *unit)
{
	checkBattleUnitType(unitType);
	m_aUnits[unitType] = unit;
}

const CvPlot *CvMissionDefinition::getPlot() const
{
	return m_pPlot;
}

void CvMissionDefinition::setPlot(const CvPlot *plot)
{
	m_pPlot = plot;
}

// advc: Body cut from CvUnit::nuke
NukeMissionDef::NukeMissionDef(CvPlot const& kPlot, CvUnit& kNuke, bool bIntercept,
	int iBaseTime) // advc.002m
{
	setMissionTime(iBaseTime * gDLL->getSecsPerTurn());
	setMissionType(MISSION_NUKE);
	setPlot(&kPlot);
	setUnit(BATTLE_UNIT_ATTACKER, &kNuke);
	if (bIntercept)
		setUnit(BATTLE_UNIT_DEFENDER, &kNuke);
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvBattleDefinition::CvBattleDefinition
//! \brief      Constructor.
//------------------------------------------------------------------------------------------------
CvBattleDefinition::CvBattleDefinition() :
	m_bAdvanceSquare(false),
	CvMissionDefinition()
{
	m_fMissionTime = 0.0f;
	m_eMissionType = MISSION_BEGIN_COMBAT;
	m_iNumMeleeRounds = 0;
	m_iNumRangedRounds = 0;

	for(int i=0;i<BATTLE_UNIT_COUNT;i++)
	{
		m_aUnits[i] = NULL;
		m_aFirstStrikes[i] = 0;
		for(int j=0;j<BATTLE_TIME_COUNT;j++)
			m_aDamage[i][j] = 0;
	}
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvBattleDefinition::CvBattleDefinition
//! \brief      Copy constructor
//! \param      kCopy The object to copy
//------------------------------------------------------------------------------------------------
CvBattleDefinition::CvBattleDefinition(const CvBattleDefinition & kCopy) :
	m_bAdvanceSquare(kCopy.m_bAdvanceSquare)
{
	m_fMissionTime = kCopy.m_fMissionTime;
	m_eMissionType = MISSION_BEGIN_COMBAT;
	m_iNumMeleeRounds = kCopy.m_iNumMeleeRounds;
	m_iNumRangedRounds = kCopy.m_iNumRangedRounds;

	for(int i=0;i<BATTLE_UNIT_COUNT;i++)
	{
		m_aUnits[i] = kCopy.m_aUnits[i];
		m_aFirstStrikes[i] = kCopy.m_aFirstStrikes[i];
		for(int j=0;j<BATTLE_TIME_COUNT;j++)
			m_aDamage[i][j] = kCopy.m_aDamage[i][j];
	}

	m_aBattleRounds.assign(kCopy.m_aBattleRounds.begin(), kCopy.m_aBattleRounds.end());
}

CvBattleDefinition::~CvBattleDefinition() {}

int CvBattleDefinition::getDamage(BattleUnitTypes unitType, BattleTimeTypes timeType) const
{
	checkBattleUnitType(unitType);
	checkBattleTimeType(timeType);
	return m_aDamage[unitType][timeType];
}

void CvBattleDefinition::setDamage(BattleUnitTypes unitType, BattleTimeTypes timeType, int damage)
{
	checkBattleUnitType(unitType);
	checkBattleTimeType(timeType);
	m_aDamage[unitType][timeType] = damage;
}

void CvBattleDefinition::addDamage(BattleUnitTypes unitType, BattleTimeTypes timeType, int increment)
{
	checkBattleUnitType(unitType);
	checkBattleTimeType(timeType);
	m_aDamage[unitType][timeType] += increment;
}

int CvBattleDefinition::getFirstStrikes(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	return m_aFirstStrikes[unitType];
}

void CvBattleDefinition::setFirstStrikes(BattleUnitTypes unitType, int firstStrikes)
{
	checkBattleUnitType(unitType);
	m_aFirstStrikes[unitType] = firstStrikes;
}

void CvBattleDefinition::addFirstStrikes(BattleUnitTypes unitType, int increment)
{
	checkBattleUnitType(unitType);
	m_aFirstStrikes[unitType] += increment;
}

bool CvBattleDefinition::isAdvanceSquare() const
{
	return m_bAdvanceSquare;
}

void CvBattleDefinition::setAdvanceSquare(bool advanceSquare)
{
	m_bAdvanceSquare = advanceSquare;
}

int CvBattleDefinition::getNumRangedRounds() const
{
	return m_iNumRangedRounds;
}

void CvBattleDefinition::setNumRangedRounds(int count)
{
	m_iNumRangedRounds = count;
}

void CvBattleDefinition::addNumRangedRounds(int increment)
{
	m_iNumRangedRounds += increment;
}

int CvBattleDefinition::getNumMeleeRounds() const
{
	return m_iNumMeleeRounds;
}

void CvBattleDefinition::setNumMeleeRounds(int count)
{
	m_iNumMeleeRounds = count;
}

void CvBattleDefinition::addNumMeleeRounds(int increment)
{
	m_iNumMeleeRounds += increment;
}

int CvBattleDefinition::getNumBattleRounds() const
{
	return m_aBattleRounds.size();
}

void CvBattleDefinition::clearBattleRounds()
{
	m_aBattleRounds.clear();
}

CvBattleRound &CvBattleDefinition::getBattleRound(int index)
{
	checkBattleRound(index);
	return m_aBattleRounds[index];
}

const CvBattleRound &CvBattleDefinition::getBattleRound(int index) const
{
	checkBattleRound(index);
	return m_aBattleRounds[index];
}

void CvBattleDefinition::addBattleRound(const CvBattleRound &round)
{
	m_aBattleRounds.push_back(round);
}

void CvBattleDefinition::setBattleRound(int index, const CvBattleRound &round)
{
	m_aBattleRounds.assign(index, round);
}

void CvBattleDefinition::checkBattleTimeType(BattleTimeTypes timeType) const
{
	FAssertMsg((timeType >= 0) && (timeType < BATTLE_TIME_COUNT), "[Jason] Invalid battle time type.");
}

void CvBattleDefinition::checkBattleRound(int index) const
{
	FAssertMsg((index >= 0) && (index < (int)m_aBattleRounds.size()), "[Jason] Invalid battle round index.");
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvAirMissionDefinition::CvAirMissionDefinition
//! \brief      Constructor
//------------------------------------------------------------------------------------------------
CvAirMissionDefinition::CvAirMissionDefinition() :
	CvMissionDefinition()
{
	m_fMissionTime = 0.0f;
	m_eMissionType = MISSION_AIRPATROL;
	// <advc> Safer to initialize this here
	for(int i = 0; i < BATTLE_UNIT_COUNT; i++)
		m_aDamage[i] = 0; // </advc>
}

//------------------------------------------------------------------------------------------------
// FUNCTION:    CvAirMissionDefinition::CvAirMissionDefinition
//! \brief      Copy constructor
//! \param      kCopy The object to copy
//------------------------------------------------------------------------------------------------
CvAirMissionDefinition::CvAirMissionDefinition(const CvAirMissionDefinition & kCopy)
{
	m_fMissionTime = kCopy.m_fMissionTime;
	m_eMissionType = kCopy.m_eMissionType;
	m_pPlot = kCopy.m_pPlot;

	for(int i=0;i<BATTLE_UNIT_COUNT;i++)
	{
		m_aDamage[i] = kCopy.m_aDamage[i];
		m_aUnits[i] = kCopy.m_aUnits[i];
	}
}

int CvAirMissionDefinition::getDamage(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	return m_aDamage[unitType];
}

void CvAirMissionDefinition::setDamage(BattleUnitTypes unitType, int damage)
{
	checkBattleUnitType(unitType);
	m_aDamage[unitType] = damage;
}

bool CvAirMissionDefinition::isDead(BattleUnitTypes unitType) const
{
	checkBattleUnitType(unitType);
	FAssertMsg(getUnit(unitType) != NULL, "[Jason] Invalid battle unit type.");
	if(getDamage(unitType) >= getUnit(unitType)->maxHitPoints())
		return true;
	else
		return false;
}

PBGameSetupData::PBGameSetupData()
{
	for (int i = 0; i < NUM_GAMEOPTION_TYPES; i++)
	{
		abOptions.push_back(false);
	}
	for (int i = 0; i < NUM_MPOPTION_TYPES; i++)
	{
		abMPOptions.push_back(false);
	}
}

// advc.071:
FirstContactData::FirstContactData(CvPlot const* pAt1, CvPlot const* pAt2,
	CvUnit const* pUnit1, CvUnit const* pUnit2)
{
	/*  Don't need to worry here about which unit is where and who sees whom - can
		figure that out when we know which teams are meeting. */

	if(pAt1 != NULL)
	{
		x1 = pAt1->getX();
		y1 = pAt1->getY();
	}
	if(pAt2 != NULL)
	{
		x2 = pAt2->getX();
		y2 = pAt2->getY();
	}
	if(pUnit1 != NULL)
	{
		u1.eOwner = pUnit1->getOwner();
		u1.iID = pUnit1->getID();
	}
	if(pUnit2 != NULL)
	{
		u2.eOwner = pUnit2->getOwner();
		u2.iID = pUnit2->getID();
	}
}

// XANA: 05-23-2026 LLM Text Diplomacy Generation
void DynamicResponseFilter::setDefaultValues()
{
	abActiveCivilizations.assign(GC.getNumCivilizationInfos(), static_cast<char>(false));
	abActiveLeaders.assign(GC.getNumLeaderHeadInfos(), static_cast<char>(false));
	abActiveAttitudes.assign(NUM_ATTITUDE_TYPES, static_cast<char>(false));
	abActivePowers.assign(NUM_DIPLOMACYPOWER_TYPES, static_cast<char>(false));
}

void LLMPromptData::setText(CvString const& szText)
{
	szPromptText = szText;
}

LLMPromptData::~LLMPromptData()
{
	SAFE_DELETE(m_pFilter);
}

DynamicResponseFilter& LLMPromptData::createLimits()
{
	if (m_pFilter == NULL)
	{
		m_pFilter = new DynamicResponseFilter();
		m_pFilter->setDefaultValues();
	}
	return *m_pFilter;
}

DynamicResponseFilter const* LLMPromptData::getLimits()
{
	DynamicResponseData const* pointer = m_pFilter;
	SAFE_DELETE(m_pFilter);
	return pointer;
}

DynamicResponseData const* LLMResultData::getData()
{
	DynamicResponseData* pointer = m_pResultText;
	SAFE_DELETE(m_pResultText);
	return pointer;
}

LLMResultData::~LLMResultData()
{
	SAFE_DELETE(m_pFilter);
	SAFE_DELETE(m_pResultText);
}

DynamicResponseData* LLMResultData::getData()
{
	DynamicResponseData* pointer = m_pResultText;
	SAFE_DELETE(m_pResultText);
	return pointer;
}

void LLMResultData::setText(CvString const& szText)
{
	if (m_pResultText == NULL)
	{
		m_pResultText = new DynamicResponseData();
	}
	m_pResultText->setText(szText);
}

DynamicResponseGroup::~DynamicResponseGroup()
{
	for (int i = 0; i < (int)data.size(); i++)
	{
		SAFE_DELETE(data[i]);
	}
	data.clear();
}

std::string const& DynamicResponseData::getText() const
{
	return szResponseText;
}

void DynamicResponseData::setText(CvString const& szText)
{
	szResponseText = szText;
}

void DynamicResponseFilter::setCivilizationTypeEnabled(CivilizationTypes eCiv)
{
	if (abActiveCivilizations.empty() || eCiv == NO_CIVILIZATION || eCiv >= GC.getNumCivilizationInfos())
	{
		return;
	}
	abActiveCivilizations[eCiv] = static_cast<char>(true);
}

void DynamicResponseFilter::setLeaderHeadTypeEnabled(LeaderHeadTypes eLeader)
{
	if (abActiveLeaders.empty() || eLeader == NO_LEADER || eLeader >= GC.getNumLeaderHeadInfos())
	{
		return;
	}
	abActiveLeaders[eLeader] = static_cast<char>(true);
}

void DynamicResponseFilter::setAttitudeTypeEnabled(AttitudeTypes eAttitude)
{
	if (abActiveAttitudes.empty() || eAttitude == NO_ATTITUDE || eAttitude >= NUM_ATTITUDE_TYPES)
	{
		return;
	}
	abActiveAttitudes[eAttitude] = static_cast<char>(true);
}

void DynamicResponseFilter::setDiplomacyPowerTypeEnabled(DiplomacyPowerTypes ePower)
{
	if (abActivePowers.empty() || ePower == NO_DIPLOMACYPOWER || ePower >= NUM_DIPLOMACYPOWER_TYPES)
	{
		return;
	}
	abActivePowers[ePower] = static_cast<char>(true);
}

int DynamicResponse::getNumResponseGroups() const
{
	return (int)m_aResponseGroups.size();
}

void DynamicResponse::initNewResponseGroup()
{
	m_aResponseGroups.resize(getNumResponseGroups() + 1);
}

int DynamicResponse::getFirstFreeResponseGroup() const
{
	int i = -1;
	for (int iGroupIndex = 0; iGroupIndex < getNumResponseGroups(); iGroupIndex++)
	{
		int iNumDiploTexts = getNumDiplomacyText(iGroupIndex);
		if (iNumDiploTexts > 0)
		{
			int iGroupResponseUsedCount = 0;
			for (int iResponseIndex = 0; iResponseIndex < iNumDiploTexts; iResponseIndex++)
			{
				if (m_aResponseGroups[iGroupIndex].data[iResponseIndex] != NULL)
				{
					if (m_aResponseGroups[iGroupIndex].data[iResponseIndex]->isAtUsageLimit())
					{
						iGroupResponseUsedCount++;
					}
					else continue;
				}
				else continue;
			}
			if (iGroupResponseUsedCount != iNumDiploTexts)
			{
				i = iGroupIndex;
				break;
			}
			else continue;
		}
		else
		{
			i = iGroupIndex;
			break;
		}
	}
	return i;
}

DiploCommentTypes DynamicResponse::getCommentType() const
{
	return m_eType;
}

bool DynamicResponse::getCivilizationTypes(int iGroupIndex, CivilizationTypes eCiv) const
{
	if (iGroupIndex < 0 || iGroupIndex >= getNumResponseGroups())
	{
		return false;
	}
	// If the filter vector is empty, treat it as unconstrained (pass-through)
	if (!m_aResponseGroups[iGroupIndex].limits.abActiveCivilizations.empty() && !(static_cast<bool>(m_aResponseGroups[iGroupIndex].limits.abActiveCivilizations[eCiv])))
	{
		return false; 
	}
	return true; // All active filter flags matched successfully!
}

bool DynamicResponse::getLeaderHeadTypes(int iGroupIndex, LeaderHeadTypes eLeader) const
{
	if (iGroupIndex < 0 || iGroupIndex >= getNumResponseGroups())
	{
		return false;
	}
	// If the filter vector is empty, treat it as unconstrained (pass-through)
	if (!m_aResponseGroups[iGroupIndex].limits.abActiveLeaders.empty() && !(static_cast<bool>(m_aResponseGroups[iGroupIndex].limits.abActiveLeaders[eLeader])))
	{
		return false;
	}
	return true; // All active filter flags matched successfully!
}

bool DynamicResponse::getAttitudeTypes(int iGroupIndex, AttitudeTypes eAttitude) const
{
	if (iGroupIndex < 0 || iGroupIndex >= getNumResponseGroups())
	{
		return false;
	}
	// If the filter vector is empty, treat it as unconstrained (pass-through)
	if (!m_aResponseGroups[iGroupIndex].limits.abActiveAttitudes.empty() && !(static_cast<bool>(m_aResponseGroups[iGroupIndex].limits.abActiveAttitudes[eAttitude])))
	{
		return false;
	}
	return true; // All active filter flags matched successfully!
}

bool DynamicResponse::getDiplomacyPowerTypes(int iGroupIndex, DiplomacyPowerTypes ePower) const
{
	if (iGroupIndex < 0 || iGroupIndex >= getNumResponseGroups())
	{
		return false;
	}
	// If the filter vector is empty, treat it as unconstrained (pass-through)
	if (!m_aResponseGroups[iGroupIndex].limits.abActivePowers.empty() && !(static_cast<bool>(m_aResponseGroups[iGroupIndex].limits.abActivePowers[ePower])))
	{
		return false;
	}
	return true; // All active filter flags matched successfully!
}

int DynamicResponse::getNumDiplomacyText(int iGroupIndex) const
{
	if (iGroupIndex < 0 || iGroupIndex >= getNumResponseGroups())
	{
		return 0;
	}
	return (int)m_aResponseGroups[iGroupIndex].data.size();
}

std::string const& DynamicResponse::getDiplomacyText(int iGroupIndex, int iVariant) const
{
	if ((iGroupIndex >= 0 && iGroupIndex < getNumResponseGroups())
		&& (iVariant >= 0 && iVariant < getNumDiplomacyText(iVariant)))
	{
		return ((m_aResponseGroups[iGroupIndex].data[iVariant] != NULL) ? m_aResponseGroups[iGroupIndex].data[iVariant]->getText() : "");
	}
	return "";
}

void DynamicResponse::updateDynamicResponseLifetime(int iGroupIndex, int iVariant)
{
	if ((iGroupIndex >= 0 && iGroupIndex < getNumResponseGroups())
		&& (iVariant >= 0 && iVariant < getNumDiplomacyText(iVariant)))
	{
		std::vector<DynamicResponseData*>& kVector = m_aResponseGroups[iGroupIndex].data;
		if (kVector[iVariant] != NULL)
		{
			if (!kVector[iVariant]->isAtUsageLimit())
			{
				kVector[iVariant]->increaseUseCount();
			}
			else
			{
				SAFE_DELETE(kVector[iVariant]);
				kVector.erase(kVector.begin() + iVariant);
			}
		}
	}
}

void DynamicResponse::setDiplomacyText(LLMResultData const& kResult)
{
	/* XANA (warning):
	DO NOT USE FIRAXIS GLOBAL FUNCTIONS OR ASSERTIONS HERE
	THIS OPERATION WILL BE CALLED VIA A BACKGROUND THREAD
	ATTEMPTING TO DO SO WILL CRASH THE GAME */
	if (kResult.getIndex() < 0 || kResult.getIndex() >= getNumResponseGroups())
	{
		return;
	}
	int const iGroupIndex = kResult.getIndex();
	std::vector<DynamicResponseData*>& kVector = m_aResponseGroups[iGroupIndex].data;
	int const iTextIndex = getNumDiplomacyText(iGroupIndex);
	if (kResult.getLimits() != NULL)
	{
		m_aResponseGroups[iGroupIndex].limits = *kResult.getLimits();
	}
	kVector.resize(iTextIndex + 1);
	kVector[iTextIndex] = kResult.getData();
}
// XANA: 05-23-2026 LLM Text Diplomacy Generation