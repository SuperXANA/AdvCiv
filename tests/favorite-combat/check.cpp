#include <cassert>
typedef int UnitCombatTypes;
#define FAssertBounds(a,b,c) assert((c)>=(a)&&(c)<(b))
struct Globals{int getNumUnitCombatInfos()const{return 2;}} GC;
struct CvLeaderHeadInfo{int* m_piUnitCombatWeights;int getFavoriteUnitCombatWeight(UnitCombatTypes)const;};
int CvLeaderHeadInfo::getFavoriteUnitCombatWeight(UnitCombatTypes eUnitCombat) const
{
	if (eUnitCombat < 0 || eUnitCombat >= GC.getNumUnitCombatInfos())
		return 0;
	FAssertBounds(0, GC.getNumUnitCombatInfos(), eUnitCombat);
	return m_piUnitCombatWeights ? (m_piUnitCombatWeights[eUnitCombat] / 100) : 0;
}
int value(int iValue,const CvLeaderHeadInfo& kPersonality,int combat){struct Unit{int id;int getUnitCombatType()const{return id;}}u={combat};
	int const iFavoriteUnitCombatWeight = kPersonality.getFavoriteUnitCombatWeight(u.getUnitCombatType());
	if (iFavoriteUnitCombatWeight > 0)
	{
		iValue *= 100 + (10 * iFavoriteUnitCombatWeight);
		iValue /= 100;
	}

return iValue;}
int main(){int weights[2];CvLeaderHeadInfo p={weights};for(int w=-200;w<=500;w+=25){weights[0]=w;weights[1]=0;for(int v=0;v<=1000;v+=10){int bonus=w/100;assert(value(v,p,0)==(bonus>0?v*(100+10*bonus)/100:v));assert(value(v,p,1)==v);assert(value(v,p,-1)==v);assert(value(v,p,2)==v);}}p.m_piUnitCombatWeights=0;assert(value(999,p,0)==999);}
