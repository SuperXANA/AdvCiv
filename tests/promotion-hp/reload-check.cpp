#include <cassert>
#include <iostream>
#include <vector>
#define FOR_EACH_ENUM(Name) for(int eLoopPromotion=0;eLoopPromotion<4;++eLoopPromotion)
struct Info {int delta;int getMaxHPValueChange()const{return delta;}};
struct Globals {Info info[4];int getMAX_HIT_POINTS()const{return 100;}const Info& getInfo(int p)const{return info[p];}} GC;
struct CvUnit {
int m_iMaxHPValueModifier;bool held[4];
CvUnit():m_iMaxHPValueModifier(0){for(int p=0;p<4;++p)held[p]=false;}
int getMaxHPValueModifier()const;void changeMaxHPValueModifier(int);
	int maxHitPoints() const																		// Exposed to Python
	{
		return GC.getMAX_HIT_POINTS() + getMaxHPValueModifier(); // XANA: 11-15-2025 Promotion HP Changes
	}
bool isHasPromotion(int p)const{return held[p];}
void set(int ePromotion,bool value){if(held[ePromotion]==value)return;int iChange=value?1:-1;held[ePromotion]=value;
	changeMaxHPValueModifier(GC.getInfo(ePromotion).getMaxHPValueChange() * iChange);
}
void write(std::vector<int>& stream)const{for(int p=0;p<4;++p)stream.push_back(held[p]?1:0);}
void read(const std::vector<int>& stream,int& cursor){for(int p=0;p<4;++p)held[p]=stream[cursor++]!=0;
	// XANA: 11-15-2025 Promotion HP Changes
	// Rebuild the derived modifier: promotion flags are loaded without setHasPromotion.
	m_iMaxHPValueModifier = 0;
	FOR_EACH_ENUM(Promotion)
	{
		if (isHasPromotion(eLoopPromotion))
			changeMaxHPValueModifier(GC.getInfo(eLoopPromotion).getMaxHPValueChange());
	}
	// XANA: 11-15-2025 Promotion HP Changes

}
};
int CvUnit::getMaxHPValueModifier() const
{
	return m_iMaxHPValueModifier;
}

void CvUnit::changeMaxHPValueModifier(int iChange)
{
	if (iChange != 0)
	{
		m_iMaxHPValueModifier += iChange;
	}
}

int main(){int cases=0;for(int rotation=0;rotation<5;++rotation)for(int mask=0;mask<16;++mask){
const int values[]={-10,0,10,20,30};int expected=0;
CvUnit source;
for(int p=0;p<4;++p){GC.info[p].delta=values[(p+rotation)%5];if(mask&(1<<p)){source.set(p,true);expected+=GC.info[p].delta;}}
assert(source.maxHitPoints()==100+expected);
std::vector<int> stream;source.write(stream);stream.push_back(2468);
CvUnit loaded;
for(int repeat=0;repeat<2;++repeat){int cursor=0;loaded.read(stream,cursor);assert(stream[cursor++]==2468);assert(cursor==5);assert(loaded.getMaxHPValueModifier()==expected);assert(loaded.maxHitPoints()==source.maxHitPoints());++cases;}
for(int p=0;p<4;++p){loaded.set(p,false);source.set(p,false);assert(loaded.maxHitPoints()==source.maxHitPoints());}assert(loaded.getMaxHPValueModifier()==0);
}std::cout<<cases<<" reload cases passed\n";}
