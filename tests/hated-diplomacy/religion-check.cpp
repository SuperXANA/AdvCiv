// Complete actual AI_religionValue with reduced engine interfaces.
#include <algorithm>
#include <cassert>
#include <iostream>
#include <vector>
typedef int ReligionTypes;
enum AttitudeTypes { ATTITUDE_FURIOUS, ATTITUDE_ANNOYED, ATTITUDE_CAUTIOUS, ATTITUDE_PLEASED, ATTITUDE_FRIENDLY };
enum { MAJOR_CIV, OTHER_KNOWN_TO, FLAVOR_RELIGION };
#define PROFILE_FUNC() ((void)0)
int range(int n,int lo,int hi) { return std::max(lo,std::min(hi,n)); }
struct CvCity { int grip,pop,team; int getReligionGrip(int)const{return grip;} int getPopulation()const{return pop;} int getTeam()const{return team;} };
struct Other { int religion,id; AttitudeTypes attitude; int getStateReligion()const{return religion;} int getID()const{return id;} };
std::vector<Other> others;
template<int,int> struct PlayerIter { unsigned i; explicit PlayerIter(int):i(0){} bool hasNext()const{return i<others.size();} void operator++(){++i;} Other const* operator->()const{return &others[i];} };
struct CvLeaderHeadInfo { int same,different; int getSameReligionAttitudeChangeLimit()const{return same;} int getDifferentReligionAttitudeChange()const{return different;} };
struct Game { CvCity* holy; bool vote; CvCity* getHolyCity(int)const{return holy;} int calculateReligionPercent(int)const{return 40;} bool isDiploVote(int)const{return vote;} int getVoteSourceReligion(int)const{return 0;} };
struct Globals { Game game; CvLeaderHeadInfo leader; Game& getGame(){return game;} CvLeaderHeadInfo const& getInfo(int)const{return leader;} } GC;
#define FOR_EACH_ENUM2(Name, var) for(int var=0;var<1;++var)
#define FOR_EACH_CITY(p,var) for(unsigned ci=0;ci<cities.size();++ci) for(CvCity const* p=&cities[ci];p!=0;p=0)
struct CvPlayerAI {
 std::vector<CvCity> cities; int flavor,religionCount;
 int getHasReligionCount(int)const{return religionCount;} int getNumCities()const{return static_cast<int>(cities.size());}
 int AI_getFlavorValue(int)const{return flavor;} int getTeam()const{return 1;} int getPersonalityType()const{return 0;}
 AttitudeTypes AI_getAttitude(int id,bool)const{return others[id].attitude;}
 int AI_religionValue(ReligionTypes eReligion)const;
 int AI_religionValueOriginal(ReligionTypes eReligion)const;
 int AI_religionValueBaseline(ReligionTypes eReligion)const;
};
int CvPlayerAI::AI_religionValue(ReligionTypes eReligion) const
{
	PROFILE_FUNC();

	int iValue = 0;

	if (getHasReligionCount(eReligion) == 0)
		return 0;

	int iReligionFlavor = AI_getFlavorValue(FLAVOR_RELIGION);

	FOR_EACH_CITY(pLoopCity, *this)
	{
		iValue += pLoopCity->getReligionGrip(eReligion) * pLoopCity->getPopulation();
		/*	note. this takes into account current state religion and
			number of religious buildings. */
	}
	iValue *= getHasReligionCount(eReligion);
	iValue /= getNumCities();

	// holy city modifier
	CvCity* pHolyCity = GC.getGame().getHolyCity(eReligion);
	if (pHolyCity != NULL && pHolyCity->getTeam() == getTeam())
	{
		iValue *= 110 + 5 * iReligionFlavor + (10 + iReligionFlavor) *
				GC.getGame().calculateReligionPercent(eReligion) / 10;
		iValue /= 100;
	}

	// diplomatic modifier
	int iTotalCivs = 0; // x2
	int iLikedReligionCivs = 0; // x2 for friendly
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	int iHatedReligionCivs = 0; // x2 for furious
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	for (PlayerIter<MAJOR_CIV,OTHER_KNOWN_TO> itOther(getTeam());
		itOther.hasNext(); ++itOther)
	{
		iTotalCivs += 2;
		if (itOther->getStateReligion() == eReligion)
		{
			AttitudeTypes eAttitude = AI_getAttitude(itOther->getID(), false);
			if (eAttitude >= ATTITUDE_PLEASED)
			{
				iLikedReligionCivs++;
				if (eAttitude >= ATTITUDE_FRIENDLY)
					iLikedReligionCivs++;
			}
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
			if (eAttitude <= ATTITUDE_ANNOYED)
			{
				iHatedReligionCivs++;
				if (eAttitude <= ATTITUDE_FURIOUS)
					iHatedReligionCivs++;
			}
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
		}
	}

	/*	up to +100% boost for liked civs having this as their state religion.
		(depending on personality)
		less potential boost if we have aspirations of being a religious leader.
		minimum boost for apostolic palace religion */
	CvLeaderHeadInfo const& kPersonality = GC.getInfo(getPersonalityType());
	int iDiplomaticBase = 50 + 5 * range(kPersonality.getSameReligionAttitudeChangeLimit() -
			kPersonality.getDifferentReligionAttitudeChange(), 0, 10);
	/*	note. with the default xml, the highest the above number can get is
		50 + 5*9 (Zara Yaqob). For most leaders its roughly 50 + 5*5. No one gets 100.
		also, most civs with a high base modifier also have iReligionFlavor > 0;
		and so their final modifier will be reduced. */
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	int iDiplomaticModifier = 10 * iDiplomaticBase * (iLikedReligionCivs / std::max(1, iHatedReligionCivs)) /
			std::max(1, iTotalCivs);
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	iDiplomaticModifier /= 10 + iReligionFlavor;
	// advc.131: AP matters even if diplo modifier already high
	//if (iDiplomaticModifier < iDiplomaticBase/3) {
	FOR_EACH_ENUM2(VoteSource, eVS)
	{	/*  advc.131: Shouldn't check if we're a member now when deciding whether
			we should be one. */
		if (/*isLoyalMember(i) &&*/
			GC.getGame().isDiploVote(eVS) &&
			GC.getGame().getVoteSourceReligion(eVS) == eReligion)
		{
			iDiplomaticModifier += iDiplomaticBase / 3; // advc.131: += instead of =
		}
	}
	iValue *= 100 + iDiplomaticModifier;
	iValue /= 100;

	return iValue;
}

