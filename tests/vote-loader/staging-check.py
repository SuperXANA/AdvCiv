#!/usr/bin/env python3
"""Actual early vote staging block plus complete finalizer, with XML/leader shells."""
from pathlib import Path
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
source=(root/'CvGameCoreDLL/CvInfo_Civilization.cpp').read_text()
start=source.index('"VoteDecisionAttitudes"')
start=source.rindex('\tif (',0,start)
end=source.index('// XANA: 01-24-2026 Leader Specific Player Vote Diplomacy',start)
stage=source[start:end]
start=source.index('bool CvLeaderHeadInfo::readPass3()')
end=source.index('{',start)+1
depth=1
while depth:
    depth+=(source[end]=='{')-(source[end]=='}')
    end+=1
finalizer=source[start:end]
prefix=r'''
#include <cassert>
#include <cstddef>
#include <string>
#include <vector>
#include <iostream>
typedef std::string CvString;
enum PlayerVoteTypes { NO_PLAYER_VOTE=-1, PLAYER_VOTE_YES=-2, PLAYER_VOTE_NO=-3,
                       PLAYER_VOTE_ABSTAIN=-4, PLAYER_VOTE_NEVER=-5 };
#define FAssert(x) assert(x)
struct Globals { int count; int getNumVoteInfos()const{return count;} } GC;
char const* const names[]={"PLAYER_VOTE_YES","PLAYER_VOTE_NO","PLAYER_VOTE_ABSTAIN","PLAYER_VOTE_NEVER"};
PlayerVoteTypes const decisions[]={PLAYER_VOTE_YES,PLAYER_VOTE_NO,PLAYER_VOTE_ABSTAIN,PLAYER_VOTE_NEVER};
struct Row {
    CvString name;
    std::vector<int> numbers;
};
struct XML {
    bool present;
    std::vector<Row> rows;
    int depth,row,field;
    XML(bool p=true):present(p),depth(0),row(-1),field(-1){}
};
struct Interface {
    bool SetToChildByTagName(XML* x,char const* tag) {
        assert(x->depth==0 && std::string(tag)=="VoteDecisionAttitudes");
        if(!x->present)return false;
        x->depth=1;return true;
    }
    int GetNumChildren(XML* x){assert(x->depth==1);return static_cast<int>(x->rows.size());}
    bool SetToChild(XML* x) {
        if(x->depth==1){if(x->rows.empty())return false;x->depth=2;x->row=0;return true;}
        assert(x->depth==2);x->depth=3;x->field=0;return true;
    }
    bool NextSibling(XML* x) {
        assert(x->depth==2);
        if(x->row+1>=static_cast<int>(x->rows.size()))return false;
        ++x->row;return true;
    }
    bool SetToParent(XML* x){assert(x->depth>0);--x->depth;return true;}
};
struct DLL {Interface iface;Interface* getXMLIFace(){return &iface;}} dll;
DLL* gDLL=&dll;
class CvXMLLoadUtility {
    XML& x;
public:
    explicit CvXMLLoadUtility(XML& xml):x(xml){}
    XML* GetXML(){return &x;}
    bool SkipToNextVal(){return true;}
    bool GetXmlVal(CvString& out){assert(x.depth==3&&x.field==0);out=x.rows[x.row].name;return true;}
    bool GetNextXmlVal(int& out) {
        // Baseline initializes the default before attempting sibling traversal.
        out=0;assert(x.depth==3);
        if(x.field>=static_cast<int>(x.rows[x.row].numbers.size()))return false;
        out=x.rows[x.row].numbers[x.field];++x.field;return true;
    }
};
struct CvLeaderHeadInfo {
    std::vector<CvString> m_aszExtraXMLforPass3;
    std::vector<int> m_aiFirstExtraXMLforPass3,m_aiSecondExtraXMLforPass3;
    PlayerVoteTypes* m_paeFavoriteVoteDecision;
    int *m_piFavoriteVoteDecisionAttitude,*m_piHateVoteDecisionAttitude;
    CvLeaderHeadInfo():m_paeFavoriteVoteDecision(NULL),m_piFavoriteVoteDecisionAttitude(NULL),m_piHateVoteDecisionAttitude(NULL){}
    ~CvLeaderHeadInfo(){delete[]m_paeFavoriteVoteDecision;delete[]m_piFavoriteVoteDecisionAttitude;delete[]m_piHateVoteDecisionAttitude;}
    bool stage(CvXMLLoadUtility* pXML);
    bool readPass3();
private:
    CvLeaderHeadInfo(CvLeaderHeadInfo const&);
    CvLeaderHeadInfo& operator=(CvLeaderHeadInfo const&);
};
'''
code=prefix+'bool CvLeaderHeadInfo::stage(CvXMLLoadUtility* pXML){\n'+stage+'\nreturn true;\n}\n'+finalizer
code+=r'''
XML make(int length,int ballot,int numbers,bool present) {
    XML x(present);
    for(int i=0;i<length;++i){Row row;row.name=names[(ballot+i)%4];if(numbers>0)row.numbers.push_back(7+i);if(numbers>1)row.numbers.push_back(-9-i);x.rows.push_back(row);}
    return x;
}
void read(CvLeaderHeadInfo& info,XML& x){CvXMLLoadUtility loader(x);assert(info.stage(&loader));assert(x.depth==0);}
void checkStage(CvLeaderHeadInfo const& info,XML const& expected) {
    assert(info.m_aszExtraXMLforPass3.size()==expected.rows.size());
    assert(info.m_aiFirstExtraXMLforPass3.size()==expected.rows.size());
    assert(info.m_aiSecondExtraXMLforPass3.size()==expected.rows.size());
    for(size_t i=0;i<expected.rows.size();++i){
        assert(info.m_aszExtraXMLforPass3[i]==expected.rows[i].name);
        assert(info.m_aiFirstExtraXMLforPass3[i]==(expected.rows[i].numbers.empty()?0:expected.rows[i].numbers[0]));
        assert(info.m_aiSecondExtraXMLforPass3[i]==(expected.rows[i].numbers.size()<2?0:expected.rows[i].numbers[1]));
    }
}
int main(){int cases=0;
 for(int cap=0;cap<=5;++cap)
 for(int first=0;first<=cap;++first)
 for(int second=0;second<=cap;++second)
 for(int ballot=0;ballot<4;++ballot)
 for(int numbers=0;numbers<=2;++numbers)
 for(int present=0;present<2;++present){
    GC.count=cap;CvLeaderHeadInfo info;
    XML a=make(first,ballot,2,true);
    read(info,a);checkStage(info,a);
    // Repeating a present list must not duplicate its positional rows.
    a.depth=0;read(info,a);checkStage(info,a);
    XML b=make(second,(ballot+1)%4,numbers,present!=0);
    read(info,b);XML const& expected=present?b:a;checkStage(info,expected);
    assert(info.readPass3());
    for(int i=0;i<cap;++i){
        PlayerVoteTypes expectedDecision=NO_PLAYER_VOTE;
        int favorite=0,hated=0;
        if(i<static_cast<int>(expected.rows.size())){
            for(int j=0;j<4;++j)if(expected.rows[i].name==names[j])expectedDecision=decisions[j];
            if(!expected.rows[i].numbers.empty())favorite=expected.rows[i].numbers[0];
            if(expected.rows[i].numbers.size()>1)hated=expected.rows[i].numbers[1];
        }
        assert((info.m_paeFavoriteVoteDecision?info.m_paeFavoriteVoteDecision[i]:NO_PLAYER_VOTE)==expectedDecision);
        assert((info.m_piFavoriteVoteDecisionAttitude?info.m_piFavoriteVoteDecisionAttitude[i]:0)==favorite);
        assert((info.m_piHateVoteDecisionAttitude?info.m_piHateVoteDecisionAttitude[i]:0)==hated);
    }
    assert(info.m_aszExtraXMLforPass3.empty());
    assert(info.m_aiFirstExtraXMLforPass3.empty()&&info.m_aiSecondExtraXMLforPass3.empty());
    assert(info.readPass3()); // No replay after finalization.
    ++cases;
 }
 assert(cases==2184);std::cout<<cases<<" repeated vote staging/finalization cases passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory:
    p=Path(directory);(p/'check.cpp').write_text(code)
    subprocess.run(['g++','-std=c++03','-Wall','-Wextra','-Werror','-pedantic',
                    '-fsanitize=address,undefined','-g',str(p/'check.cpp'),'-o',str(p/'check')],check=True)
    subprocess.run([str(p/'check')],check=True,
                   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1'))
