"""Exercise actual relation classes and player cache methods under C++03 stubs.

These checks do not replace native DLL or Civ4 XML/gameplay validation.
"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MARK = "// XANA: 03-28-2026 Leader-to-Leader Relationships"

def block(path):
    text = (ROOT / path).read_text()
    start = text.index(MARK)
    end = text.index(MARK, start + len(MARK))
    return text[start:end]

def method(text, signature):
    start = text.index(signature)
    opening = text.index("{", start)
    level = 1
    cursor = opening + 1
    while level:
        level += (text[cursor] == "{") - (text[cursor] == "}")
        cursor += 1
    return text[start:cursor]

player = (ROOT / "CvGameCoreDLL/CvPlayer.cpp").read_text()
init = method(player, "void CvPlayer::initLeaderRelationship()")
setter = method(player, "void CvPlayer::setPersonalityType(")
read = method(player, "void CvPlayer::read(")
assert "initLeaderRelationship();" in read
assert "m_eRelationship = NO_RELATIONSHIP;" in method(player, "void CvPlayer::reset(")
code = r"""
#include <cassert>
#include <climits>
#include <map>
#include <string>
#include <utility>
#include <vector>
#define MIN_INT INT_MIN
#define MAX_INT INT_MAX
#define FAssertBounds(a,b,c) assert((c)>=(a)&&(c)<(b))
#define FErrorMsg(s) ((void)0)
static int rangeAssertions=0;
#define FAssert(x) ((void)((x)?0:++rangeAssertions))
__RANGE__
// Permit runtime XML IDs in the stubs, including IDs outside the small test
// tables. Civ4's dynamic enums intentionally carry runtime values.
enum LeaderHeadTypes { NO_LEADER=-1, L0, L1, L2, STUB_LEADER_MAX=32767 };
enum RelationTypes { NO_RELATION=-1, R0, R1, STUB_RELATION_MAX=32767 };
enum RelationshipTypes { NO_RELATIONSHIP=-1, X0, X1, STUB_RELATIONSHIP_MAX=32767 };
class CvXMLLoadUtility {
public:
    std::map<std::string,int> values;
    std::vector<std::pair<int,RelationTypes> > pairs;
    LeaderHeadTypes leader;
    CvXMLLoadUtility():leader(NO_LEADER) {}
    void GetChildXmlValByName(int* out,const char* name,int def) {
        *out=values.count(name)?values[name]:def;
    }
    void SetInfoIDFromChildXmlVal(LeaderHeadTypes& out,const char*) { out=leader; }
    template<class T> class XMLTagPairIterator {
        CvXMLLoadUtility& xml; size_t index;
    public:
        XMLTagPairIterator(CvXMLLoadUtility& x,const char*):xml(x),index(0) {}
        std::pair<int,T> next() {
            if(index==xml.pairs.size()) return std::make_pair(-1,static_cast<T>(-1));
            return xml.pairs[index++];
        }
    };
};
class CvInfoBase {
public:
    bool read(CvXMLLoadUtility*) { return true; }
};
__CLASSES__
struct Globals {
    std::vector<CvRelationshipInfo> relationships;
    int getNumLeaderHeadInfos() const { return 3; }
    int getNumRelationInfos() const { return 2; }
    int getNumRelationshipInfos() const { return static_cast<int>(relationships.size()); }
    const CvRelationshipInfo& getInfo(RelationshipTypes r) { return relationships[r]; }
} GC;
#define FOR_EACH_ENUM(E) for(RelationshipTypes eLoopRelationship=X0; \
    eLoopRelationship<GC.getNumRelationshipInfos(); \
    eLoopRelationship=static_cast<RelationshipTypes>(static_cast<int>(eLoopRelationship)+1))
