#include <cassert>
typedef int PromotionTypes;
const int NO_PROMOTION=-1;
struct Event {int promo,turns;int getUnitPromotion()const{return promo;}int getPromotionExpireTurns()const{return turns;}};
struct Global {int turn,speed; const Global& getGame()const{return *this;}int getGameSpeedType()const{return 0;}const Global& getInfo(int)const{return *this;}int getTrainPercent()const{return speed;}int getGameTurn()const{return turn;}} GC;
struct Unit {int applied,writes,deadline;Unit():applied(0),writes(0),deadline(77){}void setHasPromotion(int p,bool){assert(p>=0);++applied;}void setPromotionExpireTurn(int p,int d){assert(p>=0);++writes;deadline=d;}void apply(const Event& kEvent){
	if (kEvent.getUnitPromotion() != NO_PROMOTION)
	{
		setHasPromotion((PromotionTypes)kEvent.getUnitPromotion(), true);
// XANA: 05-17-2025 Timed Promotion Expiry Turns
		if (kEvent.getPromotionExpireTurns() != 0)
		{
			int iExpireTurn = kEvent.getPromotionExpireTurns();
			iExpireTurn *= GC.getInfo(GC.getGame().getGameSpeedType()).getTrainPercent();
			iExpireTurn /= 100;
			iExpireTurn += GC.getGame().getGameTurn();
			setPromotionExpireTurn((PromotionTypes)kEvent.getUnitPromotion(), iExpireTurn);
		}
// XANA: 05-17-2025 Timed Promotion Expiry Turns
	}

}};
int main(){int n=0;for(int p=-1;p<2;++p)for(int d=0;d<5;++d)for(int sp=50;sp<=200;sp+=50){GC.turn=20;GC.speed=sp;Event e={p,d};Unit u;u.apply(e);assert(u.applied==(p!=-1));assert(u.writes==(p!=-1&&d!=0));assert(u.deadline==((p!=-1&&d!=0)?20+d*sp/100:77));++n;}assert(n==60);}
