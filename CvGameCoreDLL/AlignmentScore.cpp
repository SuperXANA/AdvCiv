#include "CvGameCoreDLL.h"
#include "AlignmentScore.h"

// XANA: 10-28-2026 Overflow-safe alignment arithmetic (ChatGPT)
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
// XANA: 10-28-2026 Overflow-safe alignment arithmetic (ChatGPT)

void AlignmentScore::nextTurn()
{
    m_iHead++;
    if (m_iHead >= m_iSampleSize) 
    {
        m_iHead = 0;
    }
    m_buffer[m_iHead].iHigh = 0;
    m_buffer[m_iHead].iLow = 0;
    if (m_iCount < m_iSampleSize)
    {
        ++m_iCount;
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

void AlignmentScore::changePermanentAlignmentTowardsPositive(int iChange)
{
	if (iChange == 0)
		return;
	m_iPermHigh = alignmentBoundedChange(m_iPermHigh, iChange, false, MAX_INT);
}

void AlignmentScore::changePermanentAlignmentTowardsNegative(int iChange)
{
	if (iChange == 0)
		return;
	m_iPermLow = alignmentBoundedChange(m_iPermLow, iChange, false, MAX_INT);
}

void AlignmentScore::decay()
{
	scaled const iHighFactor = per100(m_iHighDecay);
	scaled const iLowFactor = per100(m_iLowDecay);
	for (int i = 0; i < m_iCount; ++i)
	{
		AlignmentValue& kAlignmentValue = m_buffer[index(i)];
		kAlignmentValue.iHigh *= iHighFactor;
		kAlignmentValue.iLow *= iLowFactor;
	}
}

std::pair<int,int> AlignmentScore::get() const
{
    if (m_iCount == 0)
    {
        return std::pair<int,int>((m_iBaseHigh + m_iPermHigh),
        	(m_iBaseLow + m_iPermLow));
    }
    int iSumHigh = 0;
    int iSumLow = 0;
    for (int i = 0; i < m_iCount; ++i)
    {
        const AlignmentValue& kAlignmentValue = m_buffer[index(i)];
        iSumHigh += kAlignmentValue.iHigh;
        iSumLow += kAlignmentValue.iLow;
    }
    return std::pair<int,int>(((m_iBaseHigh + m_iPermHigh) + (iSumHigh / m_iCount)),
		((m_iBaseLow + m_iPermLow) + (iSumLow / m_iCount)));
}

void AlignmentScore::read(FDataStreamBase* pStream)
{
	pStream->Read(&m_iHead);
	pStream->Read(&m_iCount);
	pStream->Read(&m_iPermHigh);
	pStream->Read(&m_iPermLow);
	
	for(int i = 0; i < m_iSampleSize; ++i)
    {
		m_buffer[i].read(pStream);
    }
}

void AlignmentScore::write(FDataStreamBase* pStream)
{
	PROFILE_FUNC();

	pStream->Write(m_iHead);
	pStream->Write(m_iCount);
	pStream->Write(m_iPermHigh);
	pStream->Write(m_iPermLow);
	
	for(int i = 0; i < m_iSampleSize; ++i)
	{
		m_buffer[i].write(pStream);
    }
}