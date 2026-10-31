#include <cstddef>
#include <cassert>
const int NO_UNIT=-1,NO_UNITCLASS=-1,NO_UNITCOMBAT=-1;class CvXMLLoadUtility;
struct UnitCombatPreferenceData
{
	UnitCombatPreferenceData() : iUnitCombat(NO_UNITCOMBAT), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitCombatType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnitCombat;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

struct UnitClassPreferenceData
{
	UnitClassPreferenceData() : iUnitClass(NO_UNITCLASS), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitClassType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnitClass;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

struct UnitPreferenceData
{
	UnitPreferenceData() : iUnit(NO_UNIT), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnit;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

int UnitCombatPreferenceData::getUnitCombatType() const
{
	return iUnitCombat;
}

int UnitCombatPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitCombatPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitCombatPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

int UnitClassPreferenceData::getUnitClassType() const
{
	return iUnitClass;
}

int UnitClassPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitClassPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitClassPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

int UnitPreferenceData::getUnitType() const
{
	return iUnit;
}

int UnitPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}


// XANA: 10-29-2026 Typed unit preference choice snapshots (ChatGPT)
namespace
{
template<class Preference>
void copyUnitPreferenceChoice(UnitPreferenceData& target, Preference const& source)
{
	target.iUnitValueModifierPercent = source.getUnitValueModifierPercent();
	target.bPreferredChoice = source.isPreferredChoice();
	target.bNotPreferredChoice = source.isNotPreferredChoice();
}
}
// XANA: 10-29-2026 Typed unit preference choice snapshots (ChatGPT)


const int NO_UNITPREFERENCE=-1;
struct CvUnitPreferenceInfo
{
	int mask;
	UnitPreferenceData unit;
	UnitClassPreferenceData cls;
	UnitCombatPreferenceData combat;
	int getUnitPreferenceIndex(int) const { return (mask&1)?0:-1; }
	int getUnitClassPreferenceIndex(int i) const
	{
		assert(i != NO_UNITCLASS);
		return (mask&2)?0:-1;
	}
	int getUnitCombatPreferenceIndex(int i) const
	{
		assert(i != NO_UNITCOMBAT);
		return (mask&4)?0:-1;
	}
	const UnitPreferenceData& getUnitPreference(int) const { return unit; }
	const UnitClassPreferenceData& getUnitClassPreference(int) const { return cls; }
	const UnitCombatPreferenceData& getUnitCombatPreference(int) const { return combat; }
};
struct Global
{
	CvUnitPreferenceInfo info[2];
	const CvUnitPreferenceInfo& getInfo(int i) const { return info[i]; }
} GC;
int leader, civ;
int AI_getLeaderUnitPreferences() { return leader; }
int AI_getCivilizationUnitPreferences() { return civ; }

bool copyUnitPreferenceForUnit(CvUnitPreferenceInfo const& kPref,
	int eUnit, int eUnitClass, int eUnitCombat, UnitPreferenceData& kTarget)
{
	int iPrefIndex = kPref.getUnitPreferenceIndex(eUnit);
	if (iPrefIndex != -1)
	{
		copyUnitPreferenceChoice(kTarget, kPref.getUnitPreference(iPrefIndex));
		return true;
	}
	if (eUnitClass != NO_UNITCLASS)
	{
		iPrefIndex = kPref.getUnitClassPreferenceIndex(eUnitClass);
		if (iPrefIndex != -1)
		{
			copyUnitPreferenceChoice(kTarget, kPref.getUnitClassPreference(iPrefIndex));
			return true;
		}
	}
	if (eUnitCombat != NO_UNITCOMBAT)
	{
		iPrefIndex = kPref.getUnitCombatPreferenceIndex(eUnitCombat);
		if (iPrefIndex != -1)
		{
			copyUnitPreferenceChoice(kTarget, kPref.getUnitCombatPreference(iPrefIndex));
			return true;
		}
	}
	return false;
}

int evaluate(int unitClass, int unitCombat)
{
	int const eUnit = 0;
	int iValue = 1;
	UnitPreferenceData leaderChoice, civilizationChoice;
	UnitPreferenceData const* pLeaderPref = NULL;
	UnitPreferenceData const* pCivilizationPref = NULL;
	if (AI_getLeaderUnitPreferences() != NO_UNITPREFERENCE)
	{
		CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getLeaderUnitPreferences());
		if (copyUnitPreferenceForUnit(kPref, eUnit, unitClass, unitCombat, leaderChoice))
			pLeaderPref = &leaderChoice;
	}
	if (AI_getCivilizationUnitPreferences() != NO_UNITPREFERENCE)
	{
		CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getCivilizationUnitPreferences());
		if (copyUnitPreferenceForUnit(kPref, eUnit, unitClass, unitCombat, civilizationChoice))
			pCivilizationPref = &civilizationChoice;
	}
	if (pLeaderPref != NULL)
	{
		if (pLeaderPref->isPreferredChoice()) iValue += 10000;
		else if (pLeaderPref->isNotPreferredChoice()) iValue = 0;
	}
	if (pCivilizationPref != NULL)
	{
		if (pCivilizationPref->isPreferredChoice()) iValue += 10000;
		else if (pCivilizationPref->isNotPreferredChoice()) iValue = 0;
	}
	if (pLeaderPref != NULL && pLeaderPref->iUnitValueModifierPercent != 0)
	{
		iValue *= (100 + pLeaderPref->iUnitValueModifierPercent);
		iValue /= 100;
	}
	if (pCivilizationPref != NULL && pCivilizationPref->iUnitValueModifierPercent != 0)
	{
		iValue *= (100 + pCivilizationPref->iUnitValueModifierPercent);
		iValue /= 100;
	}
	return iValue;
}

