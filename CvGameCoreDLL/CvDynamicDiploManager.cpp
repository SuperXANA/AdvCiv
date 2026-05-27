#include "CvGameCoreDLL.h"
#include "CvDynamicDiploManager.h"

CvDynamicDiploManager& CvDynamicDiploManager::getInstance()
{
	static CvDynamicDiploManager singleton;
	return singleton;
}

void CvDynamicDiploManager::init()
{
	if (!m_bInitialized)
	{
		m_stagingArea.resize(MAX_PLAYERS);
		m_activeDiploResponses.resize(MAX_PLAYERS);
		m_bInitialized = true;
	}
	if (m_bInitialized)
	{
		CvFunctionMutex lock(m_CS);
		{
			setInitialItems();
		}
	}
}

void CvDynamicDiploManager::reset()
{
	uninit();
	init();
}

void CvDynamicDiploManager::uninit()
{
	CvFunctionMutex lock(m_CS);
	{
		if (m_bInitialized)
		{
			FOR_EACH_ENUM(Player)
			{
				clearStagingArea(eLoopPlayer);
				clearActiveResponses(eLoopPlayer);
			}
			m_stagingArea.clear();
			m_activeDiploResponses.clear();
			m_bInitialized = false;
		}
	}
}

void CvDynamicDiploManager::updateUniqueDiplomacyTypesMap(const CvString& szType)
{
	std::vector<CvString>::const_iterator it = std::find(m_aKnownDiploCommentTags.begin(), m_aKnownDiploCommentTags.end(), szType);
	if (it == m_aKnownDiploCommentTags.end())
	{
		m_aKnownDiploCommentTags.push_back(szType);
	}
}

void CvDynamicDiploManager::setInitialItems()
{
	if ((int)m_aKnownDiploCommentTags.size() > 0)
	{
		for (int iTag = 0; iTag < (int)m_aKnownDiploCommentTags.size(); iTag++)
		{
			DiplomacyCommentTypes const eComment = (DiplomacyCommentTypes)GC.getInfoTypeForString(m_aKnownDiploCommentTags[iTag].c_str());
			if (eComment != NO_DIPLOCOMMENT)	
			{
				std::vector<DiploCommentTypes>::const_iterator it = std::find(m_aKnownDiploCommentTypes.begin(), m_aKnownDiploCommentTypes.end(), eComment);
				if (it == m_aKnownDiploCommentTypes.end())
				{
					m_aKnownDiploCommentTypes.push_back(eComment);
				}
			}
		}
		m_aKnownDiploCommentTags.clear();
	}
	int const iNumDiploCommentTypes = (int)m_aKnownDiploCommentTypes.size();
	if (iNumDiploCommentTypes > 0)
	{
		for (int iPlayer = 0; iPlayer < (int)m_stagingArea.size(); iPlayer++)
		{
			m_stagingArea[iPlayer].reserve(iNumDiploCommentTypes);
			m_activeDiploResponses[iPlayer].reserve(iNumDiploCommentTypes);
			for (int iCommentType = 0; iCommentType < iNumDiploCommentTypes; iCommentType++)
			{
				m_stagingArea[iPlayer].push_back(DynamicResponse(m_aKnownDiploCommentTypes[iCommentType]));
			}
		}
	}
}

void CvDynamicDiploManager::clearStagingArea(PlayerTypes eAIPlayer)
{
	if (!m_bInitialized)
	{
		return;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_stagingArea.size()) 
	{
		m_stagingArea[{int}eAIPlayer].clear();
	}
}

void CvDynamicDiploManager::clearActiveResponses(PlayerTypes eAIPlayer)
{
	if (!m_bInitialized)
	{
		return;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		m_activeDiploResponses[{int}eAIPlayer].clear();
	}
}

int CvDynamicDiploManager::getNumResponses(PlayerTypes eAIPlayer) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		return (int)m_activeDiploResponses[{int}eAIPlayer].size();
	}
	return 0;
}

void CvDynamicDiploManager::updateActiveResponseCache(PlayerTypes ePlayer)
{
	CvFunctionMutex lock(m_CS);
	{
		if (!m_bInitialized)
		{
			return;
		}
		// Copy staging directly over active at turn change. This forces all players onto 
		// the exact same historical text dataset for the upcoming turn, 
		// even if their WinINet threads finished at wildly different frames.
		m_activeDiploResponses[(int)ePlayer] = m_aStagingArea[(int)ePlayer];
	}
}

