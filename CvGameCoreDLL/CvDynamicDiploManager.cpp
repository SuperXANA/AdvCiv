#include "CvGameCoreDLL.h"
#include "CvDynamicDiploManager.h"
#include "CvPlayerAI.h"

// XANA: 10-27-2026 LLM Text Diplomacy Generation - synchronized local presentation cache
CvDynamicDiploManager& CvDynamicDiploManager::getInstance()
{
	// CvGame constructs this on the main thread before a worker may access it.
	static CvDynamicDiploManager singleton;
	return singleton;
}

void CvDynamicDiploManager::init()
{
	if (!isMainThread())
		return;
	CvFunctionMutex lock(m_CS);
	if (m_bInitialized)
		return;
	if (m_ulSessionID == 0)
		m_ulSessionID = 1;
	m_iNumDiploCommentTypes = GC.getNumDiplomacyInfos();
	m_LLMDiploResponses.resize(MAX_PLAYERS);
	m_aRequestStates.resize(MAX_PLAYERS);
	setInitialItems();
	m_bInitialized = true;
}

void CvDynamicDiploManager::reset()
{
	if (!isMainThread())
		return;
	// Windows critical sections permit these nested acquisitions. Keep the entire
	// reset atomic with respect to a completion from the background worker.
	CvFunctionMutex lock(m_CS);
	uninit();
	init();
}

void CvDynamicDiploManager::uninit()
{
	if (!isMainThread())
		return;
	CvFunctionMutex lock(m_CS);
	for (int iPlayer = 0; iPlayer < (int)m_LLMDiploResponses.size(); ++iPlayer)
		clearResponses(static_cast<PlayerTypes>(iPlayer));
	m_LLMDiploResponses.clear();
	m_aRequestStates.clear();
	for (int i = 0; i < (int)m_aPendingPrompts.size(); ++i)
		delete m_aPendingPrompts[i];
	m_aPendingPrompts.clear();
	m_iMailboxHead = m_iMailboxCount = 0;
	++m_ulSessionID;
	if (m_ulSessionID == 0)
		++m_ulSessionID;
	m_iNumDiploCommentTypes = 0;
	m_bInitialized = false;
}

void CvDynamicDiploManager::setInitialItems()
{
	for (int iPlayer = 0; iPlayer < MAX_PLAYERS; ++iPlayer)
	{
		std::vector<DynamicResponse*>& aResponses = m_LLMDiploResponses[iPlayer];
		aResponses.reserve(m_iNumDiploCommentTypes);
		m_aRequestStates[iPlayer].resize(m_iNumDiploCommentTypes);
		for (int iComment = 0; iComment < m_iNumDiploCommentTypes; ++iComment)
			aResponses.push_back(new DynamicResponse(static_cast<DiploCommentTypes>(iComment)));
	}
}

void CvDynamicDiploManager::clearResponses(PlayerTypes eAIPlayer)
{
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= (int)m_LLMDiploResponses.size())
		return;
	std::vector<DynamicResponse*>& aResponses = m_LLMDiploResponses[(int)eAIPlayer];
	for (int i = 0; i < (int)aResponses.size(); ++i)
		SAFE_DELETE(aResponses[i]);
	aResponses.clear();
}

DynamicResponse* CvDynamicDiploManager::getResponse(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	// The caller holds m_CS, including throughout use of the returned pointer.
	if (!m_bInitialized || (int)eAIPlayer < 0 || (int)eAIPlayer >= (int)m_LLMDiploResponses.size()
		|| (int)eComment < 0 || (int)eComment >= m_iNumDiploCommentTypes)
		return NULL;
	std::vector<DynamicResponse*> const& aResponses = m_LLMDiploResponses[(int)eAIPlayer];
	if ((int)eComment >= (int)aResponses.size())
		return NULL;
	return aResponses[(int)eComment];
}

char* CvDynamicDiploManager::getRequestState(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (getResponse(eAIPlayer, eComment) == NULL || iGroupIndex < 0)
		return NULL;
	RequestStates& aStates = m_aRequestStates[(int)eAIPlayer][(int)eComment];
	return iGroupIndex < (int)aStates.size() ? &aStates[iGroupIndex] : NULL;
}

void CvDynamicDiploManager::updateAIPlayerAvailableResponses(LLMResultData const& kResult)
{
	if (!isMainThread())
		return;
	// Main thread only: copying STL strings may use the game memory allocator.
	CvFunctionMutex lock(m_CS);
	if (kResult.getSessionID() != m_ulSessionID)
		return;
	DynamicResponse* pResponse = getResponse(kResult.getID(), kResult.getType());
	char* pState = getRequestState(kResult.getID(), kResult.getType(), kResult.getIndex());
	if (pResponse != NULL && pState != NULL && *pState == 1)
	{
		pResponse->setDiplomacyText(kResult);
		*pState = 2;
	}
}

