#pragma once

#ifndef ALIGNMENT_SCORE_H
#define ALIGNMENT_SCORE_H

class AlignmentScore
{
public:
	AlignmentScore(int highDecayLimit = 0, int lowDecayLimit = 0, int highDecay = 0, int lowDecay = 0, int maxAlignmentPoints = MAX_INT)
	:	m_iHighDecayLimit(highDecayLimit),
		m_iHighDecayInitialLimit(highDecayLimit),
		m_iLowDecayLimit(lowDecayLimit),
		m_iLowDecayInitialLimit(lowDecayLimit),
		m_iHighDecayValue(highDecay),
		m_iLowDecayValue(lowDecay),
		m_iMaxAlignmentPoints(maxAlignmentPoints),
		m_iMovingAvgSamples(0)
	{}
	void reset()
	{
		resetSampleSize();
		m_aValues.clear();
	}
	void clear() { m_aValues.clear(); }
	int get(int iTurn) const;
	void changeAlignmentTowardsPositive(int iTurn, int iChange);
	void changeAlignmentTowardsNegative(int iTurn, int iChange);
	void decay();
	void read(FDataStreamBase* pStream, bool bLegacy = false);
	void write(FDataStreamBase* pStream);
	void changeSampleSize(char iChange) { setSampleSize(m_iMovingAvgSamples + iChange); }
	// XANA (note): A getSampleSize method isn't needed because it has no effect outside the class.
	void changeHighDecayLimit(int iChange) { m_iHighDecayLimit = (std::max(m_iHighDecayInitialLimit, std::min(m_iMaxAlignmentPoints, m_iHighDecayLimit + iChange)); }
	void changeLowDecayLimit(int iChange) { m_iLowDecayLimit = (std::max(m_iLowDecayInitialLimit, std::min(m_iMaxAlignmentPoints, m_iLowDecayLimit + iChange)); }

private:
	// XANA (note): The last 10 turns of alignment score are relevant to us, afterwards the calculated score is smoothed out for a long-term alignment overview
	void resetSampleSize() { m_iMovingAvgSamples = 10; }
	void grow(int iSize);
	int size() const { return (int)m_aiValues.size(); }
	void setSampleSize(char iNewValue) { (iNewValue <= 0 || iNewValue > 100) ? resetSampleSize() : m_iMovingAvgSamples = iNewValue; }
	int getAlignmentTowardsPositive(int iTurn) const;
	int getAlignmentTowardsNegative(int iTurn) const;
	std::vector<AlignmentValue> m_aValues; // serialized
	char m_iMovingAvgSamples;
	int m_iHighDecayLimit;
	int m_iHighDecayInitialLimit;
	int m_iLowDecayLimit;
	int m_iLowDecayInitialLimit;
	int m_iHighDecayValue;
	int m_iLowDecayValue;
	int m_iMaxAlignmentPoints;
};

#endif