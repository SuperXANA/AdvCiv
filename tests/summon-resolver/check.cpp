// Complete actual resolver; selector callbacks and event metadata are stubs.
#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>
typedef int LeaderHeadTypes;typedef int CivilizationTypes;
enum { NO_LEADER=-1,NO_CIVILIZATION=-1 };
int calls=0;
struct CvEventInfo {
 int leader,civ;bool leaderArray,civArray;int weight;
 int getSummonLeader()const{return leader;} int getSummonCivilization()const{return civ;}
 int* getSummonLeaderWeightArray()const{return leaderArray?const_cast<int*>(&weight):0;}
 int* getSummonCivilizationWeightArray()const{return civArray?const_cast<int*>(&weight):0;}
};
LeaderHeadTypes selectWeightedSummonLeader(CvEventInfo const&,std::vector<int>& v){++calls;return v.empty()?-1:v[0];}
CivilizationTypes selectWeightedSummonCiv(CvEventInfo const&,std::vector<int>& v){++calls;return v.empty()?-1:v[0];}
CivilizationTypes selectCompatibleCivForSummonLeader(int,CvEventInfo const*,std::vector<int>& v){++calls;return v.empty()?-1:v[0];}
LeaderHeadTypes selectCompatibleLeaderForSummonCiv(int,CvEventInfo const*,std::vector<int>& v){++calls;return v.empty()?-1:v[0];}
	bool resolveSummonLeaderAndCiv(const CvEventInfo& kEvent, std::vector<LeaderHeadTypes>& aeEligibleLeaders, std::vector<CivilizationTypes>& aeEligibleCivs, LeaderHeadTypes& eOutLeader, CivilizationTypes& eOutCiv)
	{
		bool const bHasSpecificLeader = (kEvent.getSummonLeader() != NO_LEADER);
		bool const bHasSpecificCiv = (kEvent.getSummonCivilization() != NO_CIVILIZATION);
		bool const bHasLeaderArray = (kEvent.getSummonLeaderWeightArray() != NULL);
		bool const bHasCivArray = (kEvent.getSummonCivilizationWeightArray() != NULL);
		/*
		 * Nothing to resolve.
		 */
		if (!bHasSpecificLeader &&
			!bHasSpecificCiv &&
			!bHasLeaderArray &&
			!bHasCivArray)
		{
			return false;
		}
		/*
		 * ============================================================
		 * STEP 1: Resolve explicitly specified values.
		 * ============================================================
		 */
		// XANA: 10-30-2026 Validate explicit summon IDs against unused pools (ChatGPT)
		if (bHasSpecificLeader &&
			std::find(aeEligibleLeaders.begin(), aeEligibleLeaders.end(),
				(LeaderHeadTypes)kEvent.getSummonLeader()) == aeEligibleLeaders.end())
			return false;
		if (bHasSpecificCiv &&
			std::find(aeEligibleCivs.begin(), aeEligibleCivs.end(),
				(CivilizationTypes)kEvent.getSummonCivilization()) == aeEligibleCivs.end())
			return false;
		// XANA: 10-30-2026 Validate explicit summon IDs against unused pools (ChatGPT)
		if (bHasSpecificLeader)
		{
			eOutLeader = (LeaderHeadTypes)kEvent.getSummonLeader();
		}
		if (bHasSpecificCiv)
		{
			eOutCiv = (CivilizationTypes)kEvent.getSummonCivilization();
		}
		// Explicit pairs take precedence over weighted arrays and need no draw.
		if (bHasSpecificLeader && bHasSpecificCiv)
			return true;
		/*
		 * ============================================================
		 * STEP 2: If we have a specific value on one side, resolve
		 * the other side around it.
		 * ============================================================
		 */
		if (eOutLeader != NO_LEADER &&
			eOutCiv == NO_CIVILIZATION)
		{
			/*
			 * Specific leader + civ array.
			 */
			if (bHasCivArray)
			{
				eOutCiv = selectCompatibleCivForSummonLeader(eOutLeader, &kEvent, aeEligibleCivs);
			}
			/*
			 * If the civ filter couldn't produce anything, fall back
			 * to any compatible civilization.
			 */
			if (eOutCiv == NO_CIVILIZATION)
			{
				eOutCiv = selectCompatibleCivForSummonLeader(eOutLeader, NULL, aeEligibleCivs);
			}

			return (eOutCiv != NO_CIVILIZATION);
		}
		if (eOutCiv != NO_CIVILIZATION &&
			eOutLeader == NO_LEADER)
		{
			/*
			 * Specific civ + leader array.
			 */
			if (bHasLeaderArray)
			{
				eOutLeader = selectCompatibleLeaderForSummonCiv(eOutCiv, &kEvent, aeEligibleLeaders);
			}
			/*
			 * Fall back to any compatible leader.
			 */
			if (eOutLeader == NO_LEADER)
			{
				eOutLeader = selectCompatibleLeaderForSummonCiv(eOutCiv, NULL, aeEligibleLeaders);
			}
			return (eOutLeader != NO_LEADER);
		}
		/*
		 * ============================================================
		 * STEP 3: Neither side is currently resolved.
		 *
		 * Try the leader side first if it exists.
		 * ============================================================
		 */
		if (bHasLeaderArray)
		{
			eOutLeader = selectWeightedSummonLeader(kEvent, aeEligibleLeaders);
			if (eOutLeader != NO_LEADER)
			{
				/*
				 * We successfully found a leader. Now find a compatible
				 * civilization, respecting the event's civ filter.
				 */
				if (bHasCivArray)
				{
					eOutCiv = selectCompatibleCivForSummonLeader(eOutLeader, &kEvent, aeEligibleCivs);
				}
				/*
				 * If the civ filter produced nothing, any compatible
				 * civ is acceptable.
				 */
				if (eOutCiv == NO_CIVILIZATION)
				{
					eOutCiv = selectCompatibleCivForSummonLeader(eOutLeader, NULL, aeEligibleCivs);
				}
				if (eOutCiv != NO_CIVILIZATION)
				{
					return true;
				}
				/*
				 * Important:
				 *
				 * We found a leader, but couldn't build a valid pair
				 * around it. Don't immediately return false. We can
				 * still try the civilization side below.
				 */
				eOutLeader = NO_LEADER;
			}
		}
		/*
		 * ============================================================
		 * STEP 4: Try the civilization side if the leader-first path
		 * failed.
		 * ============================================================
		 */
		if (bHasCivArray)
		{
			eOutCiv = selectWeightedSummonCiv(kEvent, aeEligibleCivs);
			if (eOutCiv != NO_CIVILIZATION)
			{
				/*
				 * Prefer leaders allowed by the event's leader filter.
				 */
				if (bHasLeaderArray)
				{
					eOutLeader = selectCompatibleLeaderForSummonCiv(eOutCiv, &kEvent, aeEligibleLeaders);
				}
				/*
				 * Fall back to any compatible leader.
				 */
				if (eOutLeader == NO_LEADER)
				{
					eOutLeader = selectCompatibleLeaderForSummonCiv(eOutCiv, NULL, aeEligibleLeaders);
				}
				if (eOutLeader != NO_LEADER)
				{
					return true;
				}
			}
		}
		/*
		 * No valid leader/civ pair could be constructed.
		 */
		eOutLeader = NO_LEADER;
		eOutCiv = NO_CIVILIZATION;
		return false;
	}
	