void CvDynamicDiploManager::updateAIPlayerAvailableResponses(LLMQueueResult const& kResult)
{
	if (!m_bInitialized)
	{
		return;
	}
	PlayerTypes const eAIPlayer = kResult.getID();
	if (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		int const iAIPlayer = (int)eAIPlayer;
		copyActiveResponsesToStaging(eAIPlayer);
		CvFunctionMutex lock(m_CS);
		{
			int iIndex = -1;
			for (int iLoop = 0; iLoop < (int)m_aStagingArea[iAIPlayer].size(); iLoop++)
			{
				if (m_aStagingArea[iAIPlayer][iLoop].getCommentType() == kResult.getType())
				{
					iIndex = iLoop;
					break;
				}
			}
			if (iIndex >= 0)
			{
				m_aStagingArea[iAIPlayer][iIndex].setDiplomacyText(CvString(kResult.getText()));
			}
		}
	}
}

void CvDynamicDiploManager::copyActiveResponsesToStaging(PlayerTypes ePlayer)
{
	CvFunctionMutex lock(m_CS);
	{
		if (!m_bInitialized)
		{
			return;
		}
		// Copy active directly over staging when updating a response. This ensures all players use 
		// the exact same historical text dataset for the upcoming turn, 
		// even if their WinINet threads finished at wildly different frames.
		m_aStagingArea[(int)ePlayer] = m_activeDiploResponses[(int)ePlayer];
	}
}

bool CvDynamicDiploManager::isResponseForCivilization(PlayerTypes eAIPlayer, int iIndex) const
{
	return getCivilizationTypes(eAIPlayer, iIndex, GET_PLAYER(eAIPlayer).getCivilizationType());
}

bool CvDynamicDiploManager::isResponseForLeaderHead(PlayerTypes eAIPlayer, int iIndex) const
{
	return getLeaderHeadTypes(eAIPlayer, iIndex, GET_PLAYER(eAIPlayer).getLeaderType());
}

bool CvDynamicDiploManager::isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const
{
	return getAttitudeTypes(eAIPlayer, iIndex, GET_PLAYER(eAIPlayer).AI_getAttitude(eOtherPlayer));
}

bool CvDynamicDiploManager::isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, int iIndex) const
{
	int const iPowerUs = GET_PLAYER(eAIPlayer).getPower();
	int const iPowerThem = GET_PLAYER(eOtherPlayer).getPower();
	if ((iPowerThem < (iPowerUs / 2))
	{
		return getDiplomacyPowerTypes(eAIPlayer, iIndex, DIPLOMACYPOWER_STRONGER);
	}
	else if (iPowerThem > (iPowerUs * 2))
	{
		return getDiplomacyPowerTypes(eAIPlayer, iIndex, DIPLOMACYPOWER_WEAKER);
	}
	else
	{
		return getDiplomacyPowerTypes(eAIPlayer, iIndex, DIPLOMACYPOWER_EQUAL);
	}
}

bool CvDynamicDiploManager::getCivilizationTypes(PlayerTypes eAIPlayer, int iIndex, CivilizationTypes eCiv) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			if (eCiv > NO_CIVILIZATION && eCiv < GC.getNumCivilizationInfos())
			{
				return m_activeDiploResponses[{int}eAIPlayer][iIndex].getCivilizationTypes(eCiv);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getLeaderHeadTypes(PlayerTypes eAIPlayer, int iIndex, LeaderHeadTypes eLeader) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			if (eLeader > NO_LEADER && eLeader < GC.getNumLeaderHeadInfos())
			{
				return m_activeDiploResponses[{int}eAIPlayer][iIndex].getLeaderHeadTypes(eLeader);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getAttitudeTypes(PlayerTypes eAIPlayer, int iIndex, AttitudeTypes eAttitude) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			if (eAttitude > NO_ATTITUDE && eAttitude < NUM_ATTITUDE_TYPES)
			{
				return m_activeDiploResponses[{int}eAIPlayer][iIndex].getAttitudeTypes(eAttitude);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(PlayerTypes eAIPlayer, int iIndex, DiplomacyPowerTypes ePower) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			if (ePower > NO_DIPLOMACYPOWER && ePower < NUM_DIPLOMACYPOWER_TYPES)
			{
				return m_activeDiploResponses[{int}eAIPlayer][iIndex].getDiplomacyPowerTypes(ePower);
			}
		}
	}
	return false;
}

int CvDynamicDiploManager::getNumDiplomacyText(PlayerTypes eAIPlayer, int iIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			return m_activeDiploResponses[{int}eAIPlayer][iIndex].getNumDiplomacyText();
		}
	}
	return 0;
}

const char* CvDynamicDiploManager::getDiplomacyText(PlayerTypes eAIPlayer, int iIndex, int iVariant) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < getNumResponses(eAIPlayer))
		{
			if (iVariant >= 0 && iVariant < getNumDiplomacyText(eAIPlayer, iIndex))
			{
				return &m_activeDiploResponses[{int}eAIPlayer][iIndex].getDiplomacyText(iVariant);
			}
		}
	}
	return "";
}