__IMPLEMENTATIONS__
class CvPlayer {
public:
    RelationshipTypes m_eRelationship;
    LeaderHeadTypes m_ePersonalityType;
    RelationshipTypes observedByAI;
    CvPlayer():m_eRelationship(NO_RELATIONSHIP),m_ePersonalityType(NO_LEADER),
               observedByAI(NO_RELATIONSHIP) {}
    LeaderHeadTypes getPersonalityType() const { return m_ePersonalityType; }
    CvPlayer& AI() { return *this; }
    void AI_updatePersonality() {
        // Match the real baseline setter's precondition.
        assert(getPersonalityType()!=NO_LEADER);
        observedByAI=m_eRelationship;
    }
    void initLeaderRelationship();
    void setPersonalityType(LeaderHeadTypes eNewValue);
};
__INIT__
__SETTER__
static void expect(const CvRelationInfo& info,int value,int expected) {
    info.updateLeaderRelationshipAttitude(value); assert(value==expected);
}
int main() {
    // Model the original defaults through actual 16-bit storage and baseline
    // range behavior. This is a Release/Debug-assert diagnostic, not an
    // execution of the original complete DLL.
    assert(sizeof(short)==2 && sizeof(int)==4);
    short legacyMaxPositive=static_cast<short>(INT_MAX);
    short legacyMaxNegative=static_cast<short>(INT_MIN);
    assert(legacyMaxPositive==-1 && legacyMaxNegative==0);
    assert(range(5,0,legacyMaxPositive)==-1 && rangeAssertions==1);
    rangeAssertions=0;
    CvXMLLoadUtility xml; CvRelationInfo relation;
    assert(relation.read(&xml));
    expect(relation,INT_MIN,INT_MIN); expect(relation,-5,-5);
    expect(relation,0,0); expect(relation,5,5); expect(relation,INT_MAX,INT_MAX);
    xml.values["iMinimumNegativeFirstImpression"]=-8;
    xml.values["iMaximumNegativeFirstImpression"]=-2;
    xml.values["iMinimumPositiveFirstImpression"]=3;
    xml.values["iMaximumPositiveFirstImpression"]=7;
    assert(relation.read(&xml));
    expect(relation,-20,-8); expect(relation,-1,-2);
    expect(relation,1,3); expect(relation,20,7); expect(relation,0,0);
    xml.values["iMinimumPositiveFirstImpression"]=40000;
    xml.values["iMaximumPositiveFirstImpression"]=50000;
    assert(relation.read(&xml)); expect(relation,2,40000);
    xml.values["iMaximumPositiveFirstImpression"]=39999;
    assert(!relation.read(&xml));
    xml.values.clear();
    xml.values["iMinimumNegativeFirstImpression"]=0;
    xml.values["iMaximumNegativeFirstImpression"]=0;
    xml.values["iMinimumPositiveFirstImpression"]=0;
    xml.values["iMaximumPositiveFirstImpression"]=0;
    assert(relation.read(&xml)); expect(relation,-5,-5); expect(relation,5,5);
    xml.values.clear(); assert(relation.read(&xml)); expect(relation,INT_MAX,INT_MAX);
    assert(rangeAssertions==0);
    CvRelationshipInfo mapping;
    xml.leader=L0; xml.pairs.push_back(std::make_pair(1,R1));
    assert(mapping.read(&xml)); assert(mapping.getRelation(L1)==R1);
    assert(mapping.getRelation(NO_LEADER)==NO_RELATION);
    assert(mapping.getRelation(static_cast<LeaderHeadTypes>(3))==NO_RELATION);
    CvRelationshipInfo copy=mapping;
    xml.pairs.clear(); assert(mapping.read(&xml));
    assert(mapping.getRelation(L1)==NO_RELATION && copy.getRelation(L1)==R1);
    xml.pairs.push_back(std::make_pair(3,R1));
    assert(!mapping.read(&xml)); assert(mapping.getRelation(L1)==NO_RELATION);
    xml.pairs.clear(); xml.pairs.push_back(std::make_pair(1,static_cast<RelationTypes>(2)));
    assert(!mapping.read(&xml));
    xml.pairs.clear();
    GC.relationships.push_back(copy);
    CvRelationshipInfo second; xml.leader=L1; assert(second.read(&xml));
    GC.relationships.push_back(second);
    CvPlayer player; player.setPersonalityType(L0);
    assert(player.m_eRelationship==X0 && player.observedByAI==X0);
    player.setPersonalityType(L1);
    assert(player.m_eRelationship==X1 && player.observedByAI==X1);
    player.setPersonalityType(L2);
    assert(player.m_eRelationship==NO_RELATIONSHIP && player.observedByAI==NO_RELATIONSHIP);
    player.setPersonalityType(L0);
    // An absent personality is handled during reconstruction, not through the
    // public setter, whose existing AI update requires a valid leader.
    player.m_ePersonalityType=NO_LEADER; player.initLeaderRelationship();
    assert(player.m_eRelationship==NO_RELATIONSHIP);
    player.m_ePersonalityType=L0; player.initLeaderRelationship();
    assert(player.m_eRelationship==X0);
    player.m_ePersonalityType=L2; player.initLeaderRelationship();
    assert(player.m_eRelationship==NO_RELATIONSHIP);
}
"""
# Use the actual baseline arithmetic helper bundled for review provenance.
arithmetic = (ROOT / "tests/family-relations/baseline-range.txt").read_text()
code = (code.replace("__RANGE__", arithmetic)
        .replace("__CLASSES__", block("CvGameCoreDLL/CvInfo_Civilization.h"))
        .replace("__IMPLEMENTATIONS__", block("CvGameCoreDLL/CvInfo_Civilization.cpp"))
        .replace("__INIT__", init).replace("__SETTER__", setter))
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "check.cpp"; binary = Path(tmp) / "check"
    source.write_text(code)
    flags = (["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
             if "--sanitize" in sys.argv else [])
    subprocess.run(["g++", "-std=c++03", "-Wall", "-Wextra", "-Werror", "-pedantic"]
                   + flags + [str(source), "-o", str(binary)], check=True)
    env = os.environ.copy()
    if "--sanitize" in sys.argv:
        env["UBSAN_OPTIONS"] = "halt_on_error=1"
    subprocess.run([str(binary)], check=True, env=env)
print("C++03 family bounds, mapping and identity-cache checks passed")
