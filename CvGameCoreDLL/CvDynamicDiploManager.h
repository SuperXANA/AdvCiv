#pragma once

#ifndef CV_DYNAMIC_DIPLO_MANAGER_H
#define CV_DYNAMIC_DIPLO_MANAGER_H

#include <vector>
#include <hash_map>
#include "CvEnums.h"
#include "CvStructs.h"

typedef stdext::hash_map<int /* PlayerTypes */, std::vector<DynamicResponse> > DynamicResponseMap;

class CvDynamicDiploManager
{
public:
	static CvDynamicDiploManager& getInstance(); // XANA (note): WinINet - access for writing AND reading permissions!
	static CvDynamicDiploManager const& getConstInstance() { return getInstance(); } // XANA (note): main game thread - acccess for reading permissions ONLY!

	void init();
	void reset();
	void uninit() { reset(); }

	// Called by WinINet thread to safely drop responses into staging area for synchronization
	void pushNewResponse(PlayerTypes eAIPlayer, DynamicResponse const& kResponse);

	// Called at the Turn Boundary (setTurnActive) to promote staging to active during synchronization
	void updateCache();

	// Called by Python/CvDiplomacy to fetch data for the local UI
	int getNumResponses(PlayerTypes eAIPlayer) const;
	bool isResponseForCivilization(PlayerTypes eAIPlayer, int iIndex) const;
	bool isResponseForLeaderHead(PlayerTypes eAIPlayer, int iIndex) const;
	bool isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const;
	bool isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const;
	int getNumDiplomacyText(PlayerTypes eAIPlayer, int iIndex) const;
	const char* getDiplomacyText(PlayerTypes eAIPlayer, int iIndex, int iVariant) const;

private:
	// Static lightweight unique class - no creation, no copying, no assignment, no deletion
	CvDynamicDiploManager() {}
	~CvDynamicDiploManager() {}
	CvDynamicDiploManager(CvDynamicDiploManager const& kOther);
	CvDynamicDiploManager& operator=(CvDynamicDiploManager const& kOther)
	
	CvCriticalSection m_CS;
	
	DynamicResponseMap m_stagingArea; // temporary
	DynamicResponseMap m_activeDiploResponses; // not serialized
	bool m_bInitialized;
	
	void clearStagingArea(PlayerTypes eAIPlayer);
	void clearActiveResponses(PlayerTypes eAIPlayer);
	
	bool getCivilizationTypes(PlayerTypes eAIPlayer, int iIndex, CivilizationTypes eCiv) const;
	bool getLeaderHeadTypes(PlayerTypes eAIPlayer, int iIndex, LeaderHeadTypes eLeader) const;
	bool getAttitudeTypes(PlayerTypes eAIPlayer, int iIndex, AttitudeTypes eAttitude) const;
	bool getDiplomacyPowerTypes(PlayerTypes eAIPlayer, int iIndex, DiplomacyPowerTypes ePower) const;
};

#define DIPLOMGR CvDynamicDiploManager::getConstInstance() // XANA (note): Game thread will be mostly reading from this class, mark it const for safety!

#endif