int CvPlayerAI::AI_religionValueOriginal(ReligionTypes eReligion) const
{
	PROFILE_FUNC();

	int iValue = 0;

	if (getHasReligionCount(eReligion) == 0)
		return 0;

	int iReligionFlavor = AI_getFlavorValue(FLAVOR_RELIGION);

	FOR_EACH_CITY(pLoopCity, *this)
	{
		iValue += pLoopCity->getReligionGrip(eReligion) * pLoopCity->getPopulation();
		/*	note. this takes into account current state religion and
			number of religious buildings. */
	}
	iValue *= getHasReligionCount(eReligion);
	iValue /= getNumCities();

	// holy city modifier
	CvCity* pHolyCity = GC.getGame().getHolyCity(eReligion);
	if (pHolyCity != NULL && pHolyCity->getTeam() == getTeam())
	{
		iValue *= 110 + 5 * iReligionFlavor + (10 + iReligionFlavor) *
				GC.getGame().calculateReligionPercent(eReligion) / 10;
		iValue /= 100;
	}

	// diplomatic modifier
	int iTotalCivs = 0; // x2
	int iLikedReligionCivs = 0; // x2 for friendly
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	int iHatedReligionCivs = 0; // x2 for furious
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	for (PlayerIter<MAJOR_CIV,OTHER_KNOWN_TO> itOther(getTeam());
		itOther.hasNext(); ++itOther)
	{
		iTotalCivs += 2;
		if (itOther->getStateReligion() == eReligion)
		{
			AttitudeTypes eAttitude = AI_getAttitude(itOther->getID(), false);
			if (eAttitude >= ATTITUDE_PLEASED)
			{
				iLikedReligionCivs++;
				if (eAttitude >= ATTITUDE_FRIENDLY)
					iLikedReligionCivs++;
			}
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
			if (eAttitude <= ATTITUDE_ANNOYED)
			{
				iHatedReligionCivs++;
				if (eAttitude <= ATTITUDE_FURIOUS)
					iHatedReligionCivs++;
			}
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
		}
	}

	/*	up to +100% boost for liked civs having this as their state religion.
		(depending on personality)
		less potential boost if we have aspirations of being a religious leader.
		minimum boost for apostolic palace religion */
	CvLeaderHeadInfo const& kPersonality = GC.getInfo(getPersonalityType());
	int iDiplomaticBase = 50 + 5 * range(kPersonality.getSameReligionAttitudeChangeLimit() -
			kPersonality.getDifferentReligionAttitudeChange(), 0, 10);
	/*	note. with the default xml, the highest the above number can get is
		50 + 5*9 (Zara Yaqob). For most leaders its roughly 50 + 5*5. No one gets 100.
		also, most civs with a high base modifier also have iReligionFlavor > 0;
		and so their final modifier will be reduced. */
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	int iDiplomaticModifier = 10 * iDiplomaticBase * (iLikedReligionCivs / iHatedReligionCivs) /
			std::max(1, iTotalCivs);
// XANA: 05-24-2025 Hate Civic and Religion Diplomacy
	iDiplomaticModifier /= 10 + iReligionFlavor;
	// advc.131: AP matters even if diplo modifier already high
	//if (iDiplomaticModifier < iDiplomaticBase/3) {
	FOR_EACH_ENUM2(VoteSource, eVS)
	{	/*  advc.131: Shouldn't check if we're a member now when deciding whether
			we should be one. */
		if (/*isLoyalMember(i) &&*/
			GC.getGame().isDiploVote(eVS) &&
			GC.getGame().getVoteSourceReligion(eVS) == eReligion)
		{
			iDiplomaticModifier += iDiplomaticBase / 3; // advc.131: += instead of =
		}
	}
	iValue *= 100 + iDiplomaticModifier;
	iValue /= 100;

	return iValue;
}