template<class T> void flags(T& d, int f)
{
	d.bPreferredChoice = (f&1) != 0;
	d.bNotPreferredChoice = (f&2) != 0;
}

int main()
{
	for (int m=0; m<64; ++m)
	for (int f=0; f<16; ++f)
	for (int present=0; present<4; ++present)
	{
		leader = (present&1)?0:-1;
		civ = (present&2)?1:-1;
		GC.info[0].mask = m&7;
		GC.info[1].mask = m>>3;
		for (int i=0; i<2; ++i)
		{
			int const bits = i?(f>>2):(f&3);
			flags(GC.info[i].unit,bits);
			flags(GC.info[i].cls,bits);
			flags(GC.info[i].combat,bits);
		}
		int expected = 1;
		for (int i=0; i<2; ++i)
		{
			if (!(present&(1<<i))) continue;
			int const mask = GC.info[i].mask;
			int const level = (mask&1)?1:((mask&2)?2:((mask&4)?4:0));
			if (level == 0) continue;
			int const bits = i?(f>>2):(f&3);
			if (bits&1) expected += 10000;
			else if (bits&2) expected = 0;
		}
		assert(evaluate(1,2) == expected);
	}
	// The combat fallback must not query a map with the NO_UNITCOMBAT sentinel.
	leader = 0; civ = -1;
	GC.info[0].mask = 4;
	flags(GC.info[0].combat,1);
	assert(evaluate(NO_UNITCLASS,NO_UNITCOMBAT) == 1);
	// Specificity is resolved separately for leader and civilization.
	leader = 0; civ = 1;
	GC.info[0].mask = 1;
	GC.info[1].mask = 2;
	flags(GC.info[0].unit,1);
	flags(GC.info[1].cls,1);
	assert(evaluate(1,2) == 20001);
	GC.info[0].mask = 2;
	GC.info[1].mask = 4;
	flags(GC.info[0].cls,1);
	flags(GC.info[1].combat,1);
	assert(evaluate(1,2) == 20001);
	// Percent modifiers are applied after the two independent preferences.
	GC.info[0].mask = 1;
	GC.info[1].mask = 2;
	flags(GC.info[0].unit,1);
	flags(GC.info[1].cls,1);
	GC.info[0].unit.iUnitValueModifierPercent = 50;
	GC.info[1].cls.iUnitValueModifierPercent = 50;
	assert(evaluate(1,2) == 45001);
}
