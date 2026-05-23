class CvDynamicDiploManager
{
public:
	CvDynamicDiploManager();
	~CvDynamicDiploManager();

	void uninit()
	{
		clear();
	}
	void reset()
	{
		clear();
	}
	void clear();

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

int initNewResponse();
int getNumResponses() const;
bool getCivilizationTypes(int i, int j) const;
bool getLeaderHeadTypes(int i, int j) const;
bool getAttitudeTypes(int i, int j) const;
bool getDiplomacyPowerTypes(int i, int j) const;
int getNumDiplomacyText(int i) const;
const TCHAR* getDiplomacyText(int i, int j) const;
void setCivilizationTypes(int i, int j, bool bVal);
void setLeaderHeadTypes(int i, int j, bool bVal);
void setAttitudeTypes(int i, int j, bool bVal);
void setDiplomacyPowerTypes(int i, int j, bool bVal);
void setDiplomacyText(int i, CvString szText);

protected:
	std::vector<CvDiplomacyResponse*> m_pDynamicResponses;
	std::vector<Response*> m_pDynamicResponseStructs;

};