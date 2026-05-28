#include "CvGameCoreDLL.h"
#include "CvDynamicDiploManager.h"

CvDynamicDiploManager& CvDynamicDiploManager::getInstance()
{
	static CvDynamicDiploManager singleton;
	return singleton;
}

void CvDynamicDiploManager::init()
{
	CvFunctionMutex lock(m_CS);
	{
		if (!m_bInitialized)
		{
			m_stagingArea.resize(MAX_PLAYERS);
			m_activeDiploResponses.resize(MAX_PLAYERS);
			setInitialItems();
			m_bInitialized = true;
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

void CvDynamicDiploManager::setInitialItems()
{
	int const iSize = GC.getNumDiplomacyInfos();
	FOR_EACH_ENUM(Player)
	{
		m_stagingArea[{int}eLoopPlayer].reserve(iSize);
		for (int iLoop = 0; iLoop < iSize; iLoop++)
		{
			m_stagingArea[{int}eLoopPlayer].push_back(DynamicResponse(static_cast<DiploCommentTypes>(iLoop)));
		}
		m_activeDiploResponses[{int}eLoopPlayer].reserve(iSize);
	}
}

void CvDynamicDiploManager::clearStagingArea(PlayerTypes eAIPlayer)
{
	if (!m_bInitialized)
	{
		return;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS) 
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
	if (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		m_activeDiploResponses[{int}eAIPlayer].clear();
	}
}

void CvDynamicDiploManager::updateActiveResponseCache(PlayerTypes eAIPlayer)
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
		m_activeDiploResponses[(int)eAIPlayer] = m_aStagingArea[(int)eAIPlayer];
	}
}

void CvDynamicDiploManager::updateAIPlayerAvailableResponses(LLMResultData const& kResult)
{
	if (!m_bInitialized)
	{
		return;
	}
	PlayerTypes eAIPlayer = kResult.getID();
	if (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		copyActiveResponsesToStaging(eAIPlayer);
		CvFunctionMutex lock(m_CS);
		{
			if (getResponseIndexForDiploComment(eAIPlayer, kResult.getType()) >= 0)
			{
				int const iIndex = getResponseIndexForDiploComment(eAIPlayer, kResult.getType());
				
				m_aStagingArea[(int)eAIPlayer][iIndex].setLimits(kResult.getIndex(), kResult.getLimits());
				m_aStagingArea[(int)eAIPlayer][iIndex].setDiplomacyText(kResult.getIndex(), CvString(kResult.getText()));
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

int CvDynamicDiploManager::getResponseIndexForDiploComment(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eComment > NO_DIPLOCOMMENT && eComment < GC.getNumDiplomacyInfos())
		{
			for (int iIndex = 0; iIndex < (int)m_activeDiploResponses[{int}eAIPlayer].size(); iIndex++)
			{
				if (m_activeDiploResponses[{int}eAIPlayer][iIndex].getCommentType() == eComment)
				{
					return iIndex;
				}
			}
		}
	}
	return -1;
}

int CvDynamicDiploManager::getNumResponses(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
		{
			return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getNumResponseGroups();
		}
	}
	return 0;
}

bool CvDynamicDiploManager::isResponseForCivilization(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	return getCivilizationTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getCivilizationType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForLeaderHead(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	return getLeaderHeadTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getLeaderType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	return getAttitudeTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).AI_getAttitude(eOtherPlayer), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	int const iPowerUs = GET_PLAYER(eAIPlayer).getPower();
	int const iPowerThem = GET_PLAYER(eOtherPlayer).getPower();
	if ((iPowerThem < (iPowerUs / 2))
	{
		return getDiplomacyPowerTypes(eAIPlayer, eComment, DIPLOMACYPOWER_STRONGER, iGroupIndex);
	}
	else if (iPowerThem > (iPowerUs * 2))
	{
		return getDiplomacyPowerTypes(eAIPlayer, eComment, DIPLOMACYPOWER_WEAKER, iGroupIndex);
	}
	else
	{
		return getDiplomacyPowerTypes(eAIPlayer, eComment, DIPLOMACYPOWER_EQUAL, iGroupIndex);
	}
}

bool CvDynamicDiploManager::getCivilizationTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, CivilizationTypes eCiv, int iGroupIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eCiv > NO_CIVILIZATION && eCiv < GC.getNumCivilizationInfos())
		{
			if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
			{
				return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getCivilizationTypes(iGroupIndex, eCiv);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getLeaderHeadTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, LeaderHeadTypes eLeader, int iGroupIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eLeader > NO_LEADER && eLeader < GC.getNumLeaderHeadInfos())
		{
			if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
			{
				return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getLeaderHeadTypes(iGroupIndex, eLeader);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getAttitudeTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, AttitudeTypes eAttitude, int iGroupIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eAttitude > NO_ATTITUDE && eAttitude < NUM_ATTITUDE_TYPES)
		{
			if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
			{
				return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getAttitudeTypes(iGroupIndex, eAttitude);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, DiplomacyPowerTypes ePower, int iGroupIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (ePower > NO_DIPLOMACYPOWER && ePower < NUM_DIPLOMACYPOWER_TYPES)
		{
			if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
			{
				return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getDiplomacyPowerTypes(iGroupIndex, ePower);
			}
		}
	}
	return false;
}

int CvDynamicDiploManager::getNumDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
		{
			return m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getNumDiplomacyText(iGroupIndex);
		}
	}
	return 0;
}

const char* CvDynamicDiploManager::getDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex, int iVariant) const
{
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (iVariant >= 0 && iVariant < getNumDiplomacyText(eAIPlayer, eComment))
		{
			if (getResponseIndexForDiploComment(eAIPlayer, eComment) >= 0)
			{
				return &m_activeDiploResponses[{int}eAIPlayer][getResponseIndexForDiploComment(eAIPlayer, eComment)].getDiplomacyText(iGroupIndex, iVariant);
			}
		}
	}
	return "";
}