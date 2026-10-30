#include <cassert>
#include <climits>
#include <cstddef>
#include <iostream>
#include <vector>
enum LeaderHeadTypes {NO_LEADER=-1,L0,L1,L2,LEADER_BOUND=127};
enum CivilizationTypes {NO_CIVILIZATION=-1,C0,C1,C2,CIV_BOUND=127};
enum {GAMEOPTION_LEAD_ANY_CIV};
struct CvCivilizationInfo{bool leaders[3];bool isLeaders(int l)const{return leaders[l];}};
struct Game{bool any;bool isOption(int)const{return any;}};
struct Globals{Game game;CvCivilizationInfo civs[3];int getNumLeaderHeadInfos()const{return 3;}int getNumCivilizationInfos()const{return 3;}CvCivilizationInfo const& getInfo(CivilizationTypes c)const{return civs[c];}Game const& getGame()const{return game;}} GC;
struct CvEventInfo{int weights[3];bool present;int* getSummonLeaderWeightArray()const{return present?const_cast<int*>(weights):NULL;}int* getSummonCivilizationWeightArray()const{return present?const_cast<int*>(weights):NULL;}int getSummonLeaderWeight(LeaderHeadTypes l)const{return weights[l];}int getSummonCivilizationWeight(CivilizationTypes c)const{return weights[c];}};
int nextRoll=0,calls=0,expectedBound=0;
int roll(int n){assert(n>0&&n<=65535&&n==expectedBound);assert(nextRoll>=0&&nextRoll<n);++calls;return nextRoll;}
#define SyncRandNum(n) roll(static_cast<int>(n))
	// XANA: 10-30-2026 Bounded summon weight accumulation (ChatGPT)
	bool addSummonWeight(int& iTotalWeight, int iWeight)
	{
		if (iWeight <= 0)
			return true;
		// CvRandom::get accepts int but its random bound is unsigned-short sized.
		if (iWeight > 65535 - iTotalWeight)
			return false;
		iTotalWeight += iWeight;
		return true;
	}
	// XANA: 10-30-2026 Bounded summon weight accumulation (ChatGPT)


	LeaderHeadTypes selectWeightedSummonLeader(const CvEventInfo& kEvent, std::vector<LeaderHeadTypes>& aeEligibleLeaders)
	{
		int* piChances = kEvent.getSummonLeaderWeightArray();
		if (piChances == NULL)
			return NO_LEADER;

		int iTotalWeight = 0;
		int const iEnumLength = (int)aeEligibleLeaders.size();
		
		for (int i = 0; i < iEnumLength; ++i)
		{
			if (!addSummonWeight(iTotalWeight, piChances[aeEligibleLeaders[i]]))
				return NO_LEADER;
		}

		if (iTotalWeight <= 0)
			return NO_LEADER;
		
		int iRoll = SyncRandNum(iTotalWeight);
		for (int i = 0; i < iEnumLength; ++i)
		{
			LeaderHeadTypes eLeader = aeEligibleLeaders[i];
			if (piChances[eLeader] > 0)
			{
				iRoll -= piChances[eLeader];
				if (iRoll < 0)
					return eLeader;
			}
		}
		return NO_LEADER;
	}

	// Picks a civilization from the event's SummonCivilizationToGameRandomChances array.
	// Skips civilizations already present in the game.
	// Returns NO_CIVILIZATION if the array is missing or has zero valid weight.
	CivilizationTypes selectWeightedSummonCiv(const CvEventInfo& kEvent, std::vector<CivilizationTypes>& aeEligibleCivs)
	{
		int* piChances = kEvent.getSummonCivilizationWeightArray();
		if (piChances == NULL)
			return NO_CIVILIZATION;

		int iTotalWeight = 0;
		int const iEnumLength = (int)aeEligibleCivs.size();
		
		for (int i = 0; i < iEnumLength; ++i)
		{
			if (!addSummonWeight(iTotalWeight, piChances[aeEligibleCivs[i]]))
				return NO_CIVILIZATION;
		}

		if (iTotalWeight <= 0)
			return NO_CIVILIZATION;
		
		int iRoll = SyncRandNum(iTotalWeight);
		for (int i = 0; i < iEnumLength; ++i)
		{
			CivilizationTypes eCiv = aeEligibleCivs[i];
			if (piChances[eCiv] > 0)
			{
				iRoll -= piChances[eCiv];
				if (iRoll < 0)
					return eCiv;
			}
		}
		return NO_CIVILIZATION;
	}

	// Given a leader, finds all civs that support them AND are not already in the game.
	// If pEventFilter is non-NULL, only civs with a positive weight in the event's
	// civilization chance array are considered (and also must not be in-game).
	// When no filter is used, compatible civs are chosen with equal probability.
	CivilizationTypes selectCompatibleCivForSummonLeader(LeaderHeadTypes eLeader, const CvEventInfo* pEventFilter, const std::vector<CivilizationTypes>& aeEligibleCivs)
	{
		if (eLeader < 0 || eLeader >= GC.getNumLeaderHeadInfos())
			return NO_CIVILIZATION;

		std::vector<CivilizationTypes> aeCivs;
		std::vector<int> aiWeights;
		int iTotalWeight = 0;
		int const iEnumLength = (int)aeEligibleCivs.size();

		for (int i = 0; i < iEnumLength; ++i)
		{
			CivilizationTypes const eCiv = aeEligibleCivs[i];
			if (eCiv < 0 || eCiv >= GC.getNumCivilizationInfos())
				continue;
			CvCivilizationInfo const& kCiv = GC.getInfo(eCiv);
			if (!GC.getGame().isOption(GAMEOPTION_LEAD_ANY_CIV) && !kCiv.isLeaders(eLeader))
				continue;

			if (pEventFilter != NULL && pEventFilter->getSummonCivilizationWeightArray() != NULL)
			{
				int iWeight = pEventFilter->getSummonCivilizationWeight(eCiv);
				if (iWeight <= 0)
					continue;
				aeCivs.push_back(eCiv);
				aiWeights.push_back(iWeight);
				if (!addSummonWeight(iTotalWeight, iWeight))
					return NO_CIVILIZATION;
			}
			else
			{
				aeCivs.push_back(eCiv);
				aiWeights.push_back(1);
				if (!addSummonWeight(iTotalWeight, 1))
					return NO_CIVILIZATION;
			}
		}
		if (aeCivs.empty())
			return NO_CIVILIZATION;

		// No filter: equal weight (simple uniform random)
		if (pEventFilter == NULL || pEventFilter->getSummonCivilizationWeightArray() == NULL)
			return aeCivs[SyncRandNum(aeCivs.size())];
		
		int iRoll = SyncRandNum(iTotalWeight);
		for (size_t i = 0; i < aeCivs.size(); ++i)
		{
			iRoll -= aiWeights[i];
			if (iRoll < 0)
				return aeCivs[i];
		}
		return aeCivs.back();
	}

	// Given a civilization, finds all leaders available to it AND not already in the game.
	// If pEventFilter is non-NULL, only leaders with a positive weight in the event's
	// leader chance array are considered (and also must not be in-game).
	LeaderHeadTypes selectCompatibleLeaderForSummonCiv(CivilizationTypes eCiv, const CvEventInfo* pEventFilter, const std::vector<LeaderHeadTypes>& aeEligibleLeaders)
	{
		if (eCiv < 0 || eCiv >= GC.getNumCivilizationInfos())
			return NO_LEADER;

		CvCivilizationInfo const& kCiv = GC.getInfo(eCiv);
		std::vector<LeaderHeadTypes> aeLeaders;
		std::vector<int> aiWeights;
		int iTotalWeight = 0;
		int const iEnumLength = (int)aeEligibleLeaders.size();

		for (int i = 0; i < iEnumLength; ++i)
		{
			LeaderHeadTypes const eLeader = aeEligibleLeaders[i];
			if (eLeader < 0 || eLeader >= GC.getNumLeaderHeadInfos())
				continue;
			if (!GC.getGame().isOption(GAMEOPTION_LEAD_ANY_CIV) && !kCiv.isLeaders(eLeader))
				continue;

			if (pEventFilter != NULL && pEventFilter->getSummonLeaderWeightArray() != NULL)
			{
				int iWeight = pEventFilter->getSummonLeaderWeight(eLeader);
				if (iWeight <= 0)
					continue;
				aeLeaders.push_back(eLeader);
				aiWeights.push_back(iWeight);
				if (!addSummonWeight(iTotalWeight, iWeight))
					return NO_LEADER;
			}
			else
			{
				aeLeaders.push_back(eLeader);
				aiWeights.push_back(1);
				if (!addSummonWeight(iTotalWeight, 1))
					return NO_LEADER;
			}
		}
		if (aeLeaders.empty())
			return NO_LEADER;

		if (pEventFilter == NULL || pEventFilter->getSummonLeaderWeightArray() == NULL)
			return aeLeaders[SyncRandNum(aeLeaders.size())];
		
		int iRoll = SyncRandNum(iTotalWeight);
		for (size_t i = 0; i < aeLeaders.size(); ++i)
		{
			iRoll -= aiWeights[i];
			if (iRoll < 0)
				return aeLeaders[i];
		}
		return aeLeaders.back();
	}


