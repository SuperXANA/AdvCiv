// Python wrapper class for CySelectionGroup
#include "CvGameCoreDLL.h"
#include "CySelectionGroup.h"
#include "CvSelectionGroupAI.h"
#include "CyArea.h"
#include "CvArea.h"
#include "CvPlot.h"


CySelectionGroup::CySelectionGroup() : m_pSelectionGroup(NULL) {}

CySelectionGroup::CySelectionGroup(CvSelectionGroup* pSelectionGroup) : m_pSelectionGroup(pSelectionGroup) {}
// advc.003y: (see CyCity.cpp)
CySelectionGroup::CySelectionGroup(CvSelectionGroup const& kSelectionGroup) :
	m_pSelectionGroup(const_cast<CvSelectionGroup*>(&kSelectionGroup)) {}

void CySelectionGroup::pushMission(MissionTypes eMission, int iData1, int iData2, int iFlags, bool bAppend, bool bManual, MissionAITypes eMissionAI, CyPlot* pMissionAIPlot, CyUnit* pMissionAIUnit)
{
	if (m_pSelectionGroup)
	{
		return m_pSelectionGroup->pushMission(eMission, iData1, iData2,
				(MovementFlags)iFlags, bAppend, bManual, eMissionAI,
				pMissionAIPlot->getPlot(), pMissionAIUnit->getUnit());
	}
}

void CySelectionGroup::pushMoveToMission(int iX, int iY)
{
	if (m_pSelectionGroup)
		return m_pSelectionGroup->pushMission(MISSION_MOVE_TO, iX, iY);
}

void CySelectionGroup::popMission()
{
	if (m_pSelectionGroup)
		return m_pSelectionGroup->popMission();
}

CyPlot* CySelectionGroup::lastMissionPlot()
{
	return m_pSelectionGroup ? new CyPlot(m_pSelectionGroup->lastMissionPlot()) : NULL;
}

bool CySelectionGroup::canStartMission(int iMission, int iData1, int iData2, CyPlot* pPlot, bool bTestVisible)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canStartMission((MissionTypes)iMission,
			iData1, iData2, pPlot->getPlot(), bTestVisible) : false;
}

bool CySelectionGroup::canDoInterfaceMode(InterfaceModeTypes eInterfaceMode)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canDoInterfaceMode(eInterfaceMode) : false;
}

bool CySelectionGroup::canDoInterfaceModeAt(InterfaceModeTypes eInterfaceMode, CyPlot* pPlot)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canDoInterfaceModeAt(eInterfaceMode, pPlot->getPlot()) : false;
}

bool CySelectionGroup::canDoCommand(CommandTypes eCommand, int iData1, int iData2, bool bTestVisible)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canDoCommand(eCommand, iData1, iData2, bTestVisible) : false;
}

bool CySelectionGroup::isHuman()
{
	return m_pSelectionGroup ? m_pSelectionGroup->isHuman() : false;
}

int CySelectionGroup::baseMoves()
{
	return m_pSelectionGroup ? m_pSelectionGroup->baseMoves() : -1;
}

bool CySelectionGroup::canAllMove()
{
	return m_pSelectionGroup ? m_pSelectionGroup->canAllMove() : false;
}

bool CySelectionGroup::isWaiting()
{
	return m_pSelectionGroup ? m_pSelectionGroup->isWaiting() : false;
}

bool CySelectionGroup::isFull()
{
	return m_pSelectionGroup ? m_pSelectionGroup->isFull() : false;
}

bool CySelectionGroup::hasCargo()
{
	return m_pSelectionGroup ? m_pSelectionGroup->hasCargo() : false;
}

bool CySelectionGroup::canAnyMove()
{
	return m_pSelectionGroup ? m_pSelectionGroup->canAnyMove() : false;
}

bool CySelectionGroup::hasMoved()
{
	return m_pSelectionGroup ? m_pSelectionGroup->hasMoved() : false;
}

bool CySelectionGroup::canEnterTerritory(int /*TeamTypes*/ eTeam, bool bIgnoreRightOfPassage)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canEnterTerritory((TeamTypes) eTeam, bIgnoreRightOfPassage) : false;
}

bool CySelectionGroup::canEnterArea(int /*TeamTypes*/ eTeam, CyArea* pArea, bool bIgnoreRightOfPassage)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canEnterArea((TeamTypes) eTeam, pArea->getArea(), bIgnoreRightOfPassage) : false;
}

