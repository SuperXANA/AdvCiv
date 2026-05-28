#pragma once

#ifndef CV_DYNAMIC_DIPLO_MANAGER_H
#define CV_DYNAMIC_DIPLO_MANAGER_H

#include <vector>
#include <hash_map>
#include <algorithm>
#include "CvEnums.h"
#include "CvStructs.h"
#include "CvString.h"

typedef stdext::hash_map<int /* PlayerTypes */, std::vector<DynamicResponse> > DynamicResponseMap;

class CvDynamicDiploManager
{
public:
	static CvDynamicDiploManager& getInstance(); // XANA (note): WinINet - access for writing AND reading permissions!
	static CvDynamicDiploManager const& getConstInstance() { return getInstance(); } // XANA (note): main game thread - acccess for reading permissions ONLY!

	void init();
	void reset();
	void uninit();

	// Called by WinINet thread to safely drop responses into staging area for synchronization
	void updateAIPlayerAvailableResponses(LLMResultData const& kResult);

	// Called at the Turn Boundary (setTurnActive) to promote staging to active during synchronization
	void updateActiveResponseCache(PlayerTypes ePlayer);

	// Called by Python/CvDiplomacy to fetch data for the local UI
	int getNumResponses(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const;
	bool isResponseForCivilization(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const;
	bool isResponseForLeaderHead(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const;
	bool isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const;
	bool isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const;
	int getNumDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const;
	const char* getDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex, int iVariant) const;

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
	
	void setInitialItems();
	void copyActiveResponsesToStaging(PlayerTypes ePlayer);
	
	void clearStagingArea(PlayerTypes eAIPlayer);
	void clearActiveResponses(PlayerTypes eAIPlayer);
	
	bool getCivilizationTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, CivilizationTypes eCiv, int iGroupIndex) const;
	bool getLeaderHeadTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, LeaderHeadTypes eLeader, int iGroupIndex) const;
	bool getAttitudeTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, AttitudeTypes eAttitude, int iGroupIndex const;
	bool getDiplomacyPowerTypesPlayerTypes eAIPlayer, DiploCommentTypes eComment, DiplomacyPowerTypes ePower, int iGroupIndex) const;
	
	int getResponseIndexForDiploComment(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const;
};

#define DIPLOMGR CvDynamicDiploManager::getConstInstance() // XANA (note): Game thread will be mostly reading from this class, mark it const for safety!

#endif