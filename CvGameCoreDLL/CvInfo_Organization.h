#pragma once

#ifndef CV_INFO_ORGANIZATION_H
#define CV_INFO_ORGANIZATION_H

/*  advc.003x: Cut from CvInfos.h; CvReligionInfo and CvCorporationInfo. To be
	precompiled. (Changes are very rare, in fact, no changes by mods at all so far.) */

/*  advc.003x: Common base class to reduce code duplication. Just the stuff that
	was exactly the same in CvReligionInfo and CvCorporationInfo. */
class CvOrganizationInfo : public CvHotkeyInfo
{
	typedef CvHotkeyInfo base_t;
public: // All the const functions are exposed to Python
	CvOrganizationInfo();

	wchar getChar() const; // advc: return wchar (not int)
	void setChar(/* advc: */ wchar wc);
	TechTypes getTechPrereq() const { return m_eTechPrereq; }
	UnitClassTypes getFreeUnitClass() const { return m_eFreeUnitClass; }
	int getSpreadFactor() const { return m_iSpreadFactor; }
	MissionTypes getMissionType() const { return m_eMissionType; }
	void setMissionType(int iNewType);
	// XANA: 06-27-2026 Unique Civics and Religions
	CivilizationTypes getPrereqCivilization() const { return m_iPrereqCivilization; }
	LeaderHeadTypes getPrereqLeader() const { return m_iPrereqLeader; }
	bool isMinorOrganization() const { return m_bMinorOrganization; }
	// XANA: 06-27-2026 Unique Civics and Religions

	const TCHAR* getMovieFile() const;
	const TCHAR* getMovieSound() const;
	const TCHAR* getSound() const;

	bool read(CvXMLLoadUtility* pXML);
	// XANA: 06-27-2026 Unique Civics and Religions
	bool readPass3();
	// XANA: 06-27-2026 Unique Civics and Religions

protected:
	wchar m_wcSymbol; // advc
	TechTypes m_eTechPrereq;
	UnitClassTypes m_eFreeUnitClass;
	MissionTypes m_eMissionType;
	int m_iSpreadFactor;
	// XANA: 06-27-2026 Unique Civics and Religions
	int m_iPrereqCivilization;
	int m_iPrereqLeader;
	bool m_bMinorOrganization;
	// XANA: 06-27-2026 Unique Civics and Religions

	CvString m_szMovieFile;
	CvString m_szMovieSound;
	CvString m_szSound;
};

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvReligionInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvReligionInfo : public CvOrganizationInfo
{
public: // All the const functions are exposed to Python
	CvReligionInfo();
	~CvReligionInfo();

	wchar getHolyCityChar() const;
	void setHolyCityChar(wchar c);
	int getNumFreeUnits() const;

	const TCHAR* getTechButton() const;
	const TCHAR* getGenericTechButton() const;
	const TCHAR* getButtonDisabled() const;

	const wchar* getAdjectiveKey() const;
	std::wstring pyGetAdjectiveKey() { return getAdjectiveKey(); }

	// Array access:

	int getGlobalReligionCommerce(int i) const;
	int* getGlobalReligionCommerceArray() const;
	int getHolyCityCommerce(int i) const;
	int* getHolyCityCommerceArray() const;
	int getStateReligionCommerce(int i) const;
	int* getStateReligionCommerceArray() const;

	bool read(CvXMLLoadUtility* pXML);

	static bool isReligionTech(TechTypes eTech); // advc.003w: Moved from CvGameCoreUtils

protected:
	wchar m_cHolyCityChar; // advc: was int
	int m_iNumFreeUnits;

	CvString m_szTechButton;
	CvString m_szGenericTechButton;
	CvWString m_szAdjectiveKey;

	int* m_paiGlobalReligionCommerce;
	int* m_paiHolyCityCommerce;
	int* m_paiStateReligionCommerce;
};

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvCorporationInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvCorporationInfo : public CvOrganizationInfo
{
public: // All the const functions are exposed to Python
	CvCorporationInfo();
	virtual ~CvCorporationInfo();

	wchar getHeadquarterChar() const;
	void setHeadquarterChar(wchar c);
	int getSpreadCost() const { return m_iSpreadCost; }
	int getMaintenance() const { return m_iMaintenance; }
	BonusTypes getBonusProduced() const { return m_eBonusProduced; }

	// Array access:
	int getNumPrereqBonuses() const { return m_aePrereqBonuses.size(); }
	BonusTypes getPrereqBonus(int i) const
	{
		FAssertBounds(0, getNumPrereqBonuses(), i);
		return m_aePrereqBonuses[i];
	}
	int py_getPrereqBonus(int i) const;
	// </advc.003t>
	int getHeadquarterCommerce(int i) const;
	int* getHeadquarterCommerceArray() const;
	int getCommerceProduced(int i) const;
	int* getCommerceProducedArray() const;
	int getYieldProduced(int i) const;
	int* getYieldProducedArray() const;

	bool read(CvXMLLoadUtility* pXML);

	static bool isCorporationTech(TechTypes eTech); // advc.003w: Moved from CvGameCoreUtils; unused.

protected:
	wchar m_cHeadquarterChar; // advc: was int
	int m_iSpreadCost;
	int m_iMaintenance;
	BonusTypes m_eBonusProduced;

	std::vector<BonusTypes> m_aePrereqBonuses; // advc.003t: was int*
	int* m_paiHeadquarterCommerce;
	int* m_paiCommerceProduced;
	int* m_paiYieldProduced;
};

// XANA: 06-27-2026 Unique Civics and Religions
class CvHybridOrganizationInfo : public CvOrganizationInfo
{
public:
	CvHybridOrganizationInfo();
	~CvHybridOrganizationInfo();
	
	/*
	XANA (note):
	The hybrid organization is founded by finishing construction of a marked Building.
	It sets a flag in the city that builds that Building, stating that the local religion is now available.
	The Trigger Relgion is a local Religion, which starts spreading automatically.
	The local Relgion, as a minor faith, does not come with an Missionary unit to spread it manually.
	The hosting/holy city, instead, spreads the local Religion via trade routes to other cities in the world.
	These cites must meet a set of citeria required by the hybrid organization in order for the minor faith to spread successfully.
	*/
	ReligionTypes getTriggerReligion() const { return m_eTriggerReligion; }
	
	/*
	XANA (note):
	The hybrid organization is founded by finishing construction of a marked Building.
	It sets a flag in the city that builds that Building, stating that the local corporation is active.
	The Trigger Corporation is a local organization, which provides specialized services to the hosting/holy city.
	The local Corporation, as a minor corp, does not spread automatically like other Corporations.
	It also does not come with an Executive unit, thus it cannot spread in the typical method.
	In order to spread the actual Corporation, build more instances of the Building in cities.
	*/
	CorporationTypes getTriggerCorporation() const { return m_eTriggerCorporation; }
	
	int getMinUnhappinessRequired() const { return m_iMinUnhappinessRequired; }
	int getBaseSpreadChancePercentage() const { return m_iBaseSpreadChancePercentage; }
	int getWithdrawalUnhappinessTurns() const { return m_iWithdrawalUnhappinessTurns; }
	
	bool read(CvXMLLoadUtility* pXML);

protected:
	ReligionTypes m_eTriggerReligion;
	CorporationTypes m_eTriggerCorporation;
	int m_iMinUnhappinessRequired;
	int m_iBaseSpreadChancePercentage;
	int m_iWithdrawalUnhappinessTurns;
};

// XANA: 06-27-2026 Unique Civics and Religions

#endif
