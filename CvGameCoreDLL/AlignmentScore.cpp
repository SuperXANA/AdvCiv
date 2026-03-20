#include "CvGameCoreDLL.h"
#include "AlignmentScore.h"

void AlignmentScore::nextTurn()
{
    m_iHead = (m_iHead + 1) % m_iSampleSize;
    m_buffer[m_iHead] = AlignmentValue(); // reset slot
    if (m_iCount < m_iSampleSize)
        ++m_iCount;
}

void AlignmentScore::changeAlignmentTowardsPositive(int iChange)
{
	if (iChange == 0)
		return;
    AlignmentValue& kAlignmentValue = m_buffer[m_iHead];
    kAlignmentValue.iHigh = std::max(-m_iMaxDelta,
                std::min(m_iMaxDelta, kAlignmentValue.iHigh + iChange));
}

void AlignmentScore::changeAlignmentTowardsNegative(int iChange)
{
	if (iChange == 0)
		return;
    AlignmentValue& kAlignmentValue = m_buffer[m_iHead];
    kAlignmentValue.iLow = std::max(-m_iMaxDelta,
               std::min(m_iMaxDelta, kAlignmentValue.iLow + iChange));
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
	if (!m_bDecayAlignment)
	{
		return;
	}
    scaled const iHighFactor = per100(m_iHighDecay);
    scaled const iLowFactor = per100(m_iLowDecay);
    for (int i = 0; i < m_iCount; ++i)
    {
        AlignmentValue& kAlignmentValue = m_buffer[index(i)];
        kAlignmentValue.iHigh = kAlignmentValue.iHigh * iHighFactor;
        kAlignmentValue.iLow = kAlignmentValue.iLow  * iLowFactor;
    }
}

AlignmentValue AlignmentScore::get() const
{
    if (m_iCount == 0)
    {
        return AlignmentValue((m_iBaseHigh + m_iPermHigh), (m_iBaseLow + m_iPermLow));
    }
    int iSumHigh = 0;
    int iSumLow = 0;
    for (int i = 0; i < m_iCount; ++i)
    {
        const AlignmentValue& kAlignmentValue = m_buffer[index(i)];
        iSumHigh += kAlignmentValue.iHigh;
        iSumLow += kAlignmentValue.iLow;
    }
    int const iAvgHigh = iSumHigh / m_iCount;
    int const iAvgLow = iSumLow / m_iCount;
    return AlignmentValue((m_iBaseHigh + m_iPermHigh) + iAvgHigh, (m_iBaseLow + m_iPermLow) + iAvgLow);
}

void AlignmentScore::read(FDataStreamBase* pStream)
{
	reset();

	pStream->Read(&m_iHead);
	pStream->Read(&m_iCount);
	pStream->Read(&m_iBaseHigh);
	pStream->Read(&m_iBaseLow);
	pStream->Read(&m_iPermHigh);
	pStream->Read(&m_iPermLow);
	pStream->Read(&m_iHighDecay);
	pStream->Read(&m_iLowDecay);
	pStream->Read(&m_iMaxDelta);
	{
		m_buffer.clear();
		uint iSize;
		pStream->Read(&iSize);
		m_buffer.reserve(iSize);
		for (uint i = 0; i < iSize; i++)
		{
			AlignmentValue kAlignmentValue;
			kAlignmentValue.read(pStream);
			m_buffer.push_back(kAlignmentValue);
		}
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
	{
		uint iSize = m_buffer.size();
		pStream->Write(iSize);
		std::vector<AlignmentValue>::iterator it;
		for (it = m_buffer.begin(); it != m_buffer.end(); ++it)
		{
			it->write(pStream);
		}
	}
}