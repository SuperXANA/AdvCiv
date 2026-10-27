#include "CvGameCoreDLL.h"
#include "CvDynamicDiploManager.h"
pthread_t g_main;
unsigned long g_workerNews=0;
int g_rngCalls=0;
PlayerStub g_players[MAX_PLAYERS];
GlobalStub GC;
void* operator new(std::size_t n) throw(std::bad_alloc) { if(!onMain()) ++g_workerNews; void* p=std::malloc(n ? n : 1); if(!p) throw std::bad_alloc(); return p; }
void operator delete(void* p) throw() { std::free(p); }
void* operator new[](std::size_t n) throw(std::bad_alloc) { return ::operator new(n); }
void operator delete[](void* p) throw() { ::operator delete(p); }
class CvGame {
public:
 static void initCache() { CvDynamicDiploManager::getInstance().init(); }
 static void resetCache() { CvDynamicDiploManager::getInstance().reset(); }
 static void stopCache() { CvDynamicDiploManager::getInstance().uninit(); }
};
static void check(bool ok,char const* label) { if(!ok) { std::fprintf(stderr,"FAIL %s\n",label); std::exit(1); } std::printf("PASS %s\n",label); }
static CvDynamicDiploManager& mgr() { return CvDynamicDiploManager::getInstance(); }
static int registerOne(DynamicResponseFilter const* filter=NULL) {
 int group=mgr().getAvailableResponseGroupID(PLAYER_0,COMMENT_0);
 LLMPromptData prompt(PLAYER_0,COMMENT_0,group,mgr().getSessionID());
 if(filter) prompt.createLimits()=*filter;
 assert(mgr().registerPrompt(prompt));
 return group;
}
static int deliver(char const* text,DynamicResponseFilter const* filter=NULL) {
 int group=registerOne(filter);
 assert(mgr().submitResponse(mgr().getSessionID(),PLAYER_0,COMMENT_0,group,text,(int)std::strlen(text)));
 mgr().processPendingResponses(); return group;
}
struct Work {
 unsigned long session;
 int groups[33];
 int successes;
 bool blockedMainAPIs;
};
static void* fillWorker(void* p) {
 Work& w=*static_cast<Work*>(p); w.successes=0;
 for(int i=0;i<33;++i) if(mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,w.groups[i],"worker completion",17)) ++w.successes;
 // All these calls must return without game API/RNG or STL allocations.
 mgr().processPendingResponses();
 w.blockedMainAPIs=mgr().getNumResponses(PLAYER_0,COMMENT_0)==0 && mgr().getAvailableResponseGroupID(PLAYER_0,COMMENT_0)==-1 && mgr().getDynamicDiplomacyTextForPlayers(PLAYER_0,PLAYER_1,COMMENT_0).empty();
 return NULL;
}
int main() {
 g_main=pthread_self();
 check(mgr().getSessionID()==0,"uninitialized cache has no live session");
 CvGame::initCache();
 unsigned long session=mgr().getSessionID();
 check(session!=0 && mgr().getNumResponses(PLAYER_0,COMMENT_0)==0,"main-thread initialization creates a live empty cache");
 int a=deliver("A"), b=deliver("B");
 bool preserved=true;
 for(int i=0;i<20;++i) preserved=preserved && mgr().getDiplomacyText(PLAYER_0,COMMENT_0,a,0)=="A";
 check(preserved,"20 inspection reads preserve response uses");
 int rngBefore=g_rngCalls;
 bool shownThree=true;
 for(int i=0;i<3;++i) shownThree=shownThree && mgr().getDynamicDiplomacyTextForPlayers(PLAYER_0,PLAYER_1,COMMENT_0)=="A";
 check(shownThree,"selected response remains available for exactly three displays");
 check(mgr().getDiplomacyText(PLAYER_0,COMMENT_0,a,0).empty() && mgr().getDiplomacyText(PLAYER_0,COMMENT_0,b,0)=="B" && g_rngCalls==rngBefore+3,"selected-only accounting leaves other candidates untouched and uses async RNG");
 CvString owning=mgr().getDiplomacyText(PLAYER_0,COMMENT_0,b,0);
 CvGame::resetCache();
 check(owning=="B" && mgr().getSessionID()!=session && !mgr().submitResponse(session,PLAYER_0,COMMENT_0,a,"late",4),"reset rejects stale completions while returned strings remain owned");
 DynamicResponseFilter filters; filters.setCivilizationTypeEnabled(CIV_1);
 deliver("wrong civilization",&filters);
 rngBefore=g_rngCalls;
 check(mgr().getDynamicDiplomacyTextForPlayers(PLAYER_0,PLAYER_1,COMMENT_0).empty() && g_rngCalls==rngBefore,"filter mismatch falls back without consuming a UI RNG draw");
 g_players[0].civ=CIV_1;
 check(mgr().getDynamicDiplomacyTextForPlayers(PLAYER_0,PLAYER_1,COMMENT_0)=="wrong civilization","current main-thread state controls presentation filtering");
 g_players[0].civ=CIV_0;
 CvGame::resetCache();
 Work w; w.session=mgr().getSessionID(); w.blockedMainAPIs=false;
 for(int i=0;i<33;++i) w.groups[i]=registerOne();
 pthread_t thread;
 assert(pthread_create(&thread,NULL,fillWorker,&w)==0); assert(pthread_join(thread,NULL)==0);
 check(w.successes==32,"worker mailbox accepts exactly 32 of 33 queued completions");
 check(w.blockedMainAPIs && g_workerNews==0,"worker cannot run main-thread APIs and performs no operator-new allocations or game API calls");
 mgr().processPendingResponses();
 bool imported=true;
 for(int i=0;i<32;++i) imported=imported && mgr().getDiplomacyText(PLAYER_0,COMMENT_0,w.groups[i],0)=="worker completion";
 check(imported,"main thread imports raw worker bytes into owning response values");
 check(mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,w.groups[32],"retry",5),"queue capacity becomes available after main-thread draining");
 check(!mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,w.groups[32],"duplicate",9),"duplicate queued completion is rejected");
 mgr().processPendingResponses();
 check(!mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,w.groups[32],"duplicate",9),"duplicate delivered completion is rejected");
 int canceled=registerOne(); mgr().cancelPrompt(w.session,PLAYER_0,COMMENT_0,canceled);
 check(!mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,canceled,"late canceled",13),"canceled prompt rejects late completion");
 LLMPromptData canceledPrompt(PLAYER_0,COMMENT_0,canceled,w.session);
 check(!mgr().registerPrompt(canceledPrompt),"retired cancellation ID cannot be re-registered");
 int fresh=registerOne();
 char embedded[3]={'a',0,'b'};
 check(!mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,fresh,embedded,3) && !mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,fresh,"oversize",4097) && !mgr().submitResponse(w.session,PLAYER_0,COMMENT_0,fresh,NULL,2),"invalid response lengths, embedded NUL and null text are rejected");
 CvGame::resetCache();
 int pending=0;
 for(int i=0;i<129;++i) {
  int group=mgr().getAvailableResponseGroupID(PLAYER_0,COMMENT_0);
  if(group<0) break;
  LLMPromptData p(PLAYER_0,COMMENT_0,group,mgr().getSessionID());
  if(mgr().registerPrompt(p)) ++pending;
 }
 check(pending==128 && mgr().getAvailableResponseGroupID(PLAYER_0,COMMENT_0)==-1,"pending prompt limit bounds retained metadata at 128 requests");
 CvGame::resetCache();
 int reserved=0;
 for(int i=0;i<257;++i) { if(mgr().getAvailableResponseGroupID(PLAYER_0,COMMENT_0)<0) break; ++reserved; }
 check(reserved==256,"per-comment group IDs are bounded and never reused during a session");
 CvGame::stopCache();
 check(mgr().getSessionID()==0 && mgr().getDynamicDiplomacyTextForPlayers(PLAYER_0,PLAYER_1,COMMENT_0).empty(),"unload leaves no active presentation session");
 return 0;
}