bool CySelectionGroup::canMoveInto(CyPlot* pPlot, bool bAttack)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canMoveInto(*pPlot->getPlot(), bAttack) : false;
}

bool CySelectionGroup::canMoveOrAttackInto(CyPlot* pPlot, bool bDeclareWar)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canMoveOrAttackInto(pPlot->getPlot(), bDeclareWar) : false;
}

bool CySelectionGroup::canMoveThrough(CyPlot* pPlot)
{
	return m_pSelectionGroup ? m_pSelectionGroup->canMoveThrough(*pPlot->getPlot()) : false;
}

bool CySelectionGroup::canFight()
{
	return m_pSelectionGroup ? m_pSelectionGroup->canFight() : false;
}

bool CySelectionGroup::canDefend()
{
	return m_pSelectionGroup ? m_pSelectionGroup->canDefend() : false;
}

bool CySelectionGroup::alwaysInvisible()
{
	return m_pSelectionGroup ? m_pSelectionGroup->alwaysInvisible() : false;
}

bool CySelectionGroup::isInvisible(int /*TeamTypes*/ eTeam)
{
	return m_pSelectionGroup ? m_pSelectionGroup->isInvisible((TeamTypes) eTeam) : false;
}

int CySelectionGroup::countNumUnitAIType(UnitAITypes eUnitAI)
{
	return m_pSelectionGroup ? m_pSelectionGroup->countNumUnitAIType(eUnitAI) : -1;
}

bool CySelectionGroup::hasWorker()
{
	return m_pSelectionGroup ? m_pSelectionGroup->hasWorker() : false;
}
// BETTER_BTS_AI_MOD, General AI, 11/30/08, jdog5000:
bool CySelectionGroup::isStranded()
{
	return m_pSelectionGroup ? m_pSelectionGroup->AI().AI_isStranded() : false;
}

bool CySelectionGroup::at(int iX, int iY)
{
	return m_pSelectionGroup ? m_pSelectionGroup->at(iX, iY) : false;
}

bool CySelectionGroup::atPlot(CyPlot* pPlot)
{
	return m_pSelectionGroup ? m_pSelectionGroup->atPlot(pPlot->getPlot()) : false;
}

CyPlot* CySelectionGroup::plot()
{
	return m_pSelectionGroup ? new CyPlot(m_pSelectionGroup->plot()) : NULL;
}

CyArea* CySelectionGroup::area()
{
	return m_pSelectionGroup ? new CyArea(m_pSelectionGroup->area()) : NULL;
}

int /*RouteTypes*/ CySelectionGroup::getBestBuildRoute(CyPlot* pPlot, BuildTypes* peBestBuild)
{
	if (m_pSelectionGroup == NULL)
		return NO_ROUTE;
	// <advc> Pass by reference
	CvPlot const* p = pPlot->getPlot();
	if (p == NULL)
		return NO_ROUTE; // </advc>
	return m_pSelectionGroup->getBestBuildRoute(*p, peBestBuild);
}

bool CySelectionGroup::isAmphibPlot(CyPlot* pPlot)
{
	return m_pSelectionGroup ? m_pSelectionGroup->isAmphibPlot(pPlot->getPlot()) : false;
}
bool CySelectionGroup::readyToSelect(bool bAny)
{
	return m_pSelectionGroup ? m_pSelectionGroup->readyToSelect(bAny) : false;
}

bool CySelectionGroup::readyToMove(bool bAny)
{
	return m_pSelectionGroup ? m_pSelectionGroup->readyToMove(bAny) : false;
}

bool CySelectionGroup::readyToAuto()
{
	return m_pSelectionGroup ? m_pSelectionGroup->readyToAuto() : false;
}

int CySelectionGroup::getID()
{
	return m_pSelectionGroup ? m_pSelectionGroup->getID() : -1;
}

int /*PlayerTypes*/ CySelectionGroup::getOwner()
{
	return m_pSelectionGroup ? m_pSelectionGroup->getOwner() : -1;
}

int /*TeamTypes*/ CySelectionGroup::getTeam()
{
	return m_pSelectionGroup ? (TeamTypes) m_pSelectionGroup->getTeam() : -1;
}

int /*ActivityTypes*/ CySelectionGroup::getActivityType()
{
	return m_pSelectionGroup ? (ActivityTypes) m_pSelectionGroup->getActivityType() : -1;
}

