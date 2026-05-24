#include "CvDynamicDiploManager.h"

CvDynamicDiploManager::CvDynamicDiploManager() :
{}

CvDynamicDiploManager::~CvDynamicDiploManager() :
{
	clear();
}

void CvDynamicDiploManager::clear()
{
	for (std::vector<CvDiplomacyResponse*>::iterator it = m_pDynamicResponses.begin(); it != m_pDynamicResponses.end(); ++it)
	{
		SAFE_DELETE(*it);
	}
	m_pDynamicResponses.clear();
	
	for (std::vector<Response*>::iterator it = m_pDynamicResponseStructs.begin(); it != m_pDynamicResponseStructs.end(); ++it)
	{
		SAFE_DELETE(*it);
	}
	m_pDynamicResponseStructs.clear();
}

CvDiplomacyResponse const& CvDynamicDiploManager::getResponse(int iNum) const
{
	return *m_pDynamicResponses[iNum];
}
// <advc.705>
CvDiplomacyResponse& CvDynamicDiploManager::getResponse_(int iNum)
{
	return *m_pDynamicResponses[iNum];
} // </advc.705>

const Response& CvDynamicDiploManager::getResponseExternal(int iNum) const
{
	return m_pDynamicResponseStructs[iNum];
}

// XANA (note): This returns a newly-initialized index value which can be used in the suite of dynamic response system get/set[X] functions to access/manipulate internal object values */
int CvDynamicDiploManager::initNewResponse()
{
	// Update DLL-internal object vector
	{
		CvDiplomacyResponse* pResponse = new CvDiplomacyResponse();
		pResponse->m_pbCivilizationTypes = new bool[GC.getNumCivilizationInfos()];
		for (int j = 0; j < GC.getNumCivilizationInfos(); ++j)
		{
			pResponse->m_pbCivilizationTypes[j] = false;
		}
		pResponse->m_pbLeaderHeadTypes = new bool[GC.getNumLeaderHeadInfos()];
		for (int j = 0; j < GC.getNumLeaderHeadInfos(); ++j)
		{
			pResponse->m_pbLeaderHeadTypes[j] = false;
		}
		pResponse->m_pbAttitudeTypes = new bool[NUM_ATTITUDE_TYPES];
		for (int j = 0; j < NUM_ATTITUDE_TYPES; ++j)
		{
			pResponse->m_pbAttitudeTypes[j] = false;
		}
		pResponse->m_pbDiplomacyPowerTypes = new bool[NUM_DIPLOMACYPOWER_TYPES];
		for (int j = 0; j < NUM_DIPLOMACYPOWER_TYPES; ++j)
		{
			pResponse->m_pbDiplomacyPowerTypes[j] = false;
		}
		pResponse->m_iNumDiplomacyText = 1;
		pResponse->m_paszDiplomacyText = new CvString[1];
		pResponse->m_paszDiplomacyText[0] = "";
		m_pDynamicResponses.push_back(pResponse);
	}
	// Update EXE-external struct vector
	{
		Response* pResponseStruct = new Response();
		pResponseStruct->m_pbCivilizationTypes = new bool[GC.getNumCivilizationInfos()];
		for (int j = 0; j < GC.getNumCivilizationInfos(); ++j)
		{
			pResponseStruct->m_pbCivilizationTypes[j] = false;
		}
		pResponseStruct->m_pbLeaderHeadTypes = new bool[GC.getNumLeaderHeadInfos()];
		for (int j = 0; j < GC.getNumLeaderHeadInfos(); ++j)
		{
			pResponseStruct->m_pbLeaderHeadTypes[j] = false;
		}
		pResponseStruct->m_pbAttitudeTypes = new bool[NUM_ATTITUDE_TYPES];
		for (int j = 0; j < NUM_ATTITUDE_TYPES; ++j)
		{
			pResponseStruct->m_pbAttitudeTypes[j] = false;
		}
		pResponseStruct->m_pbDiplomacyPowerTypes = new bool[NUM_DIPLOMACYPOWER_TYPES];
		for (int j = 0; j < NUM_DIPLOMACYPOWER_TYPES; ++j)
		{
			pResponseStruct->m_pbDiplomacyPowerTypes[j] = false;
		}
		pResponseStruct->m_iNumDiplomacyText = 1;
		pResponseStruct->m_paszDiplomacyText = new CvString[1];
		pResponseStruct->m_paszDiplomacyText[0] = "";
		m_pDynamicResponseStructs.push_back(pResponseStruct);
	}
	return (int)(m_pDynamicResponses.size() - 1); /* XANA (note): returns value of new "i" index that now exists in the vector storage */
}

int CvDynamicDiploManager::getNumResponses() const
{
	return m_pDynamicResponses.size();
}

bool CvDynamicDiploManager::getCivilizationTypes(int i, int j) const
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, GC.getNumCivilizationInfos(), j);
	return (m_pDynamicResponses[i].m_pbCivilizationTypes[j] == NULL ? false : // advc.003t
			m_pDynamicResponses[i].m_pbCivilizationTypes[j]);
}

bool CvDynamicDiploManager::getLeaderHeadTypes(int i, int j) const
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, GC.getNumLeaderHeadInfos(), j);
	return (m_pDynamicResponses[i].m_pbLeaderHeadTypes[j] == NULL ? false : // advc.003t
			m_pDynamicResponses[i].m_pbLeaderHeadTypes[j]);
}

bool CvDynamicDiploManager::getAttitudeTypes(int i, int j) const
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, NUM_ATTITUDE_TYPES, j);
	return (m_pDynamicResponses[i].m_pbAttitudeTypes[j] == NULL ? false : // advc.003t
			m_pDynamicResponses[i].m_pbAttitudeTypes[j]);
}

