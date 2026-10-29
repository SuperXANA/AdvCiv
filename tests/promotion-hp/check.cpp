#include <cassert>
struct CvUnit {private:int m_iMaxHPValueModifier;public:CvUnit():m_iMaxHPValueModifier(0){}int getMaxHPValueModifier() const;void changeMaxHPValueModifier(int);int maxHitPoints()const{return 100+getMaxHPValueModifier();}};
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

struct CvPromotionInfo {int m_iMaxHPValueChange;CvPromotionInfo():m_iMaxHPValueChange(0){}int getMaxHPValueChange()const{return m_iMaxHPValueChange;}};
int main(){CvPromotionInfo info;assert(info.getMaxHPValueChange()==0);for(int d=-99;d<=200;++d){CvUnit u;const CvUnit& c=u;assert(c.getMaxHPValueModifier()==0);u.changeMaxHPValueModifier(d);assert(c.maxHitPoints()==100+d);u.changeMaxHPValueModifier(-d);assert(c.maxHitPoints()==100);u.changeMaxHPValueModifier(0);assert(c.maxHitPoints()==100);}}
