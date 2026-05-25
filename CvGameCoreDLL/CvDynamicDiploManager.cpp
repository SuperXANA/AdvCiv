#include "CvDynamicDiploManager.h"

CvCriticalSection CvDynamicDiploManager::m_CS;
CvDynamicDiploManager::DynamicResponseMap CvDynamicDiploManager::m_stagingArea; // managed by WinINet ONLY!
CvDynamicDiploManager::DynamicResponseMap CvDynamicDiploManager::m_activeDiploResponses; // managed by Civ4 ONLY!
bool CvDynamicDiploManager::m_bInitialized = false;

void CvDynamicDiploManager::init()
{
	if (!m_bInitialized)
	{
		m_stagingArea.resize(MAX_PLAYERS); 
		m_activeDiploResponses.resize(MAX_PLAYERS);
		m_bInitialized = true;
	}
}

void CvDynamicDiploManager::uninit()
{
	if (m_bInitialized)
	{
		CvFunctionMutex lock(m_CS);
		FOR_EACH_ENUM(Player)
		{
			clearStagingArea(eLoopPlayer);
			clearActiveResponses(eLoopPlayer);
		}
		m_bInitialized = false;
	}
}

void CvDynamicDiploManager::pushNewResponse(PlayerTypes eAIPlayer, DynamicResponse const& kResponse)
{
	CvFunctionMutex lock(m_CS);
	{
		if (!m_bInitialized)
		{
			return;
		}
		if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_stagingArea.size())
		{
			m_stagingArea[eAIPlayer].push_back(kResponse);
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
		m_stagingArea[eAIPlayer].clear();
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
		m_activeDiploResponses[eAIPlayer].clear();
	}
}

void CvDynamicDiploManager::updateCache()
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
		m_activeDiploResponses = m_stagingArea;
	}
}

bool CvDynamicDiploManager::getCivilizationTypes(PlayerTypes eAIPlayer, int iIndex, CivilizationTypes eCiv) const
{
	if (!m_bInitialized)
	{
		return false;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			if (eCiv > NO_CIVILIZATION && eCiv < GC.getNumCivilizationInfos())
			{
				return m_activeDiploResponses[eAIPlayer][iIndex].getCivilizationTypes(eCiv);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getLeaderHeadTypes(PlayerTypes eAIPlayer, int iIndex, LeaderHeadTypes eLeader) const
{
	if (!m_bInitialized)
	{
		return false;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			if (eLeader > NO_LEADER && eLeader < GC.getNumLeaderHeadInfos())
			{
				return m_activeDiploResponses[eAIPlayer][iIndex].getLeaderHeadTypes(eLeader);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getAttitudeTypes(PlayerTypes eAIPlayer, int iIndex, AttitudeTypes eAttitude) const
{
	if (!m_bInitialized)
	{
		return false;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			if (eAttitude > NO_ATTITUDE && eAttitude < NUM_ATTITUDE_TYPES)
			{
				return m_activeDiploResponses[eAIPlayer][iIndex].getAttitudeTypes(eAttitude);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(PlayerTypes eAIPlayer, int iIndex, DiplomacyPowerTypes ePower) const
{
	if (!m_bInitialized)
	{
		return false;
	}
	if eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			if (ePower > NO_DIPLOMACYPOWER && ePower < NUM_DIPLOMACYPOWER_TYPES)
			{
				return m_activeDiploResponses[eAIPlayer][iIndex].getDiplomacyPowerTypes(ePower);
			}
		}
	}
	return false;
}

int CvDynamicDiploManager::getNumDiplomacyText(PlayerTypes eAIPlayer, int iIndex) const
{
	if (!m_bInitialized)
	{
		return 0;
	}
	// No lock needed for reading if we guarantee updateCache only runs 
	// on the main thread during turn initialization
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			return m_activeDiploResponses[eAIPlayer][iIndex].getDiplomacyTextCount();
		}
	}
	return 0;
}

const char* CvDynamicDiploManager::getDiplomacyText(PlayerTypes eAIPlayer, int iIndex, int iVariant) const
{
	if (!m_bInitialized)
	{
		return "";
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < (int)m_activeDiploResponses.size())
	{
		if (iIndex >= 0 && iIndex < (int)m_activeDiploResponses[eAIPlayer].size())
		{
			if (iVariant >= 0 && iVariant < getNumDiplomacyText(eAIPlayer, iIndex))
			{
				return &m_activeDiploResponses[eAIPlayer][iIndex].getDiplomacyText(iVariant);
			}
		}
	}
	return "";
}