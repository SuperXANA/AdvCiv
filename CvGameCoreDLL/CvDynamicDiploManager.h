#pragma once

#ifndef CIV4_DYNAMICDIPLO_H
#define CIV4_DYNAMICDIPLO_H

#include "CvGameCoreDLL.h"

class CvDynamicDiploManager
{
public:
	CvDynamicDiploManager();
	~CvDynamicDiploManager();

	void uninit() { clear(); } /* XANA (note): This function is for CvGlobals::uninit to safely clear out the vectors */
	void reset() { clear(); } /* XANA (note): This function is for CvPlayer::reset to safely clear out the vectors */
	void clear();

	CvDiplomacyResponse const& getResponse(int iNum) const;
	CvDiplomacyResponse& getResponse_(int iNum);
	const Response& getResponseExternal(int iNum) const;

	int initNewResponse();
	void addNewDiplomacyText(int i, CvString szText);

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
	void setNumDiplomacyText(int i, int iVal);
	void setDiplomacyText(int i, int j, CvString szText);

protected:
	std::vector<CvDiplomacyResponse*> m_pDynamicResponses;
	std::vector<Response*> m_pDynamicResponseStructs;

};
#endif