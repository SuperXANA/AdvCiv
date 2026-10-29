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
struct CvUnitPreferenceInfo{
 int mask;UnitPreferenceData unit;UnitClassPreferenceData cls;UnitCombatPreferenceData combat;
 int getUnitPreferenceIndex(int)const{return(mask&1)?0:-1;}
 int getUnitClassPreferenceIndex(int)const{return(mask&2)?0:-1;}
 int getUnitCombatPreferenceIndex(int)const{return(mask&4)?0:-1;}
 const UnitPreferenceData& getUnitPreference(int)const{return unit;}
 const UnitClassPreferenceData& getUnitClassPreference(int)const{return cls;}
 const UnitCombatPreferenceData& getUnitCombatPreference(int)const{return combat;}
};
struct Global{CvUnitPreferenceInfo info[2];const CvUnitPreferenceInfo& getInfo(int i)const{return info[i];}}GC;
int leader,civ;int AI_getLeaderUnitPreferences(){return leader;}int AI_getCivilizationUnitPreferences(){return civ;}
int evaluate(){int eUnit=0,iValue=1;struct Unit{int getUnitClassType()const{return 1;}int getUnitCombatType()const{return 2;}}u;
	UnitPreferenceData leaderChoice, civilizationChoice;
	UnitPreferenceData const* pLeaderPref = NULL;
	UnitPreferenceData const* pCivilizationPref = NULL;
	
	if (AI_getLeaderUnitPreferences() != NO_UNITPREFERENCE)
	{
		CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getLeaderUnitPreferences());
		int const iPrefIndex = kPref.getUnitPreferenceIndex(eUnit); 
		if (iPrefIndex != -1)
		{
			copyUnitPreferenceChoice(leaderChoice, kPref.getUnitPreference(iPrefIndex));
			pLeaderPref = &leaderChoice;
		}
	}
	if (AI_getCivilizationUnitPreferences() != NO_UNITPREFERENCE)
	{
		CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getCivilizationUnitPreferences());
		int const iPrefIndex = kPref.getUnitPreferenceIndex(eUnit); 
		if (iPrefIndex != -1)
		{
			copyUnitPreferenceChoice(civilizationChoice, kPref.getUnitPreference(iPrefIndex));
			pCivilizationPref = &civilizationChoice;
		}
	}
	
	bool bHasLeaderPreference = (pLeaderPref != NULL);
	bool bHasCivilizationPreference = (pCivilizationPref != NULL);
	
	if (!bHasLeaderPreference && !bHasCivilizationPreference)
	{
		if (AI_getLeaderUnitPreferences() != NO_UNITPREFERENCE)
		{
			CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getLeaderUnitPreferences());
			int const iPrefIndex = kPref.getUnitClassPreferenceIndex(u.getUnitClassType()); 
			if (iPrefIndex != -1)
			{
				copyUnitPreferenceChoice(leaderChoice, kPref.getUnitClassPreference(iPrefIndex));
			pLeaderPref = &leaderChoice;
			}
		}
		if (AI_getCivilizationUnitPreferences() != NO_UNITPREFERENCE)
		{
			CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getCivilizationUnitPreferences());
			int const iPrefIndex = kPref.getUnitClassPreferenceIndex(u.getUnitClassType()); 
			if (iPrefIndex != -1)
			{
				copyUnitPreferenceChoice(civilizationChoice, kPref.getUnitClassPreference(iPrefIndex));
			pCivilizationPref = &civilizationChoice;
			}
		}
		bHasLeaderPreference = (pLeaderPref != NULL);
		bHasCivilizationPreference = (pCivilizationPref != NULL);
	}
	if (!bHasLeaderPreference && !bHasCivilizationPreference)
	{
		if (AI_getLeaderUnitPreferences() != NO_UNITPREFERENCE)
		{
			CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getLeaderUnitPreferences());
			int const iPrefIndex = kPref.getUnitCombatPreferenceIndex(u.getUnitCombatType()); 
			if (iPrefIndex != -1)
			{
				copyUnitPreferenceChoice(leaderChoice, kPref.getUnitCombatPreference(iPrefIndex));
			pLeaderPref = &leaderChoice;
			}
		}
		if (AI_getCivilizationUnitPreferences() != NO_UNITPREFERENCE)
		{
			CvUnitPreferenceInfo const& kPref = GC.getInfo(AI_getCivilizationUnitPreferences());
			int const iPrefIndex = kPref.getUnitCombatPreferenceIndex(u.getUnitCombatType()); 
			if (iPrefIndex != -1)
			{
				copyUnitPreferenceChoice(civilizationChoice, kPref.getUnitCombatPreference(iPrefIndex));
			pCivilizationPref = &civilizationChoice;
			}
		}
		bHasLeaderPreference = (pLeaderPref != NULL);
		bHasCivilizationPreference = (pCivilizationPref != NULL);
	}
		
	if (bHasLeaderPreference)
	{
		UnitPreferenceData const& kPrefData = *pLeaderPref;
		if (kPrefData.isPreferredChoice())
		{
			iValue += 10000;
		}
		else if (kPrefData.isNotPreferredChoice())
		{
			iValue = 0;
		}
	}
	if (bHasCivilizationPreference)
	{
		UnitPreferenceData const& kPrefData = *pCivilizationPref;
		if (kPrefData.isPreferredChoice())
		{
			iValue += 10000;
		}
		else if (kPrefData.isNotPreferredChoice())
		{
			iValue = 0;
		}
	}
return iValue;}
template<class T>void flags(T& d,int f){d.bPreferredChoice=(f&1)!=0;d.bNotPreferredChoice=(f&2)!=0;}
int main(){int cases=0;for(int m=0;m<64;++m)for(int f=0;f<16;++f)for(int present=0;present<4;++present){leader=(present&1)?0:-1;civ=(present&2)?1:-1;GC.info[0].mask=m&7;GC.info[1].mask=m>>3;for(int i=0;i<2;++i){int bits=i?(f>>2):(f&3);flags(GC.info[i].unit,bits);flags(GC.info[i].cls,bits);flags(GC.info[i].combat,bits);}int level=0;for(int k=1;k<=4;k*=2){if((leader>=0&&(GC.info[0].mask&k))||(civ>=0&&(GC.info[1].mask&k))){level=k;break;}}int expected=1;for(int i=0;i<2;++i)if((present&(1<<i))&&(GC.info[i].mask&level)){int bits=i?(f>>2):(f&3);if(bits&1)expected+=10000;else if(bits&2)expected=0;}assert(evaluate()==expected);++cases;}assert(cases==4096);}
