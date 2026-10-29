#include <cassert>
#include <cstring>
#include <cstddef>
int liveBlocks=0;
#define SAFE_DELETE_ARRAY(p) do {if(p!=NULL){--liveBlocks;delete[] p;p=NULL;}} while(0)
struct CvLeaderHeadInfo {int* m_pbTraits;int* m_piFlavorValue;int* m_piContactRand;int* m_piContactDelay;int* m_piMemoryDecayRand;int* m_piMemoryAttitudePercent;int* m_piNoWarAttitudeProb;int* m_piUnitAIWeightModifier;int* m_piImprovementWeightModifier;int* m_piDiploPeaceIntroMusicScriptIds;int* m_piDiploPeaceMusicScriptIds;int* m_piDiploWarIntroMusicScriptIds;int* m_piDiploWarMusicScriptIds;int* m_piUnitCombatWeights;
CvLeaderHeadInfo():m_pbTraits(NULL),m_piFlavorValue(NULL),m_piContactRand(NULL),m_piContactDelay(NULL),m_piMemoryDecayRand(NULL),m_piMemoryAttitudePercent(NULL),m_piNoWarAttitudeProb(NULL),m_piUnitAIWeightModifier(NULL),m_piImprovementWeightModifier(NULL),m_piDiploPeaceIntroMusicScriptIds(NULL),m_piDiploPeaceMusicScriptIds(NULL),m_piDiploWarIntroMusicScriptIds(NULL),m_piDiploWarMusicScriptIds(NULL),m_piUnitCombatWeights(NULL) {}
~CvLeaderHeadInfo();};
CvLeaderHeadInfo::~CvLeaderHeadInfo()
{
	SAFE_DELETE_ARRAY(m_pbTraits);
	SAFE_DELETE_ARRAY(m_piFlavorValue);
	SAFE_DELETE_ARRAY(m_piContactRand);
	SAFE_DELETE_ARRAY(m_piContactDelay);
	SAFE_DELETE_ARRAY(m_piMemoryDecayRand);
	SAFE_DELETE_ARRAY(m_piMemoryAttitudePercent);
	SAFE_DELETE_ARRAY(m_piNoWarAttitudeProb);
	SAFE_DELETE_ARRAY(m_piUnitAIWeightModifier);
	SAFE_DELETE_ARRAY(m_piImprovementWeightModifier);
	SAFE_DELETE_ARRAY(m_piDiploPeaceIntroMusicScriptIds);
	SAFE_DELETE_ARRAY(m_piDiploPeaceMusicScriptIds);
	SAFE_DELETE_ARRAY(m_piDiploWarIntroMusicScriptIds);
	SAFE_DELETE_ARRAY(m_piDiploWarMusicScriptIds);
	// XANA: 10-29-2026 Favorite combat storage ownership (ChatGPT)
	SAFE_DELETE_ARRAY(m_piUnitCombatWeights);
	// XANA: 10-29-2026 Favorite combat storage ownership (ChatGPT)
}
template<typename T> void allocCopy(T*& pDst,T* pSrc,int iSize){if(pSrc!=NULL){pDst=new T[iSize];++liveBlocks;memcpy(pDst,pSrc,iSize*sizeof(T));}}
void exercise(){for(int k=0;k<500;++k){CvLeaderHeadInfo original;original.m_piUnitCombatWeights=new int[3];++liveBlocks;for(int i=0;i<3;++i)original.m_piUnitCombatWeights[i]=i+k;CvLeaderHeadInfo copy;allocCopy(copy.m_piUnitCombatWeights,original.m_piUnitCombatWeights,3);assert(copy.m_piUnitCombatWeights!=original.m_piUnitCombatWeights);for(int i=0;i<3;++i)assert(copy.m_piUnitCombatWeights[i]==i+k);copy.m_piUnitCombatWeights[0]=-10;assert(original.m_piUnitCombatWeights[0]==k);}CvLeaderHeadInfo empty;}

int main(){exercise();assert(liveBlocks==0);}
