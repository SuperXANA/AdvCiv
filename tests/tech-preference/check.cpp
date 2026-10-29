#include <cassert>
#include <cstddef>
const int NO_TECH=-1,NO_TECHPREFERENCE=-1;class CvXMLLoadUtility;
struct TechPreferenceData
{
	TechPreferenceData() : iTech(NO_TECH), iTechValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getTechType() const;
	int getTechValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iTech;
	int iTechValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

int TechPreferenceData::getTechType() const
{
	return iTech;
}

int TechPreferenceData::getTechValueModifierPercent() const
{
	return iTechValueModifierPercent;
}

bool TechPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool TechPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}


struct CvTechPreferenceInfo {TechPreferenceData data;int getTechPreferenceIndex(int tech)const{return data.iTech==tech?0:-1;}const TechPreferenceData& getTechPreference(int)const{return data;}};
struct Global {CvTechPreferenceInfo info[2];const CvTechPreferenceInfo& getInfo(int i)const{return info[i];}} GC;
int leader,civ;int AI_getLeaderTechPreferences(){return leader;}int AI_getCivilizationTechPreferences(){return civ;}
int eval(int eTech){int iValue=1;
	TechPreferenceData const* pLeaderPref = NULL;
	TechPreferenceData const* pCivilizationPref = NULL;
	
	if (AI_getLeaderTechPreferences() != NO_TECHPREFERENCE)
	{
		CvTechPreferenceInfo const& kPref = GC.getInfo(AI_getLeaderTechPreferences());
		int const iPrefIndex = kPref.getTechPreferenceIndex(eTech); 
		if (iPrefIndex != -1)
		{
			pLeaderPref = &kPref.getTechPreference(iPrefIndex);
		}
	}
	if (AI_getCivilizationTechPreferences() != NO_TECHPREFERENCE)
	{
		CvTechPreferenceInfo const& kPref = GC.getInfo(AI_getCivilizationTechPreferences());
		int const iPrefIndex = kPref.getTechPreferenceIndex(eTech); 
		if (iPrefIndex != -1)
		{
			pCivilizationPref = &kPref.getTechPreference(iPrefIndex);
		}
	}
	
	bool const bHasLeaderPreference = (pLeaderPref != NULL);
	bool const bHasCivilizationPreference = (pCivilizationPref != NULL);
	
	if (bHasLeaderPreference)
	{
		TechPreferenceData const& kPrefData = *pLeaderPref;
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
		TechPreferenceData const& kPrefData = *pCivilizationPref;
		if (kPrefData.isPreferredChoice())
		{
			iValue += 10000;
		}
		else if (kPrefData.isNotPreferredChoice())
		{
			iValue = 0;
		}
	}
	if (bHasLeaderPreference)
	{
		TechPreferenceData const& kPrefData = *pLeaderPref;
		if (kPrefData.getTechValueModifierPercent() != 0)
		{
			iValue *= (100 + kPrefData.getTechValueModifierPercent());
			iValue /= 100;
		}
	}
	if (bHasCivilizationPreference)
	{
		TechPreferenceData const& kPrefData = *pCivilizationPref;
		if (kPrefData.getTechValueModifierPercent() != 0)
		{
			iValue *= (100 + kPrefData.getTechValueModifierPercent());
			iValue /= 100;
		}
	}
return iValue;}
int main(){for(int a=0;a<4;++a)for(int b=0;b<4;++b)for(int lp=-1;lp<2;++lp)for(int cp=-1;cp<2;++cp){leader=lp;civ=cp;for(int i=0;i<2;++i){GC.info[i].data.iTech=7;GC.info[i].data.bPreferredChoice=((i?b:a)&1)!=0;GC.info[i].data.bNotPreferredChoice=((i?b:a)&2)!=0;GC.info[i].data.iTechValueModifierPercent=i?50:-50;}int expected=1;int ids[2]={lp,cp};for(int i=0;i<2;++i)if(ids[i]>=0){const TechPreferenceData& d=GC.info[ids[i]].data;if(d.bPreferredChoice)expected+=10000;else if(d.bNotPreferredChoice)expected=0;}for(int i=0;i<2;++i)if(ids[i]>=0)expected=expected*(100+GC.info[ids[i]].data.iTechValueModifierPercent)/100;assert(eval(7)==expected);assert(eval(8)==1);}}
