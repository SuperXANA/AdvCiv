#pragma once

#ifndef CIV4_AI_VECTOR_MEMORY_H
#define CIV4_AI_VECTOR_MEMORY_H

#include "CvGameCoreDLL.h"

class CvAIVectorMemory : private boost::noncopyable
{
public:
	CvAIVectorMemory() : m_bInitialized(false) {}
	~CvAIVectorMemory() { uninit(); }
	void init(int iSeed);
	void uninit();
	void reset(int iSeed)
	{
		uninit();
		init(iSeed);
	}
	bool isInitialized() const { return m_bInitialized; }
	
	// Core API
	void recordMemory(PlayerTypes eSubject, MemoryContext eContext, const std::vector<scaled>& rObservations, int iOutcome);
	int predictOutcome(PlayerTypes eSubject, MemoryContext eContext, const std::vector<scaled>& rObservations);

	// Social Mechanics
	void spreadGossip(PlayerTypes eTarget);
	void forgetOldMemories();

	// Save/Load
	void read(FDataStreamBase* pStream);
	void write(FDataStreamBase* pStream);

private:
	bool m_bInitialized;
	int getLSHHash(MemoryContextTypes eContext, const std::vector<scaled>& rObservations) const;

	// Each player has their own index of which memories they "know" about
	// (Maps LSH Hash -> List of global GameMemoryData Vector Indices)
	stdext::hash_map<int, std::vector<int> m_knowledge;
	scaled m_rHyperplanes[NUM_MEMORY_HYPERPLANE_TYPES * NUM_MEMORY_FEATURE_TYPES];
};

#endif
};