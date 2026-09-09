#pragma once

#ifndef CV_INFO_GAMEPLAYMECHANIC_H
#define CV_INFO_GAMEPLAYMECHANIC_H

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration
class CvPlayer;
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvGameplayMechanicInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvGameplayMechanicInfo : public CvInfoBase
{
	typedef CvInfoBase base_t;
public: // advc: All the const functions are exposed to Python
	CvGameplayMechanicInfo();
	~CvGameplayMechanicInfo();

	int getLeaderType() const;
	int getCivilizationType() const;
	bool isPlayerValid(const CvPlayer& kPlayer) const;

	// Array access:

	bool read(CvXMLLoadUtility* pXML);
	bool readPass3();

protected:
	int m_iLeaderType;
	int m_iCivilizationType;
};

// XANA: 09-12-2026 Fantasy Gameplay Mechanics Configuration

#endif