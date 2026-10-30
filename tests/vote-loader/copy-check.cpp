#include <cassert>
#include <cstring>
#include <string>
#include <vector>
#include <iostream>
const int NUM_CONTACT_TYPES=3,NUM_MEMORY_TYPES=3,NUM_ATTITUDE_TYPES=3,NUM_UNITAI_TYPES=3;
struct Globals {int getNumTraitInfos()const{return 3;}int getNumFlavorTypes()const{return 3;}int getNumImprovementInfos()const{return 3;}int getNumEraInfos()const{return 3;}int getNumVoteInfos()const{return 3;}} GC;
struct CvInfoBase {std::vector<std::string> m_aszExtraXMLforPass3;virtual ~CvInfoBase(){}};
template<typename T>void allocCopy(T*& pDst,T* pSrc,int iSize){if(pSrc!=NULL){pDst=new T[iSize];memcpy(pDst,pSrc,iSize*sizeof(T));}}
struct CvLeaderHeadInfo: CvInfoBase {
int m_iWonderConstructRand;
int* m_pbTraits;
int* m_piFlavorValue;
int* m_piContactRand;
int* m_piContactDelay;
int* m_piMemoryDecayRand;
int* m_piMemoryAttitudePercent;
int* m_piNoWarAttitudeProb;
int* m_piUnitAIWeightModifier;
int* m_piImprovementWeightModifier;
int* m_piDiploPeaceIntroMusicScriptIds;
int* m_piDiploPeaceMusicScriptIds;
int* m_piDiploWarIntroMusicScriptIds;
int* m_piDiploWarMusicScriptIds;
int* m_paeFavoriteVoteDecision;
int* m_piFavoriteVoteDecisionAttitude;
int* m_piHateVoteDecisionAttitude;
std::vector<int> m_aiFirstExtraXMLforPass3,m_aiSecondExtraXMLforPass3;
CvLeaderHeadInfo():m_iWonderConstructRand(42){m_pbTraits=NULL;m_piFlavorValue=NULL;m_piContactRand=NULL;m_piContactDelay=NULL;m_piMemoryDecayRand=NULL;m_piMemoryAttitudePercent=NULL;m_piNoWarAttitudeProb=NULL;m_piUnitAIWeightModifier=NULL;m_piImprovementWeightModifier=NULL;m_piDiploPeaceIntroMusicScriptIds=NULL;m_piDiploPeaceMusicScriptIds=NULL;m_piDiploWarIntroMusicScriptIds=NULL;m_piDiploWarMusicScriptIds=NULL;m_paeFavoriteVoteDecision=NULL;m_piFavoriteVoteDecisionAttitude=NULL;m_piHateVoteDecisionAttitude=NULL;}
CvLeaderHeadInfo(CvLeaderHeadInfo const& kOther);
~CvLeaderHeadInfo(){delete[] m_pbTraits;delete[] m_piFlavorValue;delete[] m_piContactRand;delete[] m_piContactDelay;delete[] m_piMemoryDecayRand;delete[] m_piMemoryAttitudePercent;delete[] m_piNoWarAttitudeProb;delete[] m_piUnitAIWeightModifier;delete[] m_piImprovementWeightModifier;delete[] m_piDiploPeaceIntroMusicScriptIds;delete[] m_piDiploPeaceMusicScriptIds;delete[] m_piDiploWarIntroMusicScriptIds;delete[] m_piDiploWarMusicScriptIds;delete[] m_paeFavoriteVoteDecision;delete[] m_piFavoriteVoteDecisionAttitude;delete[] m_piHateVoteDecisionAttitude;}
};
CvLeaderHeadInfo::CvLeaderHeadInfo(CvLeaderHeadInfo const& kOther)
{
	/*	Better not to memcpy the base class.
		m_iWonderConstructRand is the first data member of CvLeaderHeadInfo. */
	// XANA: 01-24-2026 Leader Specific Player Vote Diplomacy
	// Copy only the scalar/pointer prefix; the staged vectors own their storage.
	memcpy(&m_iWonderConstructRand, &kOther.m_iWonderConstructRand,
			reinterpret_cast<char*>(&m_aiFirstExtraXMLforPass3) -
			reinterpret_cast<char*>(&m_iWonderConstructRand));
	m_aszExtraXMLforPass3 = kOther.m_aszExtraXMLforPass3;
	m_aiFirstExtraXMLforPass3 = kOther.m_aiFirstExtraXMLforPass3;
	m_aiSecondExtraXMLforPass3 = kOther.m_aiSecondExtraXMLforPass3;
	// XANA: 01-24-2026 Leader Specific Player Vote Diplomacy
	allocCopy(m_pbTraits, kOther.m_pbTraits, GC.getNumTraitInfos());
	allocCopy(m_piFlavorValue, kOther.m_piFlavorValue, GC.getNumFlavorTypes());
	allocCopy(m_piContactRand, kOther.m_piContactRand, NUM_CONTACT_TYPES);
	allocCopy(m_piContactDelay, kOther.m_piContactDelay, NUM_CONTACT_TYPES);
	allocCopy(m_piMemoryDecayRand, kOther.m_piMemoryDecayRand, NUM_MEMORY_TYPES);
	allocCopy(m_piMemoryAttitudePercent, kOther.m_piMemoryAttitudePercent, NUM_MEMORY_TYPES);
	allocCopy(m_piNoWarAttitudeProb, kOther.m_piNoWarAttitudeProb, NUM_ATTITUDE_TYPES);
	allocCopy(m_piUnitAIWeightModifier, kOther.m_piUnitAIWeightModifier, NUM_UNITAI_TYPES);
	allocCopy(m_piImprovementWeightModifier, kOther.m_piImprovementWeightModifier, GC.getNumImprovementInfos());
	allocCopy(m_piDiploPeaceIntroMusicScriptIds, kOther.m_piDiploPeaceIntroMusicScriptIds, GC.getNumEraInfos());
	allocCopy(m_piDiploPeaceMusicScriptIds, kOther.m_piDiploPeaceMusicScriptIds, GC.getNumEraInfos());
	allocCopy(m_piDiploWarIntroMusicScriptIds, kOther.m_piDiploWarIntroMusicScriptIds, GC.getNumEraInfos());
	allocCopy(m_piDiploWarMusicScriptIds, kOther.m_piDiploWarMusicScriptIds, GC.getNumEraInfos());
// XANA: 01-24-2026 Leader Specific Player Vote Diplomacy
	allocCopy(m_paeFavoriteVoteDecision, kOther.m_paeFavoriteVoteDecision, GC.getNumVoteInfos());
	allocCopy(m_piFavoriteVoteDecisionAttitude, kOther.m_piFavoriteVoteDecisionAttitude, GC.getNumVoteInfos());
	allocCopy(m_piHateVoteDecisionAttitude, kOther.m_piHateVoteDecisionAttitude, GC.getNumVoteInfos());
// XANA: 01-24-2026 Leader Specific Player Vote Diplomacy
}
int main(){int cases=0;for(int n=0;n<=32;++n){
CvLeaderHeadInfo source;
source.m_pbTraits=new int[3];for(int k=0;k<3;++k)source.m_pbTraits[k]=0*10+k;
source.m_piFlavorValue=new int[3];for(int k=0;k<3;++k)source.m_piFlavorValue[k]=1*10+k;
source.m_piContactRand=new int[3];for(int k=0;k<3;++k)source.m_piContactRand[k]=2*10+k;
source.m_piContactDelay=new int[3];for(int k=0;k<3;++k)source.m_piContactDelay[k]=3*10+k;
source.m_piMemoryDecayRand=new int[3];for(int k=0;k<3;++k)source.m_piMemoryDecayRand[k]=4*10+k;
source.m_piMemoryAttitudePercent=new int[3];for(int k=0;k<3;++k)source.m_piMemoryAttitudePercent[k]=5*10+k;
source.m_piNoWarAttitudeProb=new int[3];for(int k=0;k<3;++k)source.m_piNoWarAttitudeProb[k]=6*10+k;
source.m_piUnitAIWeightModifier=new int[3];for(int k=0;k<3;++k)source.m_piUnitAIWeightModifier[k]=7*10+k;
source.m_piImprovementWeightModifier=new int[3];for(int k=0;k<3;++k)source.m_piImprovementWeightModifier[k]=8*10+k;
source.m_piDiploPeaceIntroMusicScriptIds=new int[3];for(int k=0;k<3;++k)source.m_piDiploPeaceIntroMusicScriptIds[k]=9*10+k;
source.m_piDiploPeaceMusicScriptIds=new int[3];for(int k=0;k<3;++k)source.m_piDiploPeaceMusicScriptIds[k]=10*10+k;
source.m_piDiploWarIntroMusicScriptIds=new int[3];for(int k=0;k<3;++k)source.m_piDiploWarIntroMusicScriptIds[k]=11*10+k;
source.m_piDiploWarMusicScriptIds=new int[3];for(int k=0;k<3;++k)source.m_piDiploWarMusicScriptIds[k]=12*10+k;
source.m_paeFavoriteVoteDecision=new int[3];for(int k=0;k<3;++k)source.m_paeFavoriteVoteDecision[k]=13*10+k;
source.m_piFavoriteVoteDecisionAttitude=new int[3];for(int k=0;k<3;++k)source.m_piFavoriteVoteDecisionAttitude[k]=14*10+k;
source.m_piHateVoteDecisionAttitude=new int[3];for(int k=0;k<3;++k)source.m_piHateVoteDecisionAttitude[k]=15*10+k;
for(int i=0;i<n;++i){source.m_aszExtraXMLforPass3.push_back("PLAYER_VOTE_YES");source.m_aiFirstExtraXMLforPass3.push_back(i+7);source.m_aiSecondExtraXMLforPass3.push_back(-i-2);}
{
CvLeaderHeadInfo copy(source);assert(copy.m_iWonderConstructRand==42);
assert(copy.m_aszExtraXMLforPass3==source.m_aszExtraXMLforPass3);assert(copy.m_aiFirstExtraXMLforPass3==source.m_aiFirstExtraXMLforPass3);assert(copy.m_aiSecondExtraXMLforPass3==source.m_aiSecondExtraXMLforPass3);
assert(copy.m_pbTraits!=source.m_pbTraits);for(int k=0;k<3;++k)assert(copy.m_pbTraits[k]==source.m_pbTraits[k]);copy.m_pbTraits[0]=999;assert(source.m_pbTraits[0]!=999);
assert(copy.m_piFlavorValue!=source.m_piFlavorValue);for(int k=0;k<3;++k)assert(copy.m_piFlavorValue[k]==source.m_piFlavorValue[k]);copy.m_piFlavorValue[0]=999;assert(source.m_piFlavorValue[0]!=999);
assert(copy.m_piContactRand!=source.m_piContactRand);for(int k=0;k<3;++k)assert(copy.m_piContactRand[k]==source.m_piContactRand[k]);copy.m_piContactRand[0]=999;assert(source.m_piContactRand[0]!=999);
assert(copy.m_piContactDelay!=source.m_piContactDelay);for(int k=0;k<3;++k)assert(copy.m_piContactDelay[k]==source.m_piContactDelay[k]);copy.m_piContactDelay[0]=999;assert(source.m_piContactDelay[0]!=999);
assert(copy.m_piMemoryDecayRand!=source.m_piMemoryDecayRand);for(int k=0;k<3;++k)assert(copy.m_piMemoryDecayRand[k]==source.m_piMemoryDecayRand[k]);copy.m_piMemoryDecayRand[0]=999;assert(source.m_piMemoryDecayRand[0]!=999);
assert(copy.m_piMemoryAttitudePercent!=source.m_piMemoryAttitudePercent);for(int k=0;k<3;++k)assert(copy.m_piMemoryAttitudePercent[k]==source.m_piMemoryAttitudePercent[k]);copy.m_piMemoryAttitudePercent[0]=999;assert(source.m_piMemoryAttitudePercent[0]!=999);
assert(copy.m_piNoWarAttitudeProb!=source.m_piNoWarAttitudeProb);for(int k=0;k<3;++k)assert(copy.m_piNoWarAttitudeProb[k]==source.m_piNoWarAttitudeProb[k]);copy.m_piNoWarAttitudeProb[0]=999;assert(source.m_piNoWarAttitudeProb[0]!=999);
assert(copy.m_piUnitAIWeightModifier!=source.m_piUnitAIWeightModifier);for(int k=0;k<3;++k)assert(copy.m_piUnitAIWeightModifier[k]==source.m_piUnitAIWeightModifier[k]);copy.m_piUnitAIWeightModifier[0]=999;assert(source.m_piUnitAIWeightModifier[0]!=999);
assert(copy.m_piImprovementWeightModifier!=source.m_piImprovementWeightModifier);for(int k=0;k<3;++k)assert(copy.m_piImprovementWeightModifier[k]==source.m_piImprovementWeightModifier[k]);copy.m_piImprovementWeightModifier[0]=999;assert(source.m_piImprovementWeightModifier[0]!=999);
assert(copy.m_piDiploPeaceIntroMusicScriptIds!=source.m_piDiploPeaceIntroMusicScriptIds);for(int k=0;k<3;++k)assert(copy.m_piDiploPeaceIntroMusicScriptIds[k]==source.m_piDiploPeaceIntroMusicScriptIds[k]);copy.m_piDiploPeaceIntroMusicScriptIds[0]=999;assert(source.m_piDiploPeaceIntroMusicScriptIds[0]!=999);
assert(copy.m_piDiploPeaceMusicScriptIds!=source.m_piDiploPeaceMusicScriptIds);for(int k=0;k<3;++k)assert(copy.m_piDiploPeaceMusicScriptIds[k]==source.m_piDiploPeaceMusicScriptIds[k]);copy.m_piDiploPeaceMusicScriptIds[0]=999;assert(source.m_piDiploPeaceMusicScriptIds[0]!=999);
assert(copy.m_piDiploWarIntroMusicScriptIds!=source.m_piDiploWarIntroMusicScriptIds);for(int k=0;k<3;++k)assert(copy.m_piDiploWarIntroMusicScriptIds[k]==source.m_piDiploWarIntroMusicScriptIds[k]);copy.m_piDiploWarIntroMusicScriptIds[0]=999;assert(source.m_piDiploWarIntroMusicScriptIds[0]!=999);
assert(copy.m_piDiploWarMusicScriptIds!=source.m_piDiploWarMusicScriptIds);for(int k=0;k<3;++k)assert(copy.m_piDiploWarMusicScriptIds[k]==source.m_piDiploWarMusicScriptIds[k]);copy.m_piDiploWarMusicScriptIds[0]=999;assert(source.m_piDiploWarMusicScriptIds[0]!=999);
assert(copy.m_paeFavoriteVoteDecision!=source.m_paeFavoriteVoteDecision);for(int k=0;k<3;++k)assert(copy.m_paeFavoriteVoteDecision[k]==source.m_paeFavoriteVoteDecision[k]);copy.m_paeFavoriteVoteDecision[0]=999;assert(source.m_paeFavoriteVoteDecision[0]!=999);
assert(copy.m_piFavoriteVoteDecisionAttitude!=source.m_piFavoriteVoteDecisionAttitude);for(int k=0;k<3;++k)assert(copy.m_piFavoriteVoteDecisionAttitude[k]==source.m_piFavoriteVoteDecisionAttitude[k]);copy.m_piFavoriteVoteDecisionAttitude[0]=999;assert(source.m_piFavoriteVoteDecisionAttitude[0]!=999);
assert(copy.m_piHateVoteDecisionAttitude!=source.m_piHateVoteDecisionAttitude);for(int k=0;k<3;++k)assert(copy.m_piHateVoteDecisionAttitude[k]==source.m_piHateVoteDecisionAttitude[k]);copy.m_piHateVoteDecisionAttitude[0]=999;assert(source.m_piHateVoteDecisionAttitude[0]!=999);
if(n>0){copy.m_aszExtraXMLforPass3[0]="PLAYER_VOTE_NO";assert(source.m_aszExtraXMLforPass3[0]=="PLAYER_VOTE_YES");copy.m_aiFirstExtraXMLforPass3[0]=1000;assert(source.m_aiFirstExtraXMLforPass3[0]==7);source.m_aiSecondExtraXMLforPass3[0]=1000;assert(copy.m_aiSecondExtraXMLforPass3[0]==-2);}
CvLeaderHeadInfo again(copy);assert(again.m_aiFirstExtraXMLforPass3==copy.m_aiFirstExtraXMLforPass3);
}
assert(source.m_iWonderConstructRand==42);if(n>0)assert(source.m_aiFirstExtraXMLforPass3[0]==7);++cases;
}std::cout<<cases<<" copy/ownership cases passed\n";
}