unsigned long CvDynamicDiploManager::getSessionID() const
{
	CvFunctionMutex lock(m_CS);
	return m_bInitialized ? m_ulSessionID : 0;
}

bool CvDynamicDiploManager::registerPrompt(LLMPromptData const& kPrompt)
{
	if (!isMainThread())
		return false;
	CvFunctionMutex lock(m_CS);
	if (kPrompt.getSessionID() == 0 || kPrompt.getSessionID() != m_ulSessionID
		|| (int)m_aPendingPrompts.size() >= MAX_PENDING_PROMPTS)
		return false;
	DynamicResponse* pResponse = getResponse(kPrompt.getID(), kPrompt.getType());
	char* pState = getRequestState(kPrompt.getID(), kPrompt.getType(), kPrompt.getIndex());
	if (pResponse == NULL || pState == NULL || *pState != 0)
		return false;
	for (int i = 0; i < (int)m_aPendingPrompts.size(); ++i)
	{
		LLMPromptData const& kExisting = *m_aPendingPrompts[i];
		if (kExisting.getID() == kPrompt.getID() && kExisting.getType() == kPrompt.getType()
			&& kExisting.getIndex() == kPrompt.getIndex())
			return false;
	}
	m_aPendingPrompts.push_back(new LLMPromptData(kPrompt));
	*pState = 1;
	return true;
}

void CvDynamicDiploManager::cancelPrompt(unsigned long ulSession, PlayerTypes eAIPlayer,
	DiploCommentTypes eComment, int iGroupIndex)
{
	if (!isMainThread())
		return;
	// Main thread only. A transport failure must release its registered prompt.
	CvFunctionMutex lock(m_CS);
	if (ulSession != m_ulSessionID)
		return;
	char* pState = getRequestState(eAIPlayer, eComment, iGroupIndex);
	if (pState != NULL)
		*pState = 2;
	for (int i = 0; i < (int)m_aPendingPrompts.size(); ++i)
	{
		LLMPromptData const& kPrompt = *m_aPendingPrompts[i];
		if (kPrompt.getID() == eAIPlayer && kPrompt.getType() == eComment && kPrompt.getIndex() == iGroupIndex)
		{
			delete m_aPendingPrompts[i];
			m_aPendingPrompts.erase(m_aPendingPrompts.begin() + i);
			return;
		}
	}
}

bool CvDynamicDiploManager::submitResponse(unsigned long ulSession, PlayerTypes eAIPlayer,
	DiploCommentTypes eComment, int iGroupIndex, const char* pszText, int iLength)
{
	// Raw WinINet output only. In particular, do not create CvString/std::string
	// here; USE_MEMMANAGER can route their allocations through gDLL.
	if (pszText == NULL || iLength <= 0 || iLength > MAX_RESPONSE_BYTES)
		return false;
	CvFunctionMutex lock(m_CS);
	if (ulSession == 0 || ulSession != m_ulSessionID || m_iMailboxCount >= MAX_QUEUED_RESULTS)
		return false;
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	char* pState = getRequestState(eAIPlayer, eComment, iGroupIndex);
	if (pResponse == NULL || pState == NULL || *pState != 1)
		return false;
	bool bRegistered = false;
	for (int i = 0; i < (int)m_aPendingPrompts.size(); ++i)
	{
		LLMPromptData const& kPrompt = *m_aPendingPrompts[i];
		if (kPrompt.getID() == eAIPlayer && kPrompt.getType() == eComment && kPrompt.getIndex() == iGroupIndex)
		{
			bRegistered = true;
			break;
		}
	}
	if (!bRegistered)
		return false;
	for (int i = 0; i < m_iMailboxCount; ++i)
	{
		QueuedResult const& kExisting = m_aMailbox[(m_iMailboxHead + i) % MAX_QUEUED_RESULTS];
		if (kExisting.ulSession == ulSession && kExisting.eAIPlayer == eAIPlayer
			&& kExisting.eComment == eComment && kExisting.iGroupIndex == iGroupIndex)
			return false;
	}
	for (int i = 0; i < iLength; ++i)
	{
		if (pszText[i] == '\0')
			return false;
	}
	QueuedResult& kQueued = m_aMailbox[(m_iMailboxHead + m_iMailboxCount) % MAX_QUEUED_RESULTS];
	kQueued.ulSession = ulSession;
	kQueued.eAIPlayer = eAIPlayer;
	kQueued.eComment = eComment;
	kQueued.iGroupIndex = iGroupIndex;
	memcpy(kQueued.szText, pszText, iLength);
	kQueued.szText[iLength] = '\0';
	++m_iMailboxCount;
	return true;
}

