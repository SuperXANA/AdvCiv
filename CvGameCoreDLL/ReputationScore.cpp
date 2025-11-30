#include "CvGameCoreDLL.h"
#include "ReputationScore.h"

void ReputationScore::grow(int iSize)
{
	FAssert(iSize >= 0);
	while (iSize >= size())
		m_aiValues.push_back(0);
}


void ReputationScore::set(int iTurn, int iValue, bool bSmoothOverOldOpinions)
{
	grow(iTurn);
	if (m_iMovingAvgSamples <= 0 || !bSmoothOverOldOpinions)
	{
		m_aiValues[iTurn] = iValue;
		return;
	}
	int iOldSamples = std::min(m_iMovingAvgSamples - 1, iTurn - 1);
	int iSamples = iOldSamples;
	int iSum = 0;
	if (iTurn == 0)
	{
		iSum += iValue;
		iSamples++;
	}
	/* XANA (note): We need to create a new game speed XML value where a percentage integer can be defined as the decay value for reputation score values.
	int const iReputationDecayPercent = 100 - GC.getInfo(GC.getGame().getGameSpeedType()).get(CvGameSpeedInfo::AIReputationDecayPercent);
	*/
	int const iReputationDecayPercent = 100 - 5; /* XANA (note): at below division by 100, this means 5% reputation decay per turn */
	for (int i = iTurn - 1; i >= iTurn - iOldSamples; i--)
		iSum += int((m_aiValues[i] * iReputationDecayPercent) / 100);
	if (iSum != 0)
		m_aiValues[iTurn] = intdiv::round(iSum, std::max(1, iSamples));
	else m_aiValues[iTurn] = 0;
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
			set(iTurn, iValue, false);
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
	int iSize = size();
	pStream->Write(iSize);
	pStream->Write(m_iMovingAvgSamples);
	if (iSize > 0)
		pStream->Write(iSize, &m_aiValues[0]);
}
