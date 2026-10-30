#include <algorithm>
#include <cassert>
#include <climits>
#include <iostream>
#include <utility>
#include <vector>
const int MAX_INT=INT_MAX,MIN_INT=INT_MIN;
struct AlignmentValue {int iHigh,iLow;AlignmentValue():iHigh(0),iLow(0){}};
class FDataStreamBase;
#define private public

#ifndef ALIGNMENT_SCORE_H
#define ALIGNMENT_SCORE_H

class AlignmentScore
{
public:
    AlignmentScore(int baseHigh = 0, int baseLow = 0,
                   int highDecay = 0, int lowDecay = 0,
                   int maxDelta = MAX_INT,
                   bool independent = false)
    : m_iBaseHigh(baseHigh),
      m_iBaseLow(baseLow),
      m_iHighDecay(highDecay),
      m_iLowDecay(lowDecay),
      m_iMaxDelta(maxDelta),
      m_bAlignmentGoodEvilIsIndependent(independent),
      m_iPermHigh(0),
      m_iPermLow(0),
      m_iHead(0),
      m_iCount(0) {}
    void nextTurn();
    void changeAlignmentTowardsPositive(int iChange);
    void changeAlignmentTowardsNegative(int iChange);
    void changePermanentAlignmentTowardsPositive(int iChange);
    void changePermanentAlignmentTowardsNegative(int iChange);
    void decay();
    std::pair<int,int> get() const;
    void read(FDataStreamBase* pStream);
    void write(FDataStreamBase* pStream);
private:
    static const int m_iSampleSize = 10; // XANA (note): default value for speed, game code can't modify
    int index(int i) const
    {
        int idx = (m_iHead - i);
        if (idx < 0)
        {
            idx += m_iSampleSize;
        }
        return idx;
    }
    AlignmentValue m_buffer[m_iSampleSize];
    int m_iHead;
    int m_iCount;
    int m_iBaseHigh;
    int m_iBaseLow;
    int m_iPermHigh;
    int m_iPermLow;
    int m_iHighDecay;
    int m_iLowDecay;
    int m_iMaxDelta;
    bool m_bAlignmentGoodEvilIsIndependent;
};

#endif

#undef private
namespace
{
int alignmentBoundedChange(int current, int change, bool subtract, int upper)
{
    int value;
    if (!subtract)
    {
        if (change > 0 && current > MAX_INT - change) value = MAX_INT;
        else if (change < 0 && current < MIN_INT - change) value = MIN_INT;
        else value = current + change;
    }
    else
    {
        if (change > 0 && current < MIN_INT + change) value = MIN_INT;
        else if (change < 0 && current > MAX_INT + change) value = MAX_INT;
        else value = current - change;
    }
    return std::min(upper, value);
}
}

void AlignmentScore::changeAlignmentTowardsPositive(int iChange)
{
	if (iChange == 0)
		return;
    AlignmentValue& kAlignmentValue = m_buffer[m_iHead];
    kAlignmentValue.iHigh = alignmentBoundedChange(kAlignmentValue.iHigh, iChange, false, m_iMaxDelta);
                
    if (m_bAlignmentGoodEvilIsIndependent)
		return;
    kAlignmentValue.iLow = alignmentBoundedChange(kAlignmentValue.iLow, iChange, true, m_iMaxDelta);
}

void AlignmentScore::changeAlignmentTowardsNegative(int iChange)
{
	if (iChange == 0)
		return;
    AlignmentValue& kAlignmentValue = m_buffer[m_iHead];
    kAlignmentValue.iLow = alignmentBoundedChange(kAlignmentValue.iLow, iChange, false, m_iMaxDelta);
    
    if (m_bAlignmentGoodEvilIsIndependent)
    	return;
    kAlignmentValue.iHigh = alignmentBoundedChange(kAlignmentValue.iHigh, iChange, true, m_iMaxDelta);
}


struct CvAlignmentAxisInfo {
enum {ALIGNMENTS_DO_NOT_DECAY,MAX_ALIGNMENT_POINTS,ALIGNMENTS_LIGHT_DARK_INDEPENDENT};
int noDecay,limit,independent;
int get(int e)const{return e==ALIGNMENTS_DO_NOT_DECAY?noDecay:e==MAX_ALIGNMENT_POINTS?limit:independent;}
};
struct Harness{
std::vector<AlignmentScore> m_aAlignmentAxisScores;
std::pair<int,int> getAlignmentStability(int)const{return std::make_pair(50,80);}
void initialize(CvAlignmentAxisInfo& kAlignmentAxis){int eLoopAlignmentAxis=0;std::pair<int,int> iiAlignmentValues(10,-10);
		if (kAlignmentAxis.get(CvAlignmentAxisInfo::ALIGNMENTS_DO_NOT_DECAY))
		{
			m_aAlignmentAxisScores.push_back(AlignmentScore(
				iiAlignmentValues.first,
				iiAlignmentValues.second,
				100, // Retain both alignment channels: this axis does not decay.
				100,
				kAlignmentAxis.get(CvAlignmentAxisInfo::MAX_ALIGNMENT_POINTS),
				kAlignmentAxis.get(CvAlignmentAxisInfo::ALIGNMENTS_LIGHT_DARK_INDEPENDENT)));
		}
		else
		{
			std::pair<int,int> iiAlignmentStability = getAlignmentStability(eLoopAlignmentAxis);
			m_aAlignmentAxisScores.push_back(AlignmentScore(
				iiAlignmentValues.first,
				iiAlignmentValues.second,
				iiAlignmentStability.first,
				iiAlignmentStability.second,
				kAlignmentAxis.get(CvAlignmentAxisInfo::MAX_ALIGNMENT_POINTS),
				kAlignmentAxis.get(CvAlignmentAxisInfo::ALIGNMENTS_LIGHT_DARK_INDEPENDENT)));
		}
}
};
int main(){int cases=0;const int limits[]={0,1,5,100,INT_MAX};const int changes[]={0,1,10,100};
for(int noDecay=0;noDecay<2;++noDecay)for(int independent=0;independent<2;++independent)for(int l=0;l<5;++l)for(int d=0;d<4;++d){
CvAlignmentAxisInfo info={noDecay,limits[l],independent};Harness h;h.initialize(info);assert(h.m_aAlignmentAxisScores.size()==1);AlignmentScore& s=h.m_aAlignmentAxisScores[0];
assert(s.m_iBaseHigh==10&&s.m_iBaseLow==-10);assert(s.m_iHighDecay==(noDecay?100:50));assert(s.m_iLowDecay==(noDecay?100:80));assert(s.m_iMaxDelta==limits[l]);assert(s.m_bAlignmentGoodEvilIsIndependent==(independent!=0));
s.changeAlignmentTowardsPositive(changes[d]);assert(s.m_buffer[0].iHigh==std::min(changes[d],limits[l]));assert(s.m_buffer[0].iLow==(independent?0:-changes[d]));
s.m_buffer[0].iHigh=0;s.m_buffer[0].iLow=0;
s.changeAlignmentTowardsNegative(changes[d]);assert(s.m_buffer[0].iLow==std::min(changes[d],limits[l]));assert(s.m_buffer[0].iHigh==(independent?0:-changes[d]));++cases;
}
std::cout<<cases<<" initialization and channel-change cases passed\n";
}
