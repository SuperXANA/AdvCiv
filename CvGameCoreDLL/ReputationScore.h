#pragma once

#ifndef REPUTATION_SCORE_H
#define REPUTATION_SCORE_H

class ReputationScore
{
public:
	ReputationScore() : m_iMovingAvgSamples(0) {}
	void reset()
	{
		m_iMovingAvgSamples = 0;
		m_aiValues.clear();
	}
	void grow(int iSize);
	int size() const { return (int)m_aiValues.size(); }
	int get(int iTurn) const
	{
		FAssertBounds(0, size(), iTurn);
		return m_aiValues[iTurn];
	}
	void set(int iTurn, int iValue);
	void read(FDataStreamBase* pStream, bool bLegacy = false);
	void write(FDataStreamBase* pStream);

private:
	std::vector<int> m_aiValues; // serialized
	int m_iMovingAvgSamples;
};

#endif
