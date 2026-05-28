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
	
	// Called during game startup to build diplomacy comment types enumeration map
	void updateUniqueDiplomacyTypesMap(const CvString& szType);

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
	
	std::vector<CvString> m_aKnownDiploCommentTags;
	std::vector<DiploCommentTypes> m_aKnownDiploCommentTypes;
	
	void setInitialItems();
	void copyActiveResponsesToStaging(PlayerTypes ePlayer);
	
	void clearStagingArea(PlayerTypes eAIPlayer);
	void clearActiveResponses(PlayerTypes eAIPlayer);
	
	bool getCivilizationTypes(PlayerTypes eAIPlayer, int iIndex, CivilizationTypes eCiv, DiploCommentTypes eComment) const;
	bool getLeaderHeadTypes(PlayerTypes eAIPlayer, int iIndex, LeaderHeadTypes eLeader, DiploCommentTypes eComment) const;
	bool getAttitudeTypes(PlayerTypes eAIPlayer, int iIndex, AttitudeTypes eAttitude, DiploCommentTypes eComment) const;
	bool getDiplomacyPowerTypes(PlayerTypes eAIPlayer, int iIndex, DiplomacyPowerTypes ePower, DiploCommentTypes eComment) const;
	
	int getResponseIndexForDiploComment(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const;
};

#define DIPLOMGR CvDynamicDiploManager::getConstInstance() // XANA (note): Game thread will be mostly reading from this class, mark it const for safety!

#endif