void CvDynamicDiploManager::processPendingResponses()
{
	if (!isMainThread())
		return;
	// Main thread only. Convert the bounded raw mailbox into owning STL values.
	CvFunctionMutex lock(m_CS);
	while (m_iMailboxCount > 0)
	{
		QueuedResult const& kQueued = m_aMailbox[m_iMailboxHead];
		if (m_bInitialized && kQueued.ulSession == m_ulSessionID)
		{
			for (int i = 0; i < (int)m_aPendingPrompts.size(); ++i)
			{
				LLMPromptData* pPrompt = m_aPendingPrompts[i];
				if (pPrompt->getID() != kQueued.eAIPlayer || pPrompt->getType() != kQueued.eComment
					|| pPrompt->getIndex() != kQueued.iGroupIndex)
					continue;
				LLMResultData kResult(*pPrompt);
				kResult.setText(CvString(kQueued.szText));
				updateAIPlayerAvailableResponses(kResult);
				delete pPrompt;
				m_aPendingPrompts.erase(m_aPendingPrompts.begin() + i);
				break;
			}
		}
		m_iMailboxHead = (m_iMailboxHead + 1) % MAX_QUEUED_RESULTS;
		--m_iMailboxCount;
	}
}

int CvDynamicDiploManager::getAvailableResponseGroupID(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	if (!isMainThread())
		return -1;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	if (pResponse == NULL || (int)m_aPendingPrompts.size() >= MAX_PENDING_PROMPTS)
		return -1;
	// IDs are never reused in one session: a late completion cannot overwrite
	// a newer request. Bounded exhaustion simply leaves XML text available.
	if (pResponse->getNumResponseGroups() >= MAX_GROUPS_PER_COMMENT)
		return -1;
	pResponse->initNewResponseGroup();
	int const iGroupIndex = pResponse->getNumResponseGroups() - 1;
	m_aRequestStates[(int)eAIPlayer][(int)eComment].push_back(0);
	return iGroupIndex;
}

int CvDynamicDiploManager::getNumResponses(PlayerTypes eAIPlayer, DiploCommentTypes eComment) const
{
	if (!isMainThread())
		return 0;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse == NULL ? 0 : pResponse->getNumResponseGroups();
}

bool CvDynamicDiploManager::isResponseForCivilization(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= MAX_PLAYERS)
		return false;
	return getCivilizationTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getCivilizationType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForLeaderHead(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= MAX_PLAYERS)
		return false;
	return getLeaderHeadTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).getLeaderType(), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForAttitude(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= MAX_PLAYERS
		|| (int)eOtherPlayer < 0 || (int)eOtherPlayer >= MAX_PLAYERS)
		return false;
	return getAttitudeTypes(eAIPlayer, eComment, GET_PLAYER(eAIPlayer).AI_getAttitude(eOtherPlayer), iGroupIndex);
}

bool CvDynamicDiploManager::isResponseForDiplomacyPower(PlayerTypes eAIPlayer, PlayerTypes eOtherPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= MAX_PLAYERS
		|| (int)eOtherPlayer < 0 || (int)eOtherPlayer >= MAX_PLAYERS)
		return false;
	int const iPowerUs = GET_PLAYER(eAIPlayer).getPower();
	int const iPowerThem = GET_PLAYER(eOtherPlayer).getPower();
	DiplomacyPowerTypes ePower = DIPLOMACYPOWER_EQUAL;
	if (iPowerThem < iPowerUs / 2)
		ePower = DIPLOMACYPOWER_STRONGER;
	else if (iPowerThem > iPowerUs && iPowerThem - iPowerUs > iPowerUs) // Avoid overflowing iPowerUs * 2.
		ePower = DIPLOMACYPOWER_WEAKER;
	return getDiplomacyPowerTypes(eAIPlayer, eComment, ePower, iGroupIndex);
}

bool CvDynamicDiploManager::getCivilizationTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, CivilizationTypes eCiv, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse != NULL && (int)eCiv >= 0 && (int)eCiv < GC.getNumCivilizationInfos()
		&& pResponse->getCivilizationTypes(iGroupIndex, eCiv);
}

bool CvDynamicDiploManager::getLeaderHeadTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, LeaderHeadTypes eLeader, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse != NULL && (int)eLeader >= 0 && (int)eLeader < GC.getNumLeaderHeadInfos()
		&& pResponse->getLeaderHeadTypes(iGroupIndex, eLeader);
}

