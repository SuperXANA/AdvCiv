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


template<class T>void check(){for(int a=0;a<2;++a)for(int b=0;b<2;++b)for(int m=-50;m<=100;m+=50){T src;src.bPreferredChoice=a!=0;src.bNotPreferredChoice=b!=0;src.iUnitValueModifierPercent=m;UnitPreferenceData out;copyUnitPreferenceChoice(out,src);assert(out.isPreferredChoice()==src.isPreferredChoice());assert(out.isNotPreferredChoice()==src.isNotPreferredChoice());assert(out.getUnitValueModifierPercent()==m);assert(out.getUnitType()==NO_UNIT);}}
int main(){check<UnitPreferenceData>();check<UnitClassPreferenceData>();check<UnitCombatPreferenceData>();}