void CySelectionGroup::setActivityType(int /*ActivityTypes*/ eNewValue)
{
	if (m_pSelectionGroup)
		m_pSelectionGroup->setActivityType((ActivityTypes) eNewValue);
}

int /*AutomateTypes*/ CySelectionGroup::getAutomateType()
{
	return m_pSelectionGroup ? (AutomateTypes) m_pSelectionGroup->getAutomateType() : -1;
}

bool CySelectionGroup::isAutomated()
{
	return m_pSelectionGroup ? m_pSelectionGroup->isAutomated() : false;
}

void CySelectionGroup::setAutomateType(int /*AutomateTypes*/ eNewValue)
{
	if (m_pSelectionGroup)
		m_pSelectionGroup->setAutomateType((AutomateTypes) eNewValue);
}

CyPlot* CySelectionGroup::getPathFirstPlot()
{
	return m_pSelectionGroup ? new CyPlot(m_pSelectionGroup->getPathFirstPlot()) : NULL;
}

CyPlot* CySelectionGroup::getPathEndTurnPlot()
{
	return m_pSelectionGroup ? new CyPlot(m_pSelectionGroup->getPathEndTurnPlot()) : NULL;
}

bool CySelectionGroup::generatePath(CyPlot* pFromPlot, CyPlot* pToPlot, int iFlags,
	bool bReuse, int* piPathTurns)
{
	if (m_pSelectionGroup == NULL ||
		pFromPlot->getPlot() == NULL || pToPlot->getPlot() == NULL)
	{
		return false;
	}
	return m_pSelectionGroup->generatePath(
			*pFromPlot->getPlot(), *pToPlot->getPlot(),
			(MovementFlags)iFlags, bReuse, piPathTurns);
}

int CySelectionGroup::getNumUnits()
{
	return m_pSelectionGroup ? m_pSelectionGroup->getNumUnits() : -1;
}

void CySelectionGroup::clearMissionQueue()
{
	if (m_pSelectionGroup)
		m_pSelectionGroup->clearMissionQueue();
}

int CySelectionGroup::getLengthMissionQueue()
{
	return m_pSelectionGroup ? m_pSelectionGroup->getLengthMissionQueue() : -1;
}

MissionData* CySelectionGroup::getMissionFromQueue(int iIndex)
{
	return m_pSelectionGroup ? m_pSelectionGroup->getMissionFromQueue(iIndex) : NULL;
}

CyUnit* CySelectionGroup::getHeadUnit()
{
	return m_pSelectionGroup ? new CyUnit(m_pSelectionGroup->getHeadUnit()) : NULL;
}

CyUnit* CySelectionGroup::getUnitAt(int iIndex)
{
	if (m_pSelectionGroup == NULL)
		return NULL;
	// <advc> Moved from CvSelectionGroup. Foolproofing should be handled here.
	if (iIndex < 0 || m_pSelectionGroup->getNumUnits() <= iIndex)
		return NULL; // </advc>
	return new CyUnit(m_pSelectionGroup->getUnitAt(iIndex));
}

int CySelectionGroup::getMissionType(int iNode)
{
	return m_pSelectionGroup ? m_pSelectionGroup->getMissionType(iNode) : -1;
}

int CySelectionGroup::getMissionData1(int iNode)
{
	return m_pSelectionGroup ? m_pSelectionGroup->getMissionData1(iNode) : -1;
}

int CySelectionGroup::getMissionData2(int iNode)
{
	return m_pSelectionGroup ? m_pSelectionGroup->getMissionData2(iNode) : -1;
}

// XANA: 09-26-2026 AI Strategy Party System
CyPartyGroup::CyPartyGroup() : m_pPartyGroup(NULL) {}

CyPartyGroup::CyPartyGroup(CyPartyGroup* pPartyGroup) : m_pPartyGroup(pPartyGroup) {}
// advc.003y: (see CyCity.cpp)
CyPartyGroup::CyPartyGroup(CyPartyGroup const& kPartyGroup) : m_pPartyGroup(const_cast<CyPartyGroup*>(&kPartyGroup)) {}

void CyPartyGroup::pushMission(MissionTypes eMission, int iData1, int iData2, int iFlags, bool bAppend, bool bManual, MissionAITypes eMissionAI, CyPlot* pMissionAIPlot, CyUnit* pMissionAIUnit)
{
	if (m_pPartyGroup)
	{
		return m_pPartyGroup->pushMission(eMission, iData1, iData2,
				(MovementFlags)iFlags, bAppend, bManual, eMissionAI,
				pMissionAIPlot->getPlot(), pMissionAIUnit->getUnit());
	}
}

