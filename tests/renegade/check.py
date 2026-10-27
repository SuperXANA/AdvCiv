"""Compile actual willingness/default code with baseline RNG and game stubs."""
from pathlib import Path
import os,subprocess,sys,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def method(s,sig):
    start=s.index(sig);i=s.index("{",start)+1;level=1
    while level:level+=(s[i]=="{")-(s[i]=="}");i+=1
    return s[start:i]
ai=(ROOT/"CvGameCoreDLL/CvPlayerAI.cpp").read_text()
actual=method(ai,"bool CvPlayerAI::AI_isWillingToTalk(")
original=(HERE/"original-willing.txt").read_text().replace(
    "CvPlayerAI::AI_isWillingToTalk(","CvPlayerAI::originalWillingToTalk(")
info=(ROOT/"CvGameCoreDLL/CvInfo_Civilization.cpp").read_text()
start=info.index('GetChildXmlValByName(m_iRenegadeFromTeamDiploProb')
end=info.index("// XANA:",start)
loader=info[start:end]
code=r"""
#include <cassert>
#include <climits>
#include <cstring>
#include <string>
#include <utility>
#define MIN_INT INT_MIN
#define MAX_UNSIGNED_SHORT 65535
#define RANDOM_A 1103515245
#define RANDOM_C 12345
#define RANDOM_SHIFT 16
#define FAssert(x) assert(x)
typedef char TCHAR;
enum PlayerTypes { NO_PLAYER=-1,P0,P1,P2 };
enum TeamTypes { T0,T1,T2 };
enum LeaderHeadTypes { NO_LEADER=-1,L0,L1 };
enum { MEMORY_STOPPED_TRADING_RECENT,TRADE_SURRENDER };
struct TradeData { TradeData(int,bool) {} };
static int range(int n,int low,int high) {
    assert(low<=high);return n<low?low:(n>high?high:n);
}
class CvRandom {
    unsigned int m_uiRandomSeed;
public:
    CvRandom():m_uiRandomSeed(0) {}
    void init(unsigned long s) { m_uiRandomSeed=static_cast<unsigned int>(s); }
    unsigned int getSeed() const { return m_uiRandomSeed; }
    unsigned short getInt(unsigned short,const char*,int,int);
    unsigned short get(int n,const char* log=NULL,int a=INT_MIN,int b=INT_MIN) {
        return getInt(static_cast<unsigned short>(n),log,a,b);
    }
    void printToLog(const char*,unsigned short,int,int) { assert(false); }
};
struct FakeXml {
    bool present; int value;
    FakeXml():present(false),value(0) {}
    void GetChildXmlValByName(int* out,const char* name,int def) {
        assert(std::strcmp(name,"iRenegadeFromTeamDiploProb")==0);
        *out=present?value:def;
    }
};
struct CvLeaderHeadInfo {
    int m_iRenegadeFromTeamDiploProb;
    static FakeXml* m_pXML;
    CvLeaderHeadInfo():m_iRenegadeFromTeamDiploProb(0) {}
    int getRenegadeFromTeamDiploProb() const { return m_iRenegadeFromTeamDiploProb; }
    static void GetChildXmlValByName(int&,const char*,int=INT_MIN);
    void load() { __LOADER__ }
};
FakeXml* CvLeaderHeadInfo::m_pXML=NULL;
__DEFAULT_HELPER__
struct Logger { bool isEnabledRand() const { return false; } };
struct Game {
    int turn; unsigned int initialSeed; CvRandom soren,asyn;
    Game():turn(0),initialSeed(34567) { soren.init(12345);asyn.init(67890); }
    int getGameTurn() const { return turn; }
    std::pair<unsigned int,unsigned int> getInitialRandSeed() const {
        return std::make_pair(0U,initialSeed);
    }
    int getSorenRandNum(int n,const char*) { return soren.get(n); }
};
struct Globals {
    Game game; CvLeaderHeadInfo leaders[2];Logger logger;
    const CvLeaderHeadInfo& getInfo(LeaderHeadTypes l) const { return leaders[l]; }
    Game& getGame() { return game; }
    Logger& getLogger() { return logger; }
} GC;
__BASE_RANDOM__
#define SyncRandNum(n) GC.game.getSorenRandNum(n,"test")
__RANDOM_MACROS__
struct CvTeamAI {
    TeamTypes id;bool human,vassal,war,always,refuse;int warAge;
    CvTeamAI():id(T0),human(false),vassal(false),war(true),always(false),refuse(false),warAge(10) {}
    TeamTypes getID() const { return id; }
    bool isHuman() const { return human; }
    bool isVassal(TeamTypes) const { return vassal; }
    bool isAVassal() const { return vassal; }
    bool isAtWar(TeamTypes) const { return war; }
    bool isAlwaysWar() const { return always; }
    int AI_getAtWarCounter(TeamTypes) const { return warAge; }
    bool AI_refusePeace(TeamTypes) const { return refuse; }
};
typedef CvTeamAI CvTeam;
struct UWAI {
    bool enabled;int answer;
    UWAI():enabled(false),answer(0) {}
    bool isEnabled() const { return enabled; }
    int willTalk(PlayerTypes,int,bool) const { return answer; }
};
struct CvPlayerAI {
    PlayerTypes id; TeamTypes team;LeaderHeadTypes leader;
    bool active,major,human,canTrade;int memory,refuseTurns;UWAI warAI;
    CvPlayerAI():id(P0),team(T0),leader(L0),active(false),major(true),human(false),
                 canTrade(true),memory(0),refuseTurns(3) {}
    LeaderHeadTypes getPersonalityType() const { return leader; }
    PlayerTypes getID() const { return id; }
    TeamTypes getTeam() const { return team; }
    bool isActive() const { return active; }
    bool isMajorCiv() const { return major; }
    bool isHuman() const { return human; }
    bool isAVassal() const;
    int AI_getMemoryCount(PlayerTypes,int) const { return memory; }
    bool canTradeItem(PlayerTypes,const TradeData&) const { return canTrade; }
    const UWAI& getUWAI() const { return warAI; }
    const UWAI& uwai() const { return warAI; }
    int AI_refuseToTalkTurns(PlayerTypes) const { return refuseTurns; }
    bool AI_isWillingToTalk(PlayerTypes,bool=false) const;
    bool originalWillingToTalk(PlayerTypes,bool=false) const;
};
CvPlayerAI players[3]; CvTeamAI teams[3];
static CvTeamAI& getTeam(TeamTypes t) { return teams[t]; }
static CvTeamAI& getTeam(PlayerTypes p) { return teams[players[p].team]; }
#define GET_TEAM(t) ::getTeam(t)
#define GET_PLAYER(p) players[p]
#define TEAMID(p) players[p].team
bool CvPlayerAI::isAVassal() const { return teams[team].vassal; }
struct DLL { PlayerTypes diplomacy;DLL():diplomacy(NO_PLAYER) {}
    PlayerTypes getDiplomacyPlayer() const { return diplomacy; } } dll;
DLL* gDLL=&dll;
__ACTUAL__
__ORIGINAL__
int main() {
    assert(sizeof(unsigned int)==4);
    for(int i=0;i<3;++i) { players[i].id=static_cast<PlayerTypes>(i);
        players[i].team=static_cast<TeamTypes>(i);teams[i].id=static_cast<TeamTypes>(i); }
    FakeXml xml;CvLeaderHeadInfo info;CvLeaderHeadInfo::m_pXML=&xml;
    int legacyMissing=0;
    CvLeaderHeadInfo::GetChildXmlValByName(legacyMissing,"iRenegadeFromTeamDiploProb");
    assert(legacyMissing==INT_MIN);
    info.load();assert(info.getRenegadeFromTeamDiploProb()==0);
    info.m_iRenegadeFromTeamDiploProb=37;info.load();
    assert(info.getRenegadeFromTeamDiploProb()==37); // inherited defaults
    xml.present=true;xml.value=0;info.load();assert(info.getRenegadeFromTeamDiploProb()==0);
    xml.value=-10;info.load();assert(info.getRenegadeFromTeamDiploProb()==0);
    xml.value=500;info.load();assert(info.getRenegadeFromTeamDiploProb()==100);
    teams[T0].human=true; GC.leaders[L0].m_iRenegadeFromTeamDiploProb=40;
    unsigned int before=GC.game.soren.getSeed();bool sawTrue=false,sawFalse=false;
    for(int j=0;j<100;++j) {
        bool v=players[P0].originalWillingToTalk(P1,true);sawTrue|=v;sawFalse|=!v;
    }
    assert(GC.game.soren.getSeed()!=before&&sawTrue&&sawFalse);
    before=GC.game.soren.getSeed();unsigned int asyncBefore=GC.game.asyn.getSeed();
    int successes=0,differentRecipient=0;
    for(int turn=0;turn<1000;++turn) {
        GC.game.turn=turn;bool first=players[P0].AI_isWillingToTalk(P1,true);
        for(int j=0;j<20;++j) {
            assert(players[P0].AI_isWillingToTalk(P1,true)==first);
            assert(players[P0].AI_isWillingToTalk(P1,false)==first);
        }
        successes+=first;
        differentRecipient+=(players[P0].AI_isWillingToTalk(P2,true)!=first);
    }
    assert(successes>300&&successes<500&&differentRecipient>100);
    assert(GC.game.soren.getSeed()==before&&GC.game.asyn.getSeed()==asyncBefore);
    GC.leaders[L0].m_iRenegadeFromTeamDiploProb=0;
    assert(!players[P0].AI_isWillingToTalk(P1));
    GC.leaders[L0].m_iRenegadeFromTeamDiploProb=100;
    assert(players[P0].AI_isWillingToTalk(P1));
    // Existing non-renegade gates still precede the override.
    players[P1].major=false;assert(!players[P0].AI_isWillingToTalk(P1));players[P1].major=true;
    teams[T1].vassal=true;assert(players[P0].AI_isWillingToTalk(P1));teams[T1].vassal=false;
    teams[T1].war=false;players[P0].memory=1;
    assert(!players[P0].AI_isWillingToTalk(P1));players[P0].memory=0;
    assert(players[P0].AI_isWillingToTalk(P1));teams[T1].war=true;
    players[P0].active=true; players[P1].active=true;teams[T1].always=true;
    assert(!players[P0].AI_isWillingToTalk(P1));teams[T1].always=false;
    dll.diplomacy=P0;assert(players[P0].AI_isWillingToTalk(P1));dll.diplomacy=NO_PLAYER;
    players[P1].active=false;teams[T0].human=false;players[P0].warAI.enabled=true;
    players[P0].warAI.answer=-1;assert(!players[P0].AI_isWillingToTalk(P1));
    players[P0].warAI.answer=1;assert(players[P0].AI_isWillingToTalk(P1));
    assert(GC.game.soren.getSeed()==before&&GC.game.asyn.getSeed()==asyncBefore);
}
"""
for key,value in {
    "__LOADER__":loader,"__DEFAULT_HELPER__":(HERE/"baseline-xml-default.txt").read_text(),
    "__BASE_RANDOM__":(HERE/"baseline-random.txt").read_text(),
    "__RANDOM_MACROS__":(HERE/"baseline-random-macros.txt").read_text(),
    "__ACTUAL__":actual,"__ORIGINAL__":original}.items():code=code.replace(key,value)
with tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/"check.cpp";binary=Path(tmp)/"check";source.write_text(code)
    flags=(["-fsanitize=address,undefined","-fno-omit-frame-pointer"]
           if "--sanitize" in sys.argv else [])
    subprocess.run(["g++","-std=c++03","-Wall","-Wextra","-Werror","-pedantic"]+
                   flags+[str(source),"-o",str(binary)],check=True)
    env=os.environ.copy()
    if "--sanitize" in sys.argv:env["UBSAN_OPTIONS"]="halt_on_error=1"
    subprocess.run([str(binary)],check=True,env=env)
ns="{urn:schemas-microsoft-com:xml-data}"
schema=ET.parse(ROOT/"Assets/XML/Civilizations/CIV4CivilizationsSchema.xml").getroot()
leader=next(x for x in schema.findall(ns+"ElementType") if x.attrib["name"]=="LeaderHeadInfo")
order={x.attrib["type"]:i for i,x in enumerate(leader.findall(ns+"element"))}
entry=next(x for x in leader.findall(ns+"element") if x.attrib["type"]=="iRenegadeFromTeamDiploProb")
assert entry.attrib["minOccurs"]=="0"
assert order["iDemandRebukedWarProb"]<order["iRenegadeFromTeamDiploProb"]<order["iRazeCityProb"]
nodes=ET.parse(ROOT/"Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml").getroot().findall(".//{*}LeaderHeadInfo")
assert len(nodes)==54
for node in nodes:
    actualOrder=[order[x.tag.split("}")[-1]] for x in node]
    assert actualOrder==sorted(actualOrder)
profile=ET.parse(HERE/"source-values.xml").getroot()
assert len(profile)==45
assert all(0<=int(x.attrib["probability"])<=100 for x in profile)
print("C++03 stable-query/RNG/default checks and XML ordering checks passed")
