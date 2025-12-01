#include "CvGameCoreDLL.h"
#include "ReputationScore.h"

void ReputationScore::grow(int iSize)
{
	FAssert(iSize >= 0);
	while (iSize >= size())
		m_aiValues.push_back(0);
}


int ReputationScore::get(int iTurn) const
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
    int iSum = 0;
    for (int i = iLastValidIndex; i >= iHistoryTurnsConsidered; --i)
		iSum += m_aiValues[i];
    return intdiv::round(iSum, std::max(1, iSampleSize));
}


void ReputationScore::set(int iTurn, int iValue)
{
	grow(iTurn);
	m_aiValues[iTurn] = iValue;
}


void ReputationScore::decay()
{
	FAssert(size() >= 0);
	if (m_aiValues.empty())
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
	scaled const rSmoothFactor = per100(95);
	for (int i = iLastValidIndex; i >= iGameTurns; --i)
		if (iLastValidIndex - i != 0)
			int const iScale = iLastValidIndex - i;
			m_aiValues[i] *= rSmoothFactor.pow(iScale);
}


void ReputationScore::read(FDataStreamBase* pStream, bool bLegacy)
{
	FAssert(size() == 0);
	if (bLegacy)
	{
		size_t iSize;
		pStream->Read(&iSize);
		pStream->Read(&m_iMovingAvgSamples);
		for (size_t i = 0; i < iSize; i++)
		{
			int iTurn;
			int iValue;
			pStream->Read(&iTurn);
			pStream->Read(&iValue);
			set(iTurn, iValue);
		}
		return;
	}
	int iSize;
	pStream->Read(&iSize);
	pStream->Read(&m_iMovingAvgSamples);
	if (iSize > 0)
	{
		m_aiValues.resize(iSize);
		pStream->Read(iSize, &m_aiValues[0]);
	}
}


void ReputationScore::write(FDataStreamBase* pStream)
{
	int const iSize = size();
	pStream->Write(iSize);
	pStream->Write(m_iMovingAvgSamples);
	if (iSize > 0)
		pStream->Write(iSize, &m_aiValues[0]);
}
