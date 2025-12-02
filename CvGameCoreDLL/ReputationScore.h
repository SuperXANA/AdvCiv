#pragma once

#ifndef REPUTATION_SCORE_H
#define REPUTATION_SCORE_H

class ReputationScore
{
public:
	ReputationScore() : m_iMovingAvgSamples(0) {}
	void reset()
	{
		resetSampleSize();
		m_aiValues.clear();
	}
	void clear() { m_aiValues.clear(); }
	int get(int iTurn) const;
	void set(int iTurn, int iValue);
	void decay();
	void read(FDataStreamBase* pStream, bool bLegacy = false);
	void write(FDataStreamBase* pStream);
	void changeSampleSize(char iChange) { setSampleSize(m_iMovingAvgSamples + iChange); }
	// XANA (note): A getSampleSize method isn't needed because it has no effect outside the class, however the set/changeSampleSize functions can be used to modify how strongly AI players remember reputation opinions.

private:
	// XANA (note): The last 4 turns of reputation score are relevant to us, afterwards the calculated score is smoothed out for a long-term opinion view
	void resetSampleSize() { m_iMovingAvgSamples = 4; }
	void grow(int iSize);
	int size() const { return (int)m_aiValues.size(); }
	void setSampleSize(char iNewValue) { (iNewValue <= 0 || iNewValue > 100) ? resetSampleSize() : m_iMovingAvgSamples = iNewValue; }
	std::vector<int> m_aiValues; // serialized
	char m_iMovingAvgSamples;
};

#endif