std::vector<LeaderHeadTypes> leaders;std::vector<CivilizationTypes> civs;
int drawChecks=0,families=0;
void checkWeights(int a,int b,int c){CvEventInfo event={{a,b,c},true};int w[3]={a,b,c};
double total=0;for(int i=0;i<3;++i)if(w[i]>0)total+=w[i]; // Exact for three int samples.
bool supported=total>0&&total<=65535;
expectedBound=supported?static_cast<int>(total):0;
int draws=supported?expectedBound:1;
for(int r=0;r<draws;++r){nextRoll=r;calls=0;int expected=-1;if(supported){int offset=r;for(int i=0;i<3;++i)if(w[i]>0){if(offset<w[i]){expected=i;break;}offset-=w[i];}}
assert(static_cast<int>(selectWeightedSummonLeader(event,leaders))==expected);
assert(static_cast<int>(selectWeightedSummonCiv(event,civs))==expected);
assert(static_cast<int>(selectCompatibleCivForSummonLeader(L0,&event,civs))==expected);
assert(static_cast<int>(selectCompatibleLeaderForSummonCiv(C0,&event,leaders))==expected);
assert(calls==(supported?4:0));drawChecks+=4;
}++families;}
int main(int argc,char**){GC.game.any=true;for(int i=0;i<3;++i)for(int j=0;j<3;++j)GC.civs[i].leaders[j]=true;
leaders.push_back(L0);leaders.push_back(L1);leaders.push_back(L2);civs.push_back(C0);civs.push_back(C1);civs.push_back(C2);
if(argc>1){checkWeights(INT_MAX,INT_MAX,INT_MAX);return 0;}
const int vals[]={-2,0,1,2,4};for(int a=0;a<5;++a)for(int b=0;b<5;++b)for(int c=0;c<5;++c)checkWeights(vals[a],vals[b],vals[c]);
checkWeights(65535,0,0);checkWeights(65534,1,0);checkWeights(65535,1,0);checkWeights(INT_MAX,INT_MAX,INT_MAX);checkWeights(INT_MIN,1,2);checkWeights(-INT_MAX,2,3);
CvEventInfo absent={{1,2,3},false};calls=0;
assert(selectWeightedSummonLeader(absent,leaders)==NO_LEADER);assert(selectWeightedSummonCiv(absent,civs)==NO_CIVILIZATION);assert(calls==0);
for(int r=0;r<3;++r){expectedBound=3;nextRoll=r;assert(static_cast<int>(selectCompatibleCivForSummonLeader(L0,NULL,civs))==r);assert(static_cast<int>(selectCompatibleLeaderForSummonCiv(C0,NULL,leaders))==r);assert(static_cast<int>(selectCompatibleCivForSummonLeader(L0,&absent,civs))==r);assert(static_cast<int>(selectCompatibleLeaderForSummonCiv(C0,&absent,leaders))==r);}
leaders.clear();civs.clear();CvEventInfo empty={{1,2,3},true};calls=0;assert(selectWeightedSummonLeader(empty,leaders)==NO_LEADER);assert(selectWeightedSummonCiv(empty,civs)==NO_CIVILIZATION);assert(selectCompatibleCivForSummonLeader(L0,&empty,civs)==NO_CIVILIZATION);assert(selectCompatibleLeaderForSummonCiv(C0,&empty,leaders)==NO_LEADER);assert(calls==0);
std::cout<<families<<" weight families; "<<drawChecks<<" weighted draw/result checks plus absent/uniform checks passed\n";
}
