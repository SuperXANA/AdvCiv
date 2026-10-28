#include "CvGameCoreDLL.h"
#include "ReputationScore.h"
#include <cmath>

void ReputationScore::grow(int iSize)
{
	FAssert(iSize >= 0);
	while (iSize >= size())
	{
		m_aiValues.push_back(0);
	}
}


// XANA: 11-15-2025 Reputation System for Advanced Civ
// Average the preceding completed turns; the queried turn is excluded.
int ReputationScore::get(int iTurn) const
{
	if (iTurn <= 0 || iTurn > size())
		return 0;
	int const iSamples = std::min(static_cast<int>(m_iMovingAvgSamples), iTurn);
	if (iSamples <= 0)
		return 0;
	// At most 100 int samples: their sum is exact in the target's double.
	double fSum = 0;
	for (int i = iTurn - iSamples; i < iTurn; ++i)
		fSum += m_aiValues[i];
	double const fMean = fSum / iSamples;
	// Round half away from zero, with the result inside the int sample range.
	return static_cast<int>(fMean < 0 ? std::ceil(fMean - 0.5) : std::floor(fMean + 0.5));
}
// XANA: 11-15-2025 Reputation System for Advanced Civ


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
	for (int iTurn = iLastValidIndex; iTurn >= iGameTurns; --iTurn)
	{
		if (iLastValidIndex - iTurn != 0)
		{
			m_aiValues[iTurn] *= rSmoothFactor.pow(iLastValidIndex - iTurn);
		}
	}
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
	{
		pStream->Write(iSize, &m_aiValues[0]);
	}
}
