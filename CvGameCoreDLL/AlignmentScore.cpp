#include "CvGameCoreDLL.h"
#include "AlignmentScore.h"

void AlignmentScore::grow(int iSize)
{
	FAssert(iSize >= 0);
	while (iSize >= size())
		m_aValues.push_back(AlignmentValue());
}


AlignmentValue AlignmentScore::get(int iTurn) const
{
	int const iSampleSize = std::max(1, std::min(m_iMovingAvgSamples - 1, iTurn - 1));
	return AlignmentValue(
		intdiv::round(getAlignmentTowardsPositive(iTurn), iSampleSize),
		intdiv::round(getAlignmentTowardsNegative(iTurn), iSampleSize)
		);
}


int AlignmentScore::getAlignmentTowardsPositive(int iTurn const
{
	FAssertBounds(0, size(), iTurn);
	if (iTurn >= size())
	{
		return 0;
	}
	int const iLastValidIndex = iTurn - 1;
	int const iSampleSize = std::min(m_iMovingAvgSamples - 1, iLastValidIndex);
	int const iHistoryTurnsConsidered = iTurn - iSampleSize;
	if (iSampleSize <= 0 || iHistoryTurnsConsidered <= 0)
	{
		return 0;
	}
	int iAxisHigh = 0;
    for (int i = iLastValidIndex; i >= iHistoryTurnsConsidered; --i)
	{
		iAxisHigh += m_aValues[i].iHigh;
	}
	return iAxisHigh;
}


int AlignmentScore::getAlignmentTowardsNegative(int iTurn) const
{
	FAssertBounds(0, size(), iTurn);
	if (iTurn >= size())
	{
		return 0;
	}
	int const iLastValidIndex = iTurn - 1;
	int const iSampleSize = std::min(m_iMovingAvgSamples - 1, iLastValidIndex);
	int const iHistoryTurnsConsidered = iTurn - iSampleSize;
	if (iSampleSize <= 0 || iHistoryTurnsConsidered <= 0)
	{
		return 0;
	}
	int iAxisLow = 0;
    for (int i = iLastValidIndex; i >= iHistoryTurnsConsidered; --i)
	{
		iAxisLow += m_aValues[i].iLow;
	}
	return iAxisLow;
}


void AlignmentScore::changeAlignmentTowardsPositive(int iTurn, int iChange)
{
	grow(iTurn);
	m_aValues[iTurn].iHigh = std::max(0, std::min(m_iMaxAlignmentPoints, getAlignmentTowardsPositive(iTurn) + iChange));
}


void AlignmentScore::changeAlignmentTowardsNegative(int iTurn, int iChange)
{
	grow(iTurn);
	m_aValues[iTurn].iLow = std::max(0, std::min(m_iMaxAlignmentPoints, getAlignmentTowardsNegative(iTurn) + iChange));
}


void AlignmentScore::decay()
{
	FAssert(size() >= 0);
	if (m_aValues.empty())
	{
		return;
	}
	int const iSize = size();
	int const iLastValidIndex = iSize - 1;
	int const iGameTurns = iSize - std::min(m_iMovingAvgSamples - 1, iLastValidIndex);
	if (iGameTurns <= 0)
	{
		return;
	}
	std::pair<scaled,scaled> const rrSmoothFactor(per100(m_iHighDecayValue), per100(m_iLowDecayValue));
	for (int iTurn = iLastValidIndex; iTurn >= iGameTurns; --iTurn)
		if (iLastValidIndex - iTurn != 0)
		{
			m_aValues[iTurn].iHigh = std::max(iHighDecayLimit, (m_aValues[iTurn].iHigh * (rrSmoothFactor.first).pow(iLastValidIndex - iTurn)));
			m_aValues[iTurn].iLow = std::max(iLowDecayLimit, (m_aValues[iTurn].iLow * (rrSmoothFactor.second).pow(iLastValidIndex - iTurn)));
		}
		else continue;
}


void AlignmentScore::read(FDataStreamBase* pStream)
{
	FAssert(size() == 0);
	
	m_aValues.clear();
	int iSize;
	pStream->Read(&iSize);
	pStream->Read(&m_iMovingAvgSamples);
	pStream->Read(&m_iHighDecayValue);
	pStream->Read(&m_iHighDecayLimit);
	pStream->Read(&m_iHighDecayInitialLimit);
	pStream->Read(&m_iLowDecayValue);
	pStream->Read(&m_iLowDecayLimit);
	pStream->Read(&m_iLowDecayInitialLimit);
	pStream->Read(&m_iMaxAlignmentPoints);
	if (iSize > 0)
	{
		m_aValues.resize(iSize);
		for (int i = 0; i < iSize; i++)
		{
			AlignmentValue kAlignmentValue();
			kAlignmentValue.read(pStream);
			m_aValues.push_back(kAlignmentValue);
		}
	}
}


void AlignmentScore::write(FDataStreamBase* pStream)
{
	int const iSize = size();
	pStream->Write(iSize);
	pStream->Write(m_iMovingAvgSamples);
	pStream->Write(m_iHighDecayValue);
	pStream->Write(m_iHighDecayLimit);
	pStream->Write(m_iHighDecayInitialLimit);
	pStream->Write(m_iLowDecayValue);
	pStream->Write(m_iLowDecayLimit);
	pStream->Write(m_iLowDecayInitialLimit);
	pStream->Write(m_iMaxAlignmentPoints);
	if (iSize > 0)
	{
		std::vector<AlignmentValue>::iterator it;
		for (it = m_aValues.begin(); it != m_aValues.end(); ++it)
		{
			it.write(pStream);
		}
	}
}