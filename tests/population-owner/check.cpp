#include <cassert>
typedef int PlayerTypes;
const int NO_PLAYER = -1;
struct Info { int bonus; int getFreePopulation() const {return bonus;} int getExtraPopulation() const{return bonus;} };
struct CvPlayer { int civ,bonus; int getCivilizationType() const{return civ;} int getExtraPopulation() const{return bonus;} };
CvPlayer players[2];
#define GET_PLAYER(x) players[x]
struct Globals { int base; Info infos[3]; Globals():base(1){} int getDefineINT(const char*)const{return base;} const Globals& getGame()const{return *this;} int getStartEra()const{return 2;} const Info& getInfo(int x)const{return infos[x];} } GC;
struct CvCity {static int initialPopulation(PlayerTypes eOwner=NO_PLAYER);};
int CvCity::initialPopulation(PlayerTypes eOwner)
{
	int iPopulation = GC.getDefineINT("INITIAL_CITY_POPULATION") +
			GC.getInfo(GC.getGame().getStartEra()).getFreePopulation();
// XANA: 07-12-2025 City Population Trait
	if (eOwner != NO_PLAYER)
	{
		CvPlayer const& kOwner = GET_PLAYER(eOwner);
		iPopulation += GC.getInfo(kOwner.getCivilizationType()).getExtraPopulation() +
				kOwner.getExtraPopulation();
	}
	return iPopulation;
// XANA: 07-12-2025 City Population Trait
}
int main(){int cases=0; for(int era=0;era<4;++era) for(int civ=0;civ<2;++civ) for(int traits=0;traits<4;++traits){GC.infos[2].bonus=era;GC.infos[0].bonus=civ;GC.infos[1].bonus=1-civ;players[0].civ=0;players[0].bonus=traits;players[1].civ=1;players[1].bonus=3-traits;assert(CvCity::initialPopulation(0)==1+era+civ+traits);assert(CvCity::initialPopulation(1)==1+era+1-civ+3-traits);assert(CvCity::initialPopulation()==1+era);++cases;} assert(cases==32);}