void CyPartyGroup::pushMoveToMission(int iX, int iY)
{
	if (m_pPartyGroup)
		return m_pSelectionGroup->pushMission(MISSION_MOVE_TO, iX, iY);
}

void CyPartyGroup::popMission()
{
	if (m_pPartyGroup)
		return m_pSelectionGroup->popMission();
}

CyPlot* CyPartyGroup::lastMissionPlot()
{
	return m_pPartyGroup ? new CyPlot(m_pSelectionGroup->lastMissionPlot()) : NULL;
}

bool CyPartyGroup::canStartMission(int iMission, int iData1, int iData2, CyPlot* pPlot, bool bTestVisible)
{
	return m_pPartyGroup ? m_pSelectionGroup->canStartMission((MissionTypes)iMission,
			iData1, iData2, pPlot->getPlot(), bTestVisible) : false;
}

bool CyPartyGroup::isHuman()
{
	return m_pPartyGroup ? m_pPartyGroup->isHuman() : false;
}

bool CyPartyGroup::isWaiting()
{
	return m_pPartyGroup ? m_pPartyGroup->isWaiting() : false;
}

bool CyPartyGroup::isFull()
{
	return m_pPartyGroup ? m_pPartyGroup->isFull() : false;
}

bool CyPartyGroup::hasCargo()
{
	return m_pPartyGroup ? m_pPartyGroup->hasCargo() : false;
}

bool CyPartyGroup::canFight()
{
	return m_pPartyGroup ? m_pPartyGroup->canFight() : false;
}

bool CyPartyGroup::canDefend()
{
	return m_pPartyGroup ? m_pPartyGroup->canDefend() : false;
}

int CyPartyGroup::countNumUnitAIType(UnitAITypes eUnitAI)
{
	return m_pPartyGroup ? m_pPartyGroup->countNumUnitAIType(eUnitAI) : -1;
}

int CyPartyGroup::getID()
{
	return m_pPartyGroup ? m_pPartyGroup->getID() : -1;
}

int /*PlayerTypes*/ CyPartyGroup::getOwner()
{
	return m_pPartyGroup ? m_pPartyGroup->getOwner() : -1;
}

int /*TeamTypes*/ CyPartyGroup::getTeam()
{
	return m_pPartyGroup ? (TeamTypes) m_pPartyGroup->getTeam() : -1;
}

int CyPartyGroup::getNumUnits()
{
	return m_pPartyGroup ? m_pPartyGroup->getNumUnits() : -1;
}

void CyPartyGroup::clearMissionQueue()
{
	if (m_pPartyGroup)
		m_pPartyGroup->clearMissionQueue();
}

int CyPartyGroup::getLengthMissionQueue()
{
	return m_pPartyGroup ? m_pPartyGroup->getLengthMissionQueue() : -1;
}

MissionData* CyPartyGroup::getMissionFromQueue(int iIndex)
{
	return m_pPartyGroup ? m_pPartyGroup->getMissionFromQueue(iIndex) : NULL;
}

CyUnit* CyPartyGroup::getHeadUnit()
{
	return m_pPartyGroup ? new CyUnit(m_pPartyGroup->getHeadUnit()) : NULL;
}

CyUnit* CyPartyGroup::getUnitAt(int iIndex)
{
	if (m_pPartyGroup == NULL)
		return NULL;
	// <advc> Moved from CvSelectionGroup. Foolproofing should be handled here.
	if (iIndex < 0 || m_pPartyGroup->getNumUnits() <= iIndex)
		return NULL; // </advc>
	return new CyUnit(m_pPartyGroup->getUnitAt(iIndex));
}

int CyPartyGroup::getMissionType(int iNode)
{
	return m_pPartyGroup ? m_pPartyGroup->getMissionType(iNode) : -1;
}

int CyPartyGroup::getMissionData1(int iNode)
{
	return m_pPartyGroup ? m_pPartyGroup->getMissionData1(iNode) : -1;
}

int CyPartyGroup::getMissionData2(int iNode)
{
	return m_pPartyGroup ? m_pPartyGroup->getMissionData2(iNode) : -1;
}
// XANA: 09-26-2026 AI Strategy Party System
