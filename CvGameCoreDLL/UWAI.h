#pragma once

#ifndef UWAI_H
#define UWAI_H

// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
#include "WarUtilityAspectAI.h"
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
class FDataStreamBase;

/*  advc.104: AI functionality for decisions on war and peace.
	Main class of the Utility-Based War AI component (UWAI).
	Instead of making lots of additions to CvTeamAI and CvPlayerAI, I've put the
	new functions in classes UWAI::Team and UWAI::Player, which are
	defined in UWAIAgent.h. The outer class UWAI shared by Team and Player is
	for overarching stuff that would otherwise fit into CvGameAI or
	CvGameCoreUtils. An instance is accessible through the macro "getUWAI".

	The main function for war planning is UWAI::Team::doWar. */

// The parentheses are unnecessary, but I think it's more intuitive this way.
#define getUWAI() GC.AI_getGame().uwai()


/*	Setting this to 1 should remove almost all runtime overhead from logging in
	optimized release builds. The overhead should be pretty small in any case,
	so I'd rather keep logging available (via an XML switch) in releases. */
#define DISABLE_UWAI_REPORT 0

class UWAI : private boost::noncopyable
{
public:
	// Nested classes; defined in UWAIAgent.h.
	class Player;
	class Team;

	UWAI();
	void invalidateUICache();
	// When a colonial vassal is created
	void initNewPlayerInGame(PlayerTypes eNewPlayer);
	// When the colonial vassal has received a capital and tech
	void processNewPlayerInGame(PlayerTypes eNewPlayer);
	/*  true if UWAI fully enabled, making all decisions, otherwise false.
		If bInBackground is set, then true if UWAI is running only in the background
		(through an XML switch), but false if UWAI fully enabled or fully disabled. */
	bool isEnabled(bool bInBackground = false) const; // Exposed to Python via CyGame::useKModAI
	void setUseLegacyAI(bool b);
	void setInBackground(bool b);
	void read(FDataStreamBase* pStream);
	void write(FDataStreamBase* pStream) const;
	int maxLandDist() const { return maxSeaDist() - 1; }
	int maxSeaDist() const;
	bool isReady() const;

	int preparationTimeLimited() const { return 8; }
	int preparationTimeLimitedNaval() const { return 10; }
	int preparationTimeTotal() const { return 15; }
	int preparationTimeTotalNaval() const { return 20; }

	void doXML();
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
	scaled aspectWeight(WarUtilityAspectAITypes eAspect) const
	{
		FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), eAspect);
		return per100(GC.getInfo(eAspect).getAIWeight());
	}
	char const* aspectName(WarUtilityAspectAITypes eAspect) const
	{
		FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), eAspect);
		return GC.getInfo(eAspect).getDescription();
	}
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights

private:
	// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
	/*
	std::vector<int> m_aiXmlWeights;
	std::vector<char const*> m_aszAspectNames;
	*/
	// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
	bool m_bEnabled; // false iff Legacy AI enabled through game option
	bool m_bInBackground; // status of background switch in XML

	void applyPersonalityWeight();
};

#endif
