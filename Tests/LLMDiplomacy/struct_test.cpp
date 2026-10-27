#include "CvGameCoreDLL.h"
#include "CvStructs.h"
pthread_t g_main;
unsigned long g_workerNews=0;
int g_rngCalls=0;
PlayerStub g_players[MAX_PLAYERS];
GlobalStub GC;
static void check(bool ok,char const* label) { if(!ok) { std::fprintf(stderr,"FAIL %s\n",label); std::exit(1); } std::printf("PASS %s\n",label); }
int main() {
 g_main=pthread_self();
 LLMPromptData prompt(PLAYER_0,COMMENT_0,0,99);
 prompt.createLimits().setCivilizationTypeEnabled(CIV_1);
 LLMResultData result(prompt);
 result.setText(CvString(std::string(500,'x')));
 std::vector<LLMResultData> copies;
 for(int i=0;i<256;++i) copies.push_back(result);
 prompt.createLimits().abActiveCivilizations[1]=0;
 result.setText(CvString("changed"));
 check(copies[255].getData()->getText()==std::string(500,'x') && copies[255].getLimits()->abActiveCivilizations[1]==1,"prompt/result copies survive source mutation and 256-element vector relocation");
 DynamicResponse response(COMMENT_0);
 response.initNewResponseGroup(); response.setDiplomacyText(copies[0]);
 for(int i=0;i<256;++i) response.initNewResponseGroup();
 check(response.getDiplomacyText(0,0)==std::string(500,'x'),"response text survives 256 group reallocations");
 check(response.getCivilizationTypes(0,CIV_1) && !response.getCivilizationTypes(0,CIV_0) && response.getLeaderHeadTypes(0,LEADER_2) && response.getAttitudeTypes(0,ATTITUDE_FRIENDLY) && response.getDiplomacyPowerTypes(0,DIPLOMACYPOWER_WEAKER),"one enabled filter dimension leaves other dimensions unrestricted");
 response.m_aResponseGroups[0].limits.abActiveCivilizations.resize(1);
 check(!response.getCivilizationTypes(0,CIV_2),"short filter vector rejects out-of-range reads");
 for(int i=0;i<3;++i) response.updateDynamicResponseLifetime(0,0);
 check(response.getDiplomacyText(0,0).empty(),"third selected use expires the response");
 response.updateDynamicResponseLifetime(0,0);
 check(response.m_aResponseGroups[0].data[0].iTotalUses==3,"usage count saturates after expiration");
 check(response.getDiplomacyText(-1,0).empty() && response.getDiplomacyText(0,2).empty(),"invalid group and text indices return empty values");
 return 0;
}
