#ifndef XANA_RACE_WEIGHTED_RANDOM_H
#define XANA_RACE_WEIGHTED_RANDOM_H
// XANA: 06-21-2025 Racial Marks
namespace xanaRace
{
// AdvCiv 1.14's synchronized RNG accepts a 16-bit upper bound.
// Preserve one native draw for supported pools; compose 31 bits for larger int pools.
template<class Game>
int drawWeightedIndex(Game& kGame, int iTotalWeight)
{
	if (iTotalWeight <= 0)
		return -1;
	if (iTotalWeight <= 65535)
		return kGame.getSorenRandNum(iTotalWeight, "Unit Race Demographics Roll");
	unsigned int const uiRange = 0x80000000U;
	unsigned int const uiTotal = static_cast<unsigned int>(iTotalWeight);
	unsigned int const uiLimit = uiRange - uiRange % uiTotal;
	unsigned int uiRoll;
	do
	{
		// Sequence the draws explicitly; operand evaluation order is unspecified in C++03.
		unsigned int const uiHigh = kGame.getSorenRandNum(32768, "Race demographics high bits");
		unsigned int const uiLow = kGame.getSorenRandNum(32768, "Race demographics low bits");
		unsigned int const uiBit = kGame.getSorenRandNum(2, "Race demographics final bit");
		uiRoll = uiHigh * 65536U + uiLow * 2U + uiBit;
	} while (uiRoll >= uiLimit);
	return static_cast<int>(uiRoll % uiTotal);
}
}
// XANA: 06-21-2025 Racial Marks
#endif
