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
		CvFunctionMutex lock(m_CS);
		{
			m_LLMDiploResponses.resize(MAX_PLAYERS);
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
	if (m_bInitialized)
	{
		CvFunctionMutex lock(m_CS);
		{
			FOR_EACH_ENUM(Player)
			{
				clearResponses(eLoopPlayer);
			}
			m_bInitialized = false;
		}
	}
}

void CvDynamicDiploManager::setInitialItems()
{
	m_iNumDiploCommentTypes = GC.getNumDiplomacyInfos();
	FOR_EACH_ENUM(Player)
	{
		m_LLMDiploResponses[(int)eLoopPlayer].reserve(GC.getNumDiplomacyInfos());
		for (int iLoop = 0; iLoop < GC.getNumDiplomacyInfos(); iLoop++)
		{
			m_LLMDiploResponses[(int)eLoopPlayer].push_back(new DynamicResponse(static_cast<DiploCommentTypes>(iLoop)));
		}
	}
}

void CvDynamicDiploManager::clearResponses(PlayerTypes eAIPlayer)
{
	if (!m_bInitialized)
	{
		return;
	}
	if (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (m_LLMDiploResponses[(int)eAIPlayer].size() > 0)
		{
			for (int iLoop = 0; iLoop < GC.getNumDiplomacyInfos(); iLoop++)
			{
				SAFE_DELETE(m_LLMDiploResponses[(int)eAIPlayer][iLoop]);
			}
		}
		m_LLMDiploResponses[(int)eAIPlayer].clear();
	}
}

void CvDynamicDiploManager::updateAIPlayerAvailableResponses(LLMResultData const& kResult)
{
	/* XANA (warning):
	DO NOT USE FIRAXIS GLOBAL FUNCTIONS OR ASSERTIONS HERE
	THIS OPERATION WILL BE CALLED VIA A BACKGROUND THREAD
	ATTEMPTING TO DO SO WILL CRASH THE GAME */
	if (!m_bInitialized || kResult.getID() <= NO_PLAYER || kResult.getID() > MAX_PLAYERS
		|| kResult.getType() <= NO_DIPLOCOMMENT || kResult.getType() > m_iNumDiploCommentTypes) /* Enum Bounds Validation - Safe No Global Function Use */
	{
		return;
	}
	
	CvFunctionMutex lock(m_CS);
	{
		m_LLMDiploResponses[(int)kResult.getID()][kResult.getType()]->setDiplomacyText(kResult);
	}
}

int CvDynamicDiploManager::getAvailableResponseGroupID(PlayerTypes eAIPlayer, DiploCommentTypes eComment)
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	if (m_bInitialized && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS
		&& eComment > NO_DIPLOCOMMENT && eComment < GC.getNumDiplomacyInfos())
	{
		if (m_LLMDiploResponses[(int)eAIPlayer].size() > 0)
		{
			CvFunctionMutex lock(m_CS);
			{
				DynamicResponse* pResponse = m_LLMDiploResponses[(int)eAIPlayer][eComment];
				if (pResponse != NULL)
				{
					int iGroupIndex = pResponse->getFirstFreeResponseGroup();
					if (iGroupIndex == -1)
					{
						/* XANA (note): The first Response Group ID assignment attempt failed, time for us to setup a new group!
						We'll use an out-parameter to assign to iGroupIndex because this function doesn't return anything.
						This is by design due to needing to alter the objects in the DynamicResponse vector. */
						pResponse->assignValidResponseGroupFallback(iGroupIndex);
					}
					return iGroupIndex;
				}
			}
		}
	}
	return -1;
}

int CvDynamicDiploManager::getNumResponses(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	if (m_bInitialized && (eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	&& (eComment > NO_DIPLOCOMMENT && eComment < GC.getNumDiplomacyInfos()))
	{
		CvFunctionMutex lock(m_CS);
		{
			return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getNumResponseGroups();
		}
	}
	return 0;
}

bool CvDynamicDiploManager::isResponseForCivilization(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	return getCivilizationTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getCivilizationType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForLeaderHead(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	return getLeaderHeadTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getLeaderType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, MAX_PLAYERS, eOtherPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	return getAttitudeTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).AI_getAttitude(eOtherPlayer), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, MAX_PLAYERS, eOtherPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
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
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	FAssertBounds(0, GC.getNumCivilizationInfos(), eCiv);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eCiv > NO_CIVILIZATION && eCiv < GC.getNumCivilizationInfos())
		{
			CvFunctionMutex lock(m_CS);
			{
				return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getCivilizationTypes(iGroupIndex, eCiv);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getLeaderHeadTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, LeaderHeadTypes eLeader, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	FAssertBounds(0, GC.getNumLeaderHeadInfos(), eLeader);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eLeader > NO_LEADER && eLeader < GC.getNumLeaderHeadInfos())
		{
			CvFunctionMutex lock(m_CS);
			{
				return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getLeaderHeadTypes(iGroupIndex, eLeader);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getAttitudeTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, AttitudeTypes eAttitude, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	FAssertBounds(0, NUM_ATTITUDE_TYPES, eAttitude);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (eAttitude > NO_ATTITUDE && eAttitude < NUM_ATTITUDE_TYPES)
		{
			CvFunctionMutex lock(m_CS);
			{
				return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getAttitudeTypes(iGroupIndex, eAttitude);
			}
		}
	}
	return false;
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, DiplomacyPowerTypes ePower, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	FAssertBounds(0, NUM_DIPLOMACYPOWER_TYPES, ePower);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (ePower > NO_DIPLOMACYPOWER && ePower < NUM_DIPLOMACYPOWER_TYPES)
		{
			CvFunctionMutex lock(m_CS);
			{
				return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getDiplomacyPowerTypes(iGroupIndex, ePower);
			}
		}
	}
	return false;
}

int CvDynamicDiploManager::getNumDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos(), eComment);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		CvFunctionMutex lock(m_CS);
		{
			return m_LLMDiploResponses[(int)eAIPlayer][eComment]->getNumDiplomacyText(iGroupIndex);
		}
	}
	return 0;
}

const char* CvDynamicDiploManager::getDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex, int iVariant)
{
	FAssertBounds(0, MAX_PLAYERS, eAIPlayer);
	FAssertBounds(0, GC.getNumDiplomacyInfos()), eComment);
	if (m_bInitialized && iGroupIndex >= 0 && iGroupIndex < getNumResponses(eAIPlayer, eComment) && eAIPlayer > NO_PLAYER && eAIPlayer < MAX_PLAYERS)
	{
		if (iVariant >= 0 && iVariant < getNumDiplomacyText(eAIPlayer, eComment, iGroupIndex))
		{
			CvFunctionMutex lock(m_CS);
			{
				DynamicResponse* pResponse = m_LLMDiploResponses[(int)eAIPlayer][eComment];
				if (pResponse != NULL)
				{
					std::string szResponse = pResponse->getDiplomacyText(iGroupIndex, iVariant);
					pResponse->updateDynamicResponseLifetime(iGroupIndex, iVariant);
					return &szResponse;
				}
			}
		}
	}
	return "";
}