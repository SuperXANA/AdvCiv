#include <cassert>
typedef int GenderTypes;typedef int CivicTypes;
const int NO_GENDER=-1,NO_CIVIC=-1,NO_RELIGION=-1;
enum Marker{ALLY_GENDER,ENEMY_GENDER,SAME_RELIGION,DIFFERENT_RELIGION,SAME_CIVIC};
struct Player{int fav,hate,religion,civic;int getFavoriteGender()const{return fav;}int getHateGender()const{return hate;}int getStateReligion()const{return religion;}bool isCivic(int c)const{return c==civic;}};
struct AI:Player{int getFavoriteCivic()const{return civic;}int count(Marker eMarker,const Player* itPlayer,int iCities)const{int iMatching=0;
		switch (eMarker)
		{
// XANA: 10-25-2025 Gender Specific Diplomacy
		case ALLY_GENDER:
		{
			GenderTypes eFavGender = getFavoriteGender();
			if (eFavGender != NO_GENDER &&
				eFavGender == itPlayer->getFavoriteGender())
			{
				iMatching += iCities;
			}
			break;
		}
		case ENEMY_GENDER:
		{
			GenderTypes eHateGender = getHateGender();
			if (eHateGender != NO_GENDER &&
				eHateGender == itPlayer->getHateGender())
			{
				iMatching += iCities;
			}
			break;
		}
// XANA: 10-25-2025 Gender Specific Diplomacy
		case SAME_RELIGION:
			if (getStateReligion() != NO_RELIGION &&
				getStateReligion() == itPlayer->getStateReligion())
			{
				iMatching += iCities;
			}
			break;
		case DIFFERENT_RELIGION:
			if (getStateReligion() != NO_RELIGION &&
				itPlayer->getStateReligion() != NO_RELIGION &&
				getStateReligion() != itPlayer->getStateReligion())
			{
				iMatching += iCities;
			}
			break;
		case SAME_CIVIC:
		{
			CivicTypes eFavCivic = getFavoriteCivic();
			if (eFavCivic != NO_CIVIC && isCivic(eFavCivic) &&
				itPlayer->isCivic(eFavCivic))
			{
				iMatching += iCities;
			}
		}
		}
return iMatching;}};
int main(){int n=0;for(int f=-1;f<2;++f)for(int h=-1;h<2;++h)for(int rf=-1;rf<2;++rf)for(int rh=-1;rh<2;++rh)for(int rel=-1;rel<2;++rel)for(int rr=-1;rr<2;++rr){AI a;a.fav=f;a.hate=h;a.religion=rel;a.civic=1;Player p={rf,rh,rr,1};assert(a.count(ALLY_GENDER,&p,3)==((f!=-1&&f==rf)?3:0));assert(a.count(ENEMY_GENDER,&p,3)==((h!=-1&&h==rh)?3:0));assert(a.count(SAME_RELIGION,&p,3)==((rel!=-1&&rel==rr)?3:0));assert(a.count(DIFFERENT_RELIGION,&p,3)==((rel!=-1&&rr!=-1&&rel!=rr)?3:0));assert(a.count(SAME_CIVIC,&p,3)==3);++n;}assert(n==729);}
