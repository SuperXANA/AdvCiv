"""Compile the actual scoped counter refinement with C++03 game stubs.

This is not a whole-feature DLL or save/load test.
"""
from pathlib import Path
import os,re,subprocess,sys,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
cpp=(ROOT/"CvGameCoreDLL/CvPlayerAI.cpp").read_text()
header=(ROOT/"CvGameCoreDLL/CvPlayerAI.h").read_text()
def method(signature):
    start=cpp.index(signature);i=cpp.index("{",start)+1;n=1
    while n:n+=(cpp[i]=="{")-(cpp[i]=="}");i+=1
    return cpp[start:i]
methods=[]
for axis in ["Favorite","Hate"]:
    for verb,ret in [("get","int"),("change","void"),("set","void")]:
        methods.append(method(ret+" CvPlayerAI::AI_"+verb+axis+"GenderCounter("))
start=header.index("int AI_getFavoriteGenderCounter(")
end=header.index("// XANA:",start)
declarations=header[start:end]
setdecls="\n".join(re.findall(r"void AI_set(?:Favorite|Hate)GenderCounter\([^;]+;",header))
assert declarations.count("AI_getFavoriteGenderCounter(")==1
assert declarations.count("AI_getHateGenderCounter(")==1
assert "int* m_aiFavoriteGenderCounter;" in header
assert "int* m_aiHateGenderCounter;" in header
start=cpp.index("\t\tif (getFavoriteGender() != NO_GENDER)",cpp.index("void CvPlayerAI::AI_doCounter("))
end=cpp.index("// XANA:",start)
turn=cpp[start:end]
code=r"""
#include <algorithm>
#include <cassert>
#include <climits>
#include <cmath>
#define MAX_INT INT_MAX
static int badIndices=0;
#define FAssertMsg(condition,text) ((void)((condition)?0:++badIndices))
static int const MAX_PLAYERS=4;
enum { NO_GENDER=-1 };
enum PlayerTypes { NO_PLAYER=-1,P0,P1,P2,P3,OUTSIDE };
struct DecayResult { double value;int floor() const { return static_cast<int>(std::floor(value)); } };
struct Decay { double value; };
static DecayResult operator*(int n,const Decay& d) { DecayResult r={n*d.value};return r; }
struct Other {
    int gender;
    int getGender() const { return gender; }
    int getTeam() const { return 1; }
};
struct Team {
    int AI_getHasMetCounter(int) const { return 100; }
    int AI_randomCounterChange() const { return 1; }
};
struct Personality {
    int getFavoriteGenderAttitudeDivisor() const { return 5; }
    int getHateGenderAttitudeDivisor() const { return -5; }
};
class CvPlayerAI {
public:
    int favorites[MAX_PLAYERS],hates[MAX_PLAYERS];
    int civicSentinel[MAX_PLAYERS],religionSentinel[MAX_PLAYERS];
    int* m_aiFavoriteGenderCounter;
    int* m_aiHateGenderCounter;
    int favoriteGender,hateGender;
    CvPlayerAI():m_aiFavoriteGenderCounter(favorites),m_aiHateGenderCounter(hates),
                 favoriteGender(1),hateGender(2) {
        for(int i=0;i<MAX_PLAYERS;++i) {
            favorites[i]=hates[i]=0;civicSentinel[i]=70;religionSentinel[i]=90;
        }
    }
    int getFavoriteGender() const { return favoriteGender; }
    int getHateGender() const { return hateGender; }
    __DECLARATIONS__
    __SET_DECLARATIONS__
    void update(Other const& kPlayer) {
        PlayerTypes ePlayer=P1;
        Team kOurTeam;Personality kPersonality;Decay rDecayFactor={0.9};
        __TURN_BLOCK__
    }
};
__METHODS__
int main() {
    CvPlayerAI ai;ai.AI_setFavoriteGenderCounter(P1,10);ai.AI_setHateGenderCounter(P1,20);
    ai.AI_changeFavoriteGenderCounter(P1,3);
    assert(ai.AI_getFavoriteGenderCounter(P1)==13&&ai.AI_getHateGenderCounter(P1)==20);
    ai.AI_changeHateGenderCounter(P1,-2);
    assert(ai.AI_getHateGenderCounter(P1)==18&&ai.AI_getFavoriteGenderCounter(P1)==13);
    ai.AI_setFavoriteGenderCounter(P1,10);ai.AI_setHateGenderCounter(P1,20);
    Other neither={3};ai.update(neither);
    assert(ai.AI_getFavoriteGenderCounter(P1)==9&&ai.AI_getHateGenderCounter(P1)==18);
    Other favored={1};ai.update(favored);
    assert(ai.AI_getFavoriteGenderCounter(P1)==10&&ai.AI_getHateGenderCounter(P1)==16);
    Other hated={2};ai.update(hated);
    assert(ai.AI_getFavoriteGenderCounter(P1)==9&&ai.AI_getHateGenderCounter(P1)==17);
    for(int i=0;i<MAX_PLAYERS;++i)assert(ai.civicSentinel[i]==70&&ai.religionSentinel[i]==90);
    ai.AI_changeFavoriteGenderCounter(P1,INT_MIN);
    assert(ai.AI_getFavoriteGenderCounter(P1)==0);
    ai.AI_changeFavoriteGenderCounter(P1,INT_MAX);
    ai.AI_changeFavoriteGenderCounter(P1,1);
    assert(ai.AI_getFavoriteGenderCounter(P1)==INT_MAX);
    ai.AI_setHateGenderCounter(P1,INT_MAX);
    ai.AI_changeHateGenderCounter(P1,INT_MIN);
    assert(ai.AI_getHateGenderCounter(P1)==0);
    ai.AI_setHateGenderCounter(P1,-3);assert(ai.AI_getHateGenderCounter(P1)==0);
    ai.favorites[P1]=-5;ai.AI_changeFavoriteGenderCounter(P1,1);
    assert(ai.AI_getFavoriteGenderCounter(P1)==1);
    ai.AI_changeFavoriteGenderCounter(NO_PLAYER,1);ai.AI_setHateGenderCounter(OUTSIDE,5);
    assert(ai.AI_getFavoriteGenderCounter(NO_PLAYER)==0);
    assert(ai.AI_getHateGenderCounter(OUTSIDE)==0&&badIndices==4);
    assert(ai.AI_getFavoriteGenderCounter(P0)==0&&ai.AI_getHateGenderCounter(P3)==0);
}
"""
code=(code.replace("__DECLARATIONS__",declarations)
      .replace("__SET_DECLARATIONS__",setdecls)
      .replace("__METHODS__","\n".join(methods)).replace("__TURN_BLOCK__",turn))
with tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/"check.cpp";binary=Path(tmp)/"check";source.write_text(code)
    flags=(["-fsanitize=address,undefined","-fno-omit-frame-pointer"] if "--sanitize" in sys.argv else [])
    subprocess.run(["g++","-std=c++03","-Wall","-Wextra","-Werror","-pedantic"]+
                   flags+[str(source),"-o",str(binary)],check=True)
    env=os.environ.copy()
    if "--sanitize" in sys.argv:env["UBSAN_OPTIONS"]="halt_on_error=1"
    subprocess.run([str(binary)],check=True,env=env)
ns="{urn:schemas-microsoft-com:xml-data}"
schema=ET.parse(ROOT/"XML/Civilizations/CIV4CivilizationsSchema.xml").getroot()
names={x.attrib["name"] for x in schema.findall(ns+"ElementType")}
assert "iHateGenderAttitudeChangeLimit" in names
leaders=ET.parse(ROOT/"XML/Civilizations/CIV4LeaderHeadInfos.xml").getroot()
for node in leaders.findall(".//{*}LeaderHeadInfo"):
    for child in node:
        tag=child.tag.split("}")[-1]
        if tag.startswith(("iFavoriteGender","iHateGender")):
            assert tag in names
            int(child.text)
print("C++03 independent gender-counter/update and XML scalar checks passed")
