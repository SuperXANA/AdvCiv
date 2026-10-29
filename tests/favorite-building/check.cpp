#include <cassert>
#include <utility>
enum UnitCombatTypes {MELEE, ARCHER, COUNT};
struct Personality{int weights[COUNT];mutable int queried;int getFavoriteUnitCombatWeight(UnitCombatTypes e)const{queried=e;return weights[e];}};
struct City{bool trainable[COUNT];bool canTrain(UnitCombatTypes e)const{return trainable[e];}int eval(const Personality& kPersonality,std::pair<UnitCombatTypes,int> perUnitCombatVal,int iWeight)const{int iValue=0;
				int iFavoriteUnitCombatWeight = kPersonality.getFavoriteUnitCombatWeight(perUnitCombatVal.first);
				// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
				if (canTrain(perUnitCombatVal.first))
	// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
					iValue += (perUnitCombatVal.second * (iWeight + (iFavoriteUnitCombatWeight > 0 ? iFavoriteUnitCombatWeight : 0))
	// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
				) / 2;
return iValue;}};
int main(){City c={{true,true}};Personality p={{7,0},-1};for(int k=0;k<COUNT;++k)for(int xp=0;xp<=10;++xp)for(int w=0;w<=12;++w){int bonus=p.weights[k]>0?p.weights[k]:0;assert(c.eval(p,std::make_pair(static_cast<UnitCombatTypes>(k),xp),w)==xp*(w+bonus)/2);assert(p.queried==k);}c.trainable[MELEE]=false;assert(c.eval(p,std::make_pair(MELEE,5),12)==0);}