int main() {
 int ids[]={-1,0,1,2,99};int count=0,explicitPairs=0,rejected=0;
 for(int lm=0;lm<8;++lm)for(int cm=0;cm<8;++cm)for(int li=0;li<5;++li)for(int ci=0;ci<5;++ci)for(int flags=0;flags<4;++flags) {
  std::vector<int> leaders,civs;
  for(int i=0;i<3;++i){if(lm&(1<<i))leaders.push_back(i);if(cm&(1<<i))civs.push_back(i);}
  CvEventInfo e={ids[li],ids[ci],(flags&1)!=0,(flags&2)!=0,1};
  bool hasL=e.leader!=-1,hasC=e.civ!=-1;
  bool eligibleL=!hasL||std::find(leaders.begin(),leaders.end(),e.leader)!=leaders.end();
  bool eligibleC=!hasC||std::find(civs.begin(),civs.end(),e.civ)!=civs.end();
  int l=-1,c=-1;calls=0;
  bool ok=resolveSummonLeaderAndCiv(e,leaders,civs,l,c);
  bool expected=false;
  if(eligibleL&&eligibleC) {
   if(hasL&&hasC)expected=true;
   else if(hasL)expected=!civs.empty();
   else if(hasC)expected=!leaders.empty();
   else expected=(flags!=0)&&!leaders.empty()&&!civs.empty();
  }
  assert(ok==expected);
  if(!eligibleL||!eligibleC){assert(calls==0);++rejected;}
  if(eligibleL&&eligibleC&&hasL&&hasC) {
   assert(l==e.leader&&c==e.civ);assert(calls==0);++explicitPairs;
  }
  if(ok){
   assert(std::find(leaders.begin(),leaders.end(),l)!=leaders.end());
   assert(std::find(civs.begin(),civs.end(),c)!=civs.end());
   if(hasL)assert(l==e.leader);
   if(hasC)assert(c==e.civ);
  }
  // Final array-search failure clears partial outputs.
  if(eligibleL&&eligibleC&&!hasL&&!hasC&&flags!=0&&!ok){assert(l==-1&&c==-1);}
  ++count;
 }
 // Focused regressions with observable selector counts and stale output state.
 {
  std::vector<int> leaders(1,0),civs(1,0);
  CvEventInfo pair={0,0,false,false,1};int l=-1,c=-1;calls=0;
  assert(resolveSummonLeaderAndCiv(pair,leaders,civs,l,c));
  assert(l==0&&c==0&&calls==0);
  CvEventInfo unavailable={1,-1,false,false,1};l=-1;c=-1;calls=0;
  assert(!resolveSummonLeaderAndCiv(unavailable,leaders,civs,l,c));assert(calls==0);
  CvEventInfo failed={-1,-1,true,false,1};leaders.clear();l=77;c=88;calls=0;
  assert(!resolveSummonLeaderAndCiv(failed,leaders,civs,l,c));assert(l==-1&&c==-1);
 }
 std::cout<<count<<" resolver configurations passed; "<<explicitPairs<<" explicit pairs, "<<rejected<<" ineligible-ID rejections\n";
}