int CvPlayerAI::AI_religionValueBaseline(ReligionTypes eReligion) const
{
	PROFILE_FUNC();

	int iValue = 0;

	if (getHasReligionCount(eReligion) == 0)
		return 0;

	int iReligionFlavor = AI_getFlavorValue(FLAVOR_RELIGION);

	FOR_EACH_CITY(pLoopCity, *this)
	{
		iValue += pLoopCity->getReligionGrip(eReligion) * pLoopCity->getPopulation();
		/*	note. this takes into account current state religion and
			number of religious buildings. */
	}
	iValue *= getHasReligionCount(eReligion);
	iValue /= getNumCities();

	// holy city modifier
	CvCity* pHolyCity = GC.getGame().getHolyCity(eReligion);
	if (pHolyCity != NULL && pHolyCity->getTeam() == getTeam())
	{
		iValue *= 110 + 5 * iReligionFlavor + (10 + iReligionFlavor) *
				GC.getGame().calculateReligionPercent(eReligion) / 10;
		iValue /= 100;
	}

	// diplomatic modifier
	int iTotalCivs = 0; // x2
	int iLikedReligionCivs = 0; // x2 for friendly
	for (PlayerIter<MAJOR_CIV,OTHER_KNOWN_TO> itOther(getTeam());
		itOther.hasNext(); ++itOther)
	{
		iTotalCivs += 2;
		if (itOther->getStateReligion() == eReligion)
		{
			AttitudeTypes eAttitude = AI_getAttitude(itOther->getID(), false);
			if (eAttitude >= ATTITUDE_PLEASED)
			{
				iLikedReligionCivs++;
				if (eAttitude >= ATTITUDE_FRIENDLY)
					iLikedReligionCivs++;
			}
		}
	}

	/*	up to +100% boost for liked civs having this as their state religion.
		(depending on personality)
		less potential boost if we have aspirations of being a religious leader.
		minimum boost for apostolic palace religion */
	CvLeaderHeadInfo const& kPersonality = GC.getInfo(getPersonalityType());
	int iDiplomaticBase = 50 + 5 * range(kPersonality.getSameReligionAttitudeChangeLimit() -
			kPersonality.getDifferentReligionAttitudeChange(), 0, 10);
	/*	note. with the default xml, the highest the above number can get is
		50 + 5*9 (Zara Yaqob). For most leaders its roughly 50 + 5*5. No one gets 100.
		also, most civs with a high base modifier also have iReligionFlavor > 0;
		and so their final modifier will be reduced. */
	int iDiplomaticModifier = 10 * iDiplomaticBase * iLikedReligionCivs /
			std::max(1, iTotalCivs);
	iDiplomaticModifier /= 10 + iReligionFlavor;
	// advc.131: AP matters even if diplo modifier already high
	//if (iDiplomaticModifier < iDiplomaticBase/3) {
	FOR_EACH_ENUM2(VoteSource, eVS)
	{	/*  advc.131: Shouldn't check if we're a member now when deciding whether
			we should be one. */
		if (/*isLoyalMember(i) &&*/
			GC.getGame().isDiploVote(eVS) &&
			GC.getGame().getVoteSourceReligion(eVS) == eReligion)
		{
			iDiplomaticModifier += iDiplomaticBase / 3; // advc.131: += instead of =
		}
	}
	iValue *= 100 + iDiplomaticModifier;
	iValue /= 100;

	return iValue;
}
int expected(CvPlayerAI const& p) {
 if(p.religionCount==0)return 0;
 int citySum=0;
 for(unsigned i=0;i<p.cities.size();++i)citySum+=p.cities[i].grip*p.cities[i].pop;
 int value=citySum*p.religionCount/p.getNumCities();
 if(GC.game.holy!=0 && GC.game.holy->team==1) value=value*(110+5*p.flavor+(10+p.flavor)*40/10)/100;
 int liked=0,hated=0;
 for(unsigned i=0;i<others.size();++i) if(others[i].religion==0) {
  switch(others[i].attitude) {
   case ATTITUDE_FRIENDLY: liked+=2;break;
   case ATTITUDE_PLEASED: liked+=1;break;
   case ATTITUDE_FURIOUS: hated+=2;break;
   case ATTITUDE_ANNOYED: hated+=1;break;
   default:break;
  }
 }
 int diff=GC.leader.same-GC.leader.different;
 int base=50+5*(diff<0?0:(diff>10?10:diff));
 int numerator=hated>0?liked/hated:liked;
 int modifier=10*base*numerator/std::max(1,static_cast<int>(2*others.size()));
 modifier/=10+p.flavor;
 if(GC.game.vote)modifier+=base/3;
 return value*(100+modifier)/100;
}
int main(){
 CvPlayerAI p;p.religionCount=2;
 CvCity a={2,3,1}, b={3,4,1}, foreign={0,0,2};p.cities.push_back(a);p.cities.push_back(b);
 int changes[]={-2,5,12},flavors[]={0,3,10};
 unsigned cases=0,zeroHated=0,positiveHated=0;
 for(int n=0;n<=4;++n) {
  int combinations=1;for(int i=0;i<n;++i)combinations*=6;
  for(int config=0;config<combinations;++config) {
   others.clear();int code=config;bool hasHated=false;
   for(int i=0;i<n;++i) {
    int state=code%6;code/=6;Other o={state==0?1:0,i,static_cast<AttitudeTypes>(state==0?2:state-1)};
    others.push_back(o); if(state==1||state==2)hasHated=true;
   }
   for(int d=0;d<3;++d)for(int fl=0;fl<3;++fl)for(int holy=0;holy<3;++holy)for(int vote=0;vote<2;++vote) {
    GC.leader.same=changes[d];GC.leader.different=0;p.flavor=flavors[fl];
    GC.game.holy=holy==0?0:(holy==1?&p.cities[0]:&foreign);GC.game.vote=vote!=0;
    assert(p.AI_religionValue(0)==expected(p));
    if(hasHated) assert(p.AI_religionValue(0)==p.AI_religionValueOriginal(0));
    else assert(p.AI_religionValue(0)==p.AI_religionValueBaseline(0));
    ++cases;if(hasHated)++positiveHated;else ++zeroHated;
   }
  }
 }
 p.religionCount=0;p.cities.clear();others.clear();assert(p.AI_religionValue(0)==0);
 std::cout<<cases<<" religion configurations passed ("<<zeroHated<<" zero-hated; "<<positiveHated<<" positive-hated), plus absent-religion early return\n";
}
