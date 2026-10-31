#include "CvAIVectorMemory.h'

void CvAIVectorMemory::init(int iSeed)
{
	if (!isInitialized())
	{
		{
			CvRandom CvRandomHyperplane;
			CvRandomHyperplane.init(iSeed);
			{
				int const iFlatElementsTotal = (NUM_MEMORY_HYPERPLANE_TYPES * NUM_MEMORY_FEATURE_TYPES);
				for (int iIndex = 0; iIndex < iFlatElementsTotal; iIndex++)
				{
					// Randomly generate values between -1.0 and 1.0
					m_rHyperplanes[iIndex] = fixp((CvRandomHyperplane.get(2000, "LSH_INIT") - 1000) / 1000);
				}
			}
		}
		m_bInitialized = true;
	}
}

void CvAIVectorMemory::uninit()
{
	if (isInitialized())
	{
		for (int iHash = 0; iHash < (int)m_knowledge.size(); iHash++)
		{
			m_knowledge[iHash].clear();
		}
		m_knowledge.clear();
		{
			int const iFlatElementsTotal = (NUM_MEMORY_HYPERPLANE_TYPES * NUM_MEMORY_FEATURE_TYPES);
			for (int iIndex = 0; iIndex < iFlatElementsTotal; iIndex++)
			{
				m_rHyperplanes[iIndex] = 0;
			}
		}
		m_bInitialized = false;
	}
}

int CvAIVectorMemory::getLSHHash(AIMemoryContextTypes eContext, const std::vector<scaled>& rObservations) const
{
	int iMemoryKey = 0;
	for (int iHyperplane = 0; iHyperplane < NUM_MEMORY_HYPERPLANE_TYPES; iHyperplane++)
	{
		scaled rDotValue = 0;
		for (int iFeature = 0; iFeature < NUM_MEMORY_FEATURE_TYPES; iFeature++)
		{
			rDotValue += (rObservations[iFeature] * m_rHyperplanes[iHyperplane * NUM_MEMORY_FEATURE_TYPES + iFeature]);
		}
		if (rDotValue >= 0)
		{
			iMemoryKey |= (1 << iHyperplane);
		}
	}
	return ((static_cast<int>(eContext) << 8) | iMemoryKey);
}