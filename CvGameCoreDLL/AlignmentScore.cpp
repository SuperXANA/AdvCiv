#include "CvGameCoreDLL.h"
#include "AlignmentScore.h"

void AlignmentScore::nextTurn()
{
    m_iHead++;
    if (m_iHead >= m_iSampleSize) 
    {
        m_iHead = 0;
    }
    m_buffer[m_iHead].m_iHigh = 0;
    m_buffer[m_iHead].m_iLow = 0;
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
    kAlignmentValue.iHigh = std::max(-m_iMaxDelta,
                std::min(m_iMaxDelta, kAlignmentValue.iHigh + iChange));
                
    if (m_bAlignmentGoodEvilIsIndependent)
		return;
    kAlignmentValue.iLow = std::max(-m_iMaxDelta,
                std::min(m_iMaxDelta, kAlignmentValue.iLow - iChange));
}

void AlignmentScore::changeAlignmentTowardsNegative(int iChange)
{
	if (iChange == 0)
		return;
    AlignmentValue& kAlignmentValue = m_buffer[m_iHead];
    kAlignmentValue.iLow = std::max(-m_iMaxDelta,
               std::min(m_iMaxDelta, kAlignmentValue.iLow + iChange));
    
    if (m_bAlignmentGoodEvilIsIndependent)
    	return;
    kAlignmentValue.iHigh = std::max(-m_iMaxDelta,
               std::min(m_iMaxDelta, kAlignmentValue.iHigh - iChange));
}

void AlignmentScore::changePermanentAlignmentTowardsPositive(int iChange)
{
	if (iChange == 0)
		return;
	m_iPermHigh += iChange;
}

void AlignmentScore::changePermanentAlignmentTowardsNegative(int iChange)
{
	if (iChange == 0)
		return;
	m_iPermLow += iChange;
}

void AlignmentScore::decay()
{
	if (m_iHighDecay > 0)
	{
		scaled const iHighFactor = per100(m_iHighDecay);
	}
	if (m_iLowDecay > 0)
	{
		scaled const iLowFactor = per100(m_iLowDecay);
	}
	if (m_iHighDecay > 0 || m_iLowDecay > 0)
	{
		for (int i = 0; i < m_iCount; ++i)
		{
			AlignmentValue& kAlignmentValue = m_buffer[index(i)];
			if (m_iHighDecay > 0)
			{
				kAlignmentValue.iHigh *= iHighFactor;
			}
			if (m_iLowDecay > 0)
			{
				kAlignmentValue.iLow *= iLowFactor;
			}
		}
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
    return std::pair<int,int>((m_iBaseHigh + m_iPermHigh) + (iSumHigh / m_iCount),
		(m_iBaseLow + m_iPermLow) + (iSumLow / m_iCount));
}

void AlignmentScore::read(FDataStreamBase* pStream)
{
	pStream->Read(&m_iHead);
	pStream->Read(&m_iCount);
	pStream->Read(&m_iBaseHigh);
	pStream->Read(&m_iBaseLow);
	pStream->Read(&m_iPermHigh);
	pStream->Read(&m_iPermLow);
	pStream->Read(&m_iHighDecay);
	pStream->Read(&m_iLowDecay);
	pStream->Read(&m_iMaxDelta);
	pStream->Read(&m_bAlignmentGoodEvilIsIndependent);
	
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
	pStream->Write(m_iBaseHigh);
	pStream->Write(m_iBaseLow);
	pStream->Write(m_iPermHigh);
	pStream->Write(m_iPermLow);
	pStream->Write(m_iHighDecay);
	pStream->Write(m_iLowDecay);
	pStream->Write(m_iMaxDelta);
	pStream->Write(m_bAlignmentGoodEvilIsIndependent);
	
	for(int i = 0; i < m_iSampleSize; ++i)
	{
		m_buffer[i].write(pStream);
    }
}