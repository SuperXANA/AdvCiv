#include <cassert>
#include <climits>
#include <algorithm>
#include <utility>
#define MAX_INT INT_MAX
#define MIN_INT INT_MIN
template<class A,class B>struct product_int_type{typedef long type;};
class FDataStreamBase;
struct AlignmentValue{int iHigh,iLow;AlignmentValue():iHigh(0),iLow(0){}};
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
// XANA: 10-29-2026 Wide alignment aggregation (ChatGPT)
std::pair<int,int> AlignmentScore::get() const
{
    typedef product_int_type<int,int>::type WideInt;
    WideInt sumHigh = 0, sumLow = 0;
    for (int i = 0; i < m_iCount; ++i)
    {
        const AlignmentValue& value = m_buffer[index(i)];
        sumHigh += value.iHigh;
        sumLow += value.iLow;
    }
    WideInt high = WideInt(m_iBaseHigh) + m_iPermHigh;
    WideInt low = WideInt(m_iBaseLow) + m_iPermLow;
    if (m_iCount > 0)
    {
        high += sumHigh / m_iCount;
        low += sumLow / m_iCount;
    }
    high = std::max(WideInt(MIN_INT), std::min(WideInt(MAX_INT), high));
    low = std::max(WideInt(MIN_INT), std::min(WideInt(MAX_INT), low));
    return std::pair<int,int>(static_cast<int>(high), static_cast<int>(low));
}
// XANA: 10-29-2026 Wide alignment aggregation (ChatGPT)

int bound(long v){return int(std::max(long(INT_MIN),std::min(long(INT_MAX),v)));}
int main(){assert(sizeof(long)>=8);int vals[]={INT_MIN,-100,-1,0,1,100,INT_MAX};for(int n=0;n<=10;++n)for(int h=0;h<10;++h)for(int x=0;x<7;++x)for(int y=0;y<7;++y){AlignmentScore a;a.m_iCount=n;a.m_iHead=h;a.m_iBaseHigh=vals[x];a.m_iBaseLow=vals[y];a.m_iPermHigh=vals[y];a.m_iPermLow=vals[x];long sh=0,sl=0;for(int j=0;j<10;++j){a.m_buffer[j].iHigh=vals[(x+j)%7];a.m_buffer[j].iLow=vals[(y+j)%7];}for(int j=0;j<n;++j){int k=(h-j+10)%10;sh+=a.m_buffer[k].iHigh;sl+=a.m_buffer[k].iLow;}std::pair<int,int> r=a.get();assert(r.first==bound(long(vals[x])+vals[y]+(n?sh/n:0)));assert(r.second==bound(long(vals[y])+vals[x]+(n?sl/n:0)));}}
