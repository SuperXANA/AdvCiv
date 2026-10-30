#include <cassert>
#include <climits>
#include <iostream>
typedef int PromotionTypes;
const int NO_PROMOTION=-1;
#define FOR_EACH_ENUM(Name) for(int eLoopPromotion=0;eLoopPromotion<3;++eLoopPromotion)
struct Event { int promo, turns; int getUnitPromotion()const{return promo;} int getPromotionExpireTurns()const{return turns;} };
struct Game {int turn; int getGameTurn()const{return turn;} int getGameSpeedType()const{return 0;}};
struct Info {int speed; int getTrainPercent()const{return speed;}};
struct Globals {Game game;Info info;Game& getGame(){return game;}Info& getInfo(int){return info;}} GC;
struct CvUnit { bool has[3]; int deadline[3]; int removals,writes;
CvUnit():removals(0),writes(0){for(int p=0;p<3;++p){has[p]=false;deadline[p]=0;}}
bool isHasPromotion(int p)const{return has[p];}
int getPromotionExpireTurn(int p)const{return deadline[p];}
void setPromotionExpireTurn(int p,int d){assert(p>=0&&p<3);deadline[p]=d;++writes;}
void setHasPromotion(int p,bool b){assert(p>=0&&p<3);has[p]=b;if(!b)++removals;}
void doExpireTempPromotions();
void apply(const Event& kEvent){	if (kEvent.getUnitPromotion() != NO_PROMOTION)
	{
		setHasPromotion((PromotionTypes)kEvent.getUnitPromotion(), true);
// XANA: 05-17-2025 Timed Promotion Expiry Turns
		if (kEvent.getPromotionExpireTurns() != 0)
		{
			int iExpireTurn = kEvent.getPromotionExpireTurns();
			if (iExpireTurn < 0)
				iExpireTurn = -1; // Match promotion metadata: infinite duration.
			else
			{
				iExpireTurn *= GC.getInfo(GC.getGame().getGameSpeedType()).getTrainPercent();
				iExpireTurn /= 100;
				iExpireTurn += GC.getGame().getGameTurn();
			}
			setPromotionExpireTurn((PromotionTypes)kEvent.getUnitPromotion(), iExpireTurn);
		}
// XANA: 05-17-2025 Timed Promotion Expiry Turns
	}
}
};
void CvUnit::doExpireTempPromotions()
{
	FOR_EACH_ENUM(Promotion)
	{
		if (!isHasPromotion(eLoopPromotion))
			continue;
		
		int iExpireTurn = getPromotionExpireTurn(eLoopPromotion);
		
		if (iExpireTurn <= 0) // No deadline (0) or infinite duration (-1)
			continue;
		
		if (iExpireTurn <= GC.getGame().getGameTurn())
			setHasPromotion(eLoopPromotion, false);
	}
}

int main(){
const int ds[]={-1,0,1,2,50,INT_MAX};
const int ts[]={0,1,2,50,INT_MAX};
int cases=0;
for(int d=0;d<6;++d)for(int t=0;t<5;++t)for(int present=0;present<2;++present){
CvUnit u;u.has[0]=present!=0;u.deadline[0]=ds[d];GC.game.turn=ts[t];u.doExpireTempPromotions();
bool expired=present&&ds[d]>0&&ds[d]<=ts[t];assert(u.has[0]==(present&&!expired));assert(u.removals==(expired?1:0));++cases;}
const int duration[]={INT_MIN,-2,-1,0,1,2,5};
const int speeds[]={50,100,150,200};
for(int p=-1;p<3;++p)for(int d=0;d<7;++d)for(int s=0;s<4;++s){
CvUnit u;GC.game.turn=100;GC.info.speed=speeds[s];Event e={p,duration[d]};u.apply(e);
assert(u.writes==((p>=0&&duration[d]!=0)?1:0));
if(p>=0){assert(u.has[p]);if(duration[d]<0)assert(u.deadline[p]==-1);else if(duration[d]>0)assert(u.deadline[p]==100+duration[d]*speeds[s]/100);else assert(u.deadline[p]==0);}
u.doExpireTempPromotions();if(p>=0){bool expire=duration[d]>0&&duration[d]*speeds[s]/100==0;assert(u.has[p]==!expire);}
++cases;}std::cout<<cases<<" cases passed\n";
}