bool CvDynamicDiploManager::getAttitudeTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, AttitudeTypes eAttitude, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse != NULL && (int)eAttitude >= 0 && (int)eAttitude < NUM_ATTITUDE_TYPES
		&& pResponse->getAttitudeTypes(iGroupIndex, eAttitude);
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(PlayerTypes eAIPlayer, DiploCommentTypes eComment, DiplomacyPowerTypes ePower, int iGroupIndex) const
{
	if (!isMainThread())
		return false;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse != NULL && (int)ePower >= 0 && (int)ePower < NUM_DIPLOMACYPOWER_TYPES
		&& pResponse->getDiplomacyPowerTypes(iGroupIndex, ePower);
}

int CvDynamicDiploManager::getNumDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex) const
{
	if (!isMainThread())
		return 0;
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	return pResponse == NULL ? 0 : pResponse->getNumDiplomacyText(iGroupIndex);
}

CvString CvDynamicDiploManager::getDynamicDiplomacyTextForPlayers(PlayerTypes eAIPlayer,
	PlayerTypes eOtherPlayer, DiploCommentTypes eComment) const
{
	if (!isMainThread())
		return CvString();
	// UI call on the main thread. Transport completion never participates in
	// gameplay decisions, synchronized RNG, serialization or Python mutations.
	const_cast<CvDynamicDiploManager*>(this)->processPendingResponses();
	if ((int)eAIPlayer < 0 || (int)eAIPlayer >= MAX_PLAYERS
		|| (int)eOtherPlayer < 0 || (int)eOtherPlayer >= MAX_PLAYERS)
		return CvString();
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	if (pResponse == NULL)
		return CvString();
	CivilizationTypes const eCiv = GET_PLAYER(eAIPlayer).getCivilizationType();
	LeaderHeadTypes const eLeader = GET_PLAYER(eAIPlayer).getLeaderType();
	AttitudeTypes const eAttitude = GET_PLAYER(eAIPlayer).AI_getAttitude(eOtherPlayer);
	int const iPowerUs = GET_PLAYER(eAIPlayer).getPower();
	int const iPowerThem = GET_PLAYER(eOtherPlayer).getPower();
	DiplomacyPowerTypes ePower = DIPLOMACYPOWER_EQUAL;
	if (iPowerThem < iPowerUs / 2)
		ePower = DIPLOMACYPOWER_STRONGER;
	else if (iPowerThem > iPowerUs && iPowerThem - iPowerUs > iPowerUs)
		ePower = DIPLOMACYPOWER_WEAKER;
	std::vector<std::pair<int, int> > aCandidates;
	for (int iGroup = 0; iGroup < pResponse->getNumResponseGroups(); ++iGroup)
	{
		if (!pResponse->getCivilizationTypes(iGroup, eCiv)
			|| !pResponse->getLeaderHeadTypes(iGroup, eLeader)
			|| !pResponse->getAttitudeTypes(iGroup, eAttitude)
			|| !pResponse->getDiplomacyPowerTypes(iGroup, ePower))
			continue;
		for (int iVariant = 0; iVariant < pResponse->getNumDiplomacyText(iGroup); ++iVariant)
		{
			if (!pResponse->getDiplomacyText(iGroup, iVariant).empty())
				aCandidates.push_back(std::make_pair(iGroup, iVariant));
		}
	}
	if (aCandidates.empty())
		return CvString();
	int const iChosen = GC.getASyncRand().get((int)aCandidates.size(), "Dynamic diplomacy UI");
	int const iGroup = aCandidates[iChosen].first;
	int const iVariant = aCandidates[iChosen].second;
	CvString szText(pResponse->getDiplomacyText(iGroup, iVariant).c_str());
	pResponse->updateDynamicResponseLifetime(iGroup, iVariant);
	return szText;
}

CvString CvDynamicDiploManager::getDiplomacyText(PlayerTypes eAIPlayer, DiploCommentTypes eComment, int iGroupIndex, int iVariant) const
{
	if (!isMainThread())
		return CvString();
	CvFunctionMutex lock(m_CS);
	DynamicResponse* pResponse = getResponse(eAIPlayer, eComment);
	// Copy under the lock. The UI receives an owning value, and enumerating
	// candidates does not consume or erase any response.
	return pResponse == NULL ? CvString() : CvString(pResponse->getDiplomacyText(iGroupIndex, iVariant).c_str());
}
// XANA: 10-27-2026 LLM Text Diplomacy Generation - synchronized local presentation cache
