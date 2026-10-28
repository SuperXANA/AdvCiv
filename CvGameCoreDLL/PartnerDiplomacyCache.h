#ifndef XANA_PARTNER_DIPLOMACY_CACHE_H
#define XANA_PARTNER_DIPLOMACY_CACHE_H
// XANA: 03-29-2025 Leader_Amd_Civilization-Specific Diplomacy Texts for AdvancedCiv
#include <algorithm>
namespace xanaPartnerDiplomacy
{
// Optional XML lists are represented by NULL. Write an explicit false list to
// the cache rather than asking the external stream implementation to read NULL.
template<class Stream>
void writeFilter(Stream* pStream, bool const* pValues, int iCount)
{
	if (iCount <= 0)
		return;
	if (pValues != NULL)
	{
		pStream->Write(iCount, pValues);
		return;
	}
	struct FalseValues
	{
		explicit FalseValues(int iSize) : p(new bool[iSize])
		{
			std::fill(p, p + iSize, false);
		}
		~FalseValues() { delete[] p; }
		bool* p;
	private:
		FalseValues(FalseValues const&);
		FalseValues& operator=(FalseValues const&);
	} aFalse(iCount);
	pStream->Write(iCount, aFalse.p);
}
}
// XANA: 03-29-2025 Leader_Amd_Civilization-Specific Diplomacy Texts for AdvancedCiv
#endif
