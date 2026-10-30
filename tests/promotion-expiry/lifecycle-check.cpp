// Actual promotion timing/event/expiry blocks with reduced surrounding engine interfaces.
#include <cassert>
#include <iostream>
enum PromotionTypes { NO_PROMOTION=-1, P0, P1, P2 };
enum GameSpeedTypes { SPEED };
#define FOR_EACH_ENUM(Name) for(int i=0;i<3;++i) for(PromotionTypes eLoopPromotion=static_cast<PromotionTypes>(i);eLoopPromotion!=NO_PROMOTION;eLoopPromotion=NO_PROMOTION)
struct PromotionInfo { int duration; int getExpireTurns() const { return duration; } };
struct SpeedInfo { int percent; int getTrainPercent() const { return percent; } };
struct Game { int turn; int getGameTurn() const { return turn; } GameSpeedTypes getGameSpeedType() const { return SPEED; } };
struct Globals { Game game; PromotionInfo p[3]; SpeedInfo speed;
 Game& getGame() { return game; } PromotionInfo& getInfo(PromotionTypes e) { return p[e]; } SpeedInfo& getInfo(GameSpeedTypes) { return speed; }
} GC;
struct Event { int p,d; int getUnitPromotion()const {return p;} int getPromotionExpireTurns()const {return d;} };
struct BoolMap { bool v[3]; void set(PromotionTypes p,bool b){v[p]=b;} };
struct CvUnit {
 BoolMap m_abHasPromotion; int deadlines[3];
 CvUnit() { for(int i=0;i<3;++i){m_abHasPromotion.v[i]=false;deadlines[i]=0;} }
 bool isHasPromotion(PromotionTypes p) const { return m_abHasPromotion.v[p]; }
 int getPromotionExpireTurn(PromotionTypes p) const { return deadlines[p]; }
 void setPromotionExpireTurn(PromotionTypes p,int n) { deadlines[p]=n; }
 void setHasPromotion(PromotionTypes ePromotion,bool bNewValue) {
 if(isHasPromotion(ePromotion)==bNewValue) return;
 m_abHasPromotion.set(ePromotion,bNewValue);
 int iChange=(isHasPromotion(ePromotion)?1:-1);
// XANA: 05-17-2025 Timed Promotion Expiry Turns
	if (iChange < 0)
	{
		// Event deadlines also belong to promotions with no metadata duration.
		setPromotionExpireTurn(ePromotion, 0);
	}
	else if (GC.getInfo(ePromotion).getExpireTurns() != 0)
	{
		int iExpireTurn = GC.getInfo(ePromotion).getExpireTurns();
		
		if (iExpireTurn <= -1)
			iExpireTurn = -1; // XNAA (note): Infinite Duration Promotion
			
		if (iExpireTurn >= 0)
		{
			iExpireTurn *= GC.getInfo(GC.getGame().getGameSpeedType()).getTrainPercent();
			iExpireTurn /= 100;
			iExpireTurn += GC.getGame().getGameTurn();
		}
		setPromotionExpireTurn(ePromotion, iExpireTurn);
	}
// XANA: 05-17-2025 Timed Promotion Expiry Turns
 }
 void doExpireTempPromotions();
 void apply(Event const& kEvent) {
	if (kEvent.getUnitPromotion() != NO_PROMOTION)
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

int main() {
 int const durations[]={-2,-1,0,1,5}, speeds[]={50,100,200};
 int cases=0;
 for(int md=0;md<5;++md)for(int ed=0;ed<5;++ed)for(int sp=0;sp<3;++sp)for(int pi=0;pi<3;++pi)for(int loss=0;loss<2;++loss) {
  for(int i=0;i<3;++i)GC.p[i].duration=durations[md];
  GC.speed.percent=speeds[sp];GC.game.turn=100;
  PromotionTypes p=static_cast<PromotionTypes>(pi); CvUnit u; Event e={pi,durations[ed]};
  u.apply(e); assert(u.isHasPromotion(p));
  int d=durations[ed]!=0?durations[ed]:durations[md];
  int expected=d<0?-1:(d==0?0:100+d*speeds[sp]/100);
  assert(u.getPromotionExpireTurn(p)==expected);
  // An event override can time a promotion whose metadata duration is zero.
  if(loss==0 || expected<=0) u.setHasPromotion(p,false);
  else { GC.game.turn=expected; u.doExpireTempPromotions(); }
  assert(!u.isHasPromotion(p)); assert(u.getPromotionExpireTurn(p)==0);
  GC.game.turn=500;u.setHasPromotion(p,true);
  int normal=durations[md]<0?-1:(durations[md]==0?0:500+durations[md]*speeds[sp]/100);
  assert(u.getPromotionExpireTurn(p)==normal);
  u.doExpireTempPromotions();
  assert(u.isHasPromotion(p)==!(normal>0&&normal<=500));
  u.setHasPromotion(p,false);assert(u.getPromotionExpireTurn(p)==0);
  for(int i=0;i<3;++i)if(i!=pi){assert(!u.m_abHasPromotion.v[i]);assert(u.deadlines[i]==0);}
  ++cases;
 }
 // Removing an absent promotion remains an unchanged no-op.
 CvUnit absent;absent.deadlines[P0]=42;absent.setHasPromotion(P0,false);assert(absent.deadlines[P0]==42);
 std::cout<<cases<<" grant/remove/regrant sequences passed\n";
}