bool CvDynamicDiploManager::getDiplomacyPowerTypes(int i, int j) const
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, NUM_DIPLOMACYPOWER_TYPES, j);
	return (m_pDynamicResponses[i].m_pbDiplomacyPowerTypes[j] == NULL ? false : // advc.003t
			m_pDynamicResponses[i].m_pbDiplomacyPowerTypes[j]);
}

int CvDynamicDiploManager::getNumDiplomacyText(int i) const
{
	FAssertBounds(0, getNumResponses(), i);
	return m_pDynamicResponses[i].m_iNumDiplomacyText;
}

const TCHAR* CvDynamicDiploManager::getDiplomacyText(int i, int j) const
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, getNumDiplomacyText(i), j);
	return m_pDynamicResponses[i].m_paszDiplomacyText[j];
}

void CvDynamicDiploManager::setCivilizationTypes(int i, int j, bool bVal)
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, GC.getNumCivilizationInfos(), j);
	if (m_pDynamicResponses[i].m_pbCivilizationTypes[j] == NULL || m_pDynamicResponseStructs[i].m_pbCivilizationTypes[j] == NULL)
		return; // advc.003t
	m_pDynamicResponses[i].m_pbCivilizationTypes[j] = bVal;
	m_pDynamicResponseStructs[i].m_pbCivilizationTypes[j] = bVal;
}

void CvDynamicDiploManager::setLeaderHeadTypes(int i, int j, bool bVal)
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, GC.getNumLeaderHeadInfos(), j);
	if (m_pDynamicResponses[i].m_pbLeaderHeadTypes[j] == NULL || m_pDynamicResponseStructs[i].m_pbLeaderHeadTypes[j] == NULL))
		return; // advc.003t
	m_pDynamicResponses[i].m_pbLeaderHeadTypes[j] = bVal;
	m_pDynamicResponseStructs[i].m_pbLeaderHeadTypes[j] = bVal;
}

void CvDynamicDiploManager::setAttitudeTypes(int i, int j, bool bVal)
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, NUM_ATTITUDE_TYPES, j);
	if (m_pDynamicResponses[i].m_pbAttitudeTypes[j] == NULL || m_pDynamicResponseStructs[i].m_pbAttitudeTypes[j] == NULL))
		return; // advc.003t
	m_pDynamicResponses[i].m_pbAttitudeTypes[j] = bVal;
	m_pDynamicResponseStructs[i].m_pbAttitudeTypes[j] = bVal;
}

void CvDynamicDiploManager::setDiplomacyPowerTypes(int i, int j, bool bVal)
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, NUM_DIPLOMACYPOWER_TYPES, j);
	if (m_pDynamicResponses[i].m_pbDiplomacyPowerTypes[j] == NULL || m_pDynamicResponseStructs[i].m_pbDiplomacyPowerTypes[j] == NULL))
		return; // advc.003t
	m_pDynamicResponses[i].m_pbDiplomacyPowerTypes[j] = bVal;
	m_pDynamicResponseStructs[i].m_pbDiplomacyPowerTypes[j] = bVal;
}

void CvDynamicDiploManager::setNumDiplomacyText(int i, int iVal)
{
	FAssertBounds(0, getNumResponses(), i);
	if (iVal < 0)
		return;
	m_pDynamicResponses[i].m_iNumDiplomacyText = iVal;
	m_pDynamicResponseStructs[i].m_iNumDiplomacyText = iVal;
}

void CvDynamicDiploManager::setDiplomacyText(int i, int j, CvString szText)
{
	FAssertBounds(0, getNumResponses(), i);
	FAssertBounds(0, getNumDiplomacyText(i), j);
	m_pDynamicResponses[i].m_paszDiplomacyText[j] = szText;
	m_pDynamicResponseStructs[i].m_paszDiplomacyText[j] = szText;
}

/* XANA (note): Facilitates adding extra dynamic diplomactic text responses to a particular Response object by calling this function multiple times with different szText string values */
void CvDynamicDiploManager::addNewDiplomacyText(int i, CvString szText)
{
	FAssertBounds(0, getNumResponses(), i);
	// Update DLL-internal object vector
	{
		CvDiplomacyResponse& kResponse = m_pDynamicResponses[i];
		int const iNumDiploTexts = kResponse.m_iNumDiplomacyText;
		CvString* pTempStringArray = new CvString[iNumDiploTexts + 1];
		for (int i = 0; i < kResponse.m_iNumDiplomacyText; i++)
		{
			pTempStringArray[i] = kResponse.m_paszDiplomacyText[i];
		}
		pTempStringArray[kResponse.m_iNumDiplomacyText] = szText;
		SAFE_DELETE_ARRAY(kResponse.m_paszDiplomacyText);
		kResponse.m_paszDiplomacyText = pTempStringArray;
		kResponse.m_iNumDiplomacyText = (iNumDiploTexts + 1);
	}
	// Update EXE-external struct vector
	{
		Response& kResponseStruct = m_pDynamicResponseStructs[i];
		int const iNumDiploStructTexts = kResponseStruct.m_iNumDiplomacyText;
		CvString* pTempStructStringArray = new CvString[iNumDiploStructTexts + 1];
		for (int i = 0; i < kResponseStruct.m_iNumDiplomacyText; i++)
		{
			pTempStructStringArray[i] = kResponseStruct.m_paszDiplomacyText[i];
		}
		pTempStringArray[kResponseStruct.m_iNumDiplomacyText] = szText;
		SAFE_DELETE_ARRAY(kResponseStruct.m_paszDiplomacyText);
		kResponseStruct.m_paszDiplomacyText = pTempStructStringArray;
		kResponseStruct.m_iNumDiplomacyText = (iNumDiploStructTexts + 1);
	}
}