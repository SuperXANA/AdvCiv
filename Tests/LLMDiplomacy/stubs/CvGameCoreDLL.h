#ifndef TEST_GAMECORE_H
#define TEST_GAMECORE_H
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <climits>
#include <string>
#include <vector>
#include <algorithm>
#include <utility>
#include <new>
#include "windows.h"
#include "CvEnums.h"
#define SAFE_DELETE(p) do { delete (p); (p)=NULL; } while(0)
#define FAssert(x) assert(x)
#define FAssertMsg(x,msg) assert(x)
#define FAssertBounds(a,b,x) assert((x)>=(a) && (x)<(b))
extern pthread_t g_main;
extern unsigned long g_workerNews;
extern int g_rngCalls;
inline bool onMain() { return pthread_equal(pthread_self(),g_main)!=0; }
inline void requireMain() { assert(onMain()); }
class CvString: public std::string {
public:
 CvString() {}
 CvString(char const* s):std::string(s) {}
 CvString(std::string const& s):std::string(s) {}
};
class CvRandom { public: int get(int count,char const*) { requireMain(); ++g_rngCalls; assert(count>0); return 0; } };
struct PlayerStub {
 CivilizationTypes civ; LeaderHeadTypes leader; AttitudeTypes attitude; int power;
 PlayerStub():civ(CIV_0),leader(LEADER_0),attitude(ATTITUDE_PLEASED),power(10) {}
 CivilizationTypes getCivilizationType() const { requireMain(); return civ; }
 LeaderHeadTypes getLeaderType() const { requireMain(); return leader; }
 AttitudeTypes AI_getAttitude(PlayerTypes) const { requireMain(); return attitude; }
 int getPower() const { requireMain(); return power; }
};
extern PlayerStub g_players[MAX_PLAYERS];
inline PlayerStub& getPlayer(PlayerTypes p) { requireMain(); assert(p>=0 && p<MAX_PLAYERS); return g_players[p]; }
#define GET_PLAYER(p) getPlayer(p)
struct GlobalStub {
 CvRandom random;
 int getNumCivilizationInfos() const { requireMain(); return 3; }
 int getNumLeaderHeadInfos() const { requireMain(); return 3; }
 int getNumDiplomacyInfos() const { requireMain(); return 2; }
 CvRandom& getASyncRand() { requireMain(); return random; }
};
extern GlobalStub GC;
#endif
