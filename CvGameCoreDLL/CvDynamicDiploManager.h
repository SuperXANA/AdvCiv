#pragma once

#ifndef CV_DYNAMIC_DIPLO_MANAGER_H
#define CV_DYNAMIC_DIPLO_MANAGER_H

#include "CvGameCoreDLL.h"
	
class CvDynamicDiploManager
{
public:
	static void init();
	static void uninit();

	// Called by WinINet thread to safely drop responses into staging area for synchronization
	static void pushNewResponse(PlayerTypes eAIPlayer, DynamicResponse const& kResponse);

	// Called at the Turn Boundary (setTurnActive) to promote staging to active during synchronization
	static void updateCache();

	// Called by Python/CvDiplomacy to fetch data for the local UI
	static int getNumResponses(PlayerTypes eAIPlayer) const;
	static bool isResponseForCivilization(PlayerTypes eAIPlayer, int iIndex) const;
	static bool isResponseForLeaderHead(PlayerTypes eAIPlayer, int iIndex) const;
	static bool isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const;
	static bool isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const;
	static int getNumDiplomacyText(PlayerTypes eAIPlayer, int iIndex) const;
	static const char* getDiplomacyText(PlayerTypes eAIPlayer, int iIndex, int iVariant) const;

private:
	// Static lightweight unique class - no creation, no copying, no assignment
	CvDynamicDiploManager() {}
	CvDynamicDiploManager(CvDynamicDiploManager const& kOther);
	CvDynamicDiploManager& operator=(CvDynamicDiploManager const& kOther)
	
	static CvCriticalSection m_CS;
	
	typedef stdext::hash_map<PlayerTypes, std::vector<DynamicResponse> > DynamicResponseMap;
	
	static DynamicResponseMap m_stagingArea; // temporary
	static DynamicResponseMap m_activeDiploResponses; // not serialized
	static bool m_bInitialized;
	
	static void clearStagingArea(PlayerTypes eAIPlayer);
	static void clearActiveResponses(PlayerTypes eAIPlayer);
	
	static bool getCivilizationTypes(PlayerTypes eAIPlayer, int iIndex, CivilizationTypes eCiv) const;
	static bool getLeaderHeadTypes(PlayerTypes eAIPlayer, int iIndex, LeaderHeadTypes eLeader) const;
	static bool getAttitudeTypes(PlayerTypes eAIPlayer, int iIndex, AttitudeTypes eAttitude) const;
	static bool getDiplomacyPowerTypes(PlayerTypes eAIPlayer, int iIndex, DiplomacyPowerTypes ePower) const;
};

#endif