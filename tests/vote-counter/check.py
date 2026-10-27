#!/usr/bin/env python3
"""Compile the three production vote-history methods in a C++03 fixture.
This is counter logic validation, not a full DLL or gameplay test.
"""
import os
import pathlib
import re
import subprocess
import tempfile
root = pathlib.Path(__file__).resolve().parents[2]
cpp = (root / "CvGameCoreDLL/CvPlayerAI.cpp").read_text()
header = (root / "CvGameCoreDLL/CvPlayerAI.h").read_text()
names = ["AI_updateVoteCount", "AI_getPreferredVoteChoice", "AI_getMostVotedCivPlayer"]
def method(name):
    match = re.search(r"(?:void|PlayerVoteTypes|CivPlayerTypes) CvPlayerAI::" + name + r"\(", cpp)
    assert match
    end = cpp.index("\n}\n", match.start()) + 2
    return cpp[match.start():end]
declarations = []
for name in names:
    declarations.append(next(line.split("//")[0].strip() for line in header.splitlines()
                             if re.search(r"\b" + name + r"\(", line)
                             and line.split("//")[0].strip().endswith(";")))
fixture = r'''
#include <cassert>
#include <algorithm>
// Exact PlayerVoteTypes values from pinned AdvCiv 1.14 CvEnums.h.
enum PlayerVoteTypes {
    NO_PLAYER_VOTE_CHECKED=-6, FIRST_PLAYER_VOTE=NO_PLAYER_VOTE_CHECKED,
    PLAYER_VOTE_NEVER=-5, PLAYER_VOTE_ABSTAIN=-4, PLAYER_VOTE_NO=-3,
    PLAYER_VOTE_YES=-2, NO_PLAYER_VOTE=-1
};
typedef int VoteTypes;
typedef int PlayerTypes;
typedef int CivTeamTypes;
typedef int CivPlayerTypes;
enum { NO_PLAYER=-1, NO_CIV_TEAM=-1, NO_CIV_PLAYER=-1,
       MAX_CIV_TEAMS=18, MAX_CIV_PLAYERS=18 };
int range(int n,int lo,int hi){return std::max(lo,std::min(n,hi));}
#define FOR_EACH_ENUM(Name) for(int eLoop##Name=0;eLoop##Name<18;++eLoop##Name)
struct VoteInfo { bool city; bool isAssignCity()const{return city;} };
struct Game { bool isTeamVote(VoteTypes vote)const{return vote==1;} };
struct Globals {
    VoteInfo infos[3]; Game game;
    Globals(){infos[0].city=infos[1].city=false;infos[2].city=true;}
    int getNumVoteInfos()const{return 3;}
    VoteInfo const& getInfo(VoteTypes vote)const{return infos[vote];}
    Game const& getGame()const{return game;}
} GC;
struct CvPlayerAI {
    int vote[3],teams[18],owners[18];
    int* m_aiVoteAlignment;
    int* m_aiElectionTeamPreference;
    int* m_aiCityAssignmentPlayerPreference;
    CvPlayerAI():m_aiVoteAlignment(vote),m_aiElectionTeamPreference(teams),
        m_aiCityAssignmentPlayerPreference(owners){
        std::fill(vote,vote+3,0);std::fill(teams,teams+18,0);std::fill(owners,owners+18,0);
    }
    @DECLARATIONS@
};
@METHODS@
int main(){
    CvPlayerAI voter;
    voter.AI_updateVoteCount(0,PLAYER_VOTE_YES);assert(voter.vote[0]==1);
    voter.AI_updateVoteCount(0,PLAYER_VOTE_NO);assert(voter.vote[0]==0);
    voter.vote[0]=4;
    voter.AI_updateVoteCount(0,PLAYER_VOTE_ABSTAIN);assert(voter.vote[0]==3);
    voter.AI_updateVoteCount(0,PLAYER_VOTE_NEVER);assert(voter.vote[0]==2);
    voter.vote[0]=-4;
    voter.AI_updateVoteCount(0,PLAYER_VOTE_ABSTAIN);assert(voter.vote[0]==-3);
    voter.AI_updateVoteCount(0,PLAYER_VOTE_NEVER);assert(voter.vote[0]==-2);
    voter.vote[0]=0;
    voter.AI_updateVoteCount(0,PLAYER_VOTE_NEVER);assert(voter.vote[0]==0);
    voter.vote[1]=10;
    voter.AI_updateVoteCount(1,static_cast<PlayerVoteTypes>(1));
    assert(voter.vote[1]==11 && voter.teams[1]==1);
    voter.AI_updateVoteCount(1,PLAYER_VOTE_ABSTAIN);assert(voter.vote[1]==10 && voter.teams[1]==1);
    voter.AI_updateVoteCount(1,PLAYER_VOTE_NEVER);assert(voter.vote[1]==9 && voter.teams[1]==1);
    voter.AI_updateVoteCount(1,static_cast<PlayerVoteTypes>(0));assert(voter.teams[0]==1);
    voter.AI_updateVoteCount(1,static_cast<PlayerVoteTypes>(17));assert(voter.teams[17]==1);
    int before=voter.vote[1];
    voter.AI_updateVoteCount(1,static_cast<PlayerVoteTypes>(18));
    voter.AI_updateVoteCount(1,PLAYER_VOTE_YES);assert(voter.vote[1]==before);
    voter.vote[2]=0;voter.owners[2]=5;
    voter.AI_updateVoteCount(2,PLAYER_VOTE_ABSTAIN,2);assert(voter.vote[2]==0 && voter.owners[2]==4);
    voter.AI_updateVoteCount(2,PLAYER_VOTE_NEVER,2);assert(voter.owners[2]==3);
    voter.owners[2]=-5;
    voter.AI_updateVoteCount(2,PLAYER_VOTE_NEVER,2);assert(voter.owners[2]==-4);
    voter.AI_updateVoteCount(-2,PLAYER_VOTE_YES);
    voter.AI_updateVoteCount(-1,PLAYER_VOTE_YES);
    voter.AI_updateVoteCount(3,PLAYER_VOTE_YES);
    voter.AI_updateVoteCount(2,PLAYER_VOTE_YES,-2);
    voter.AI_updateVoteCount(2,PLAYER_VOTE_YES,18);assert(voter.owners[2]==-4);
    voter.vote[0]=100;voter.AI_updateVoteCount(0,PLAYER_VOTE_YES);assert(voter.vote[0]==100);
    voter.vote[0]=-100;voter.AI_updateVoteCount(0,PLAYER_VOTE_NO);assert(voter.vote[0]==-100);
    voter.vote[1]=voter.teams[1]=100;
    voter.AI_updateVoteCount(1,static_cast<PlayerVoteTypes>(1));
    assert(voter.vote[1]==100 && voter.teams[1]==100);
    assert(voter.AI_getPreferredVoteChoice(1)==static_cast<PlayerVoteTypes>(1));
    voter.owners[0]=7;voter.owners[1]=7;assert(voter.AI_getMostVotedCivPlayer()==0);
    assert(voter.AI_getPreferredVoteChoice(-1)==NO_PLAYER_VOTE);
    assert(voter.AI_getPreferredVoteChoice(3)==NO_PLAYER_VOTE);
    voter.m_aiVoteAlignment=NULL;voter.m_aiElectionTeamPreference=NULL;
    voter.m_aiCityAssignmentPlayerPreference=NULL;
    voter.AI_updateVoteCount(0,PLAYER_VOTE_YES);
    assert(voter.AI_getPreferredVoteChoice(0)==NO_PLAYER_VOTE);
    assert(voter.AI_getMostVotedCivPlayer()==NO_CIV_PLAYER);
}
'''.replace("@DECLARATIONS@", "\n".join(declarations)).replace(
    "@METHODS@", "\n\n".join(method(name) for name in names))
with tempfile.TemporaryDirectory() as temp:
    source = pathlib.Path(temp) / "vote.cpp"
    binary = pathlib.Path(temp) / "vote"
    source.write_text(fixture)
    command = ["g++", "-std=c++03", "-pedantic-errors", "-Wall", "-Wextra",
               str(source), "-o", str(binary)]
    if os.environ.get("VOTE_TEST_SANITIZE") == "1":
        command[1:1] = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    subprocess.run(command, check=True)
    subprocess.run([str(binary)], check=True)
print("C++03 vote counter regressions passed.")
