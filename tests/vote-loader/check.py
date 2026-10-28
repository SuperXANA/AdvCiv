#!/usr/bin/env python3
"""Actual readPass3 with a tree/cursor stub; not an engine XML or DLL test."""
import os
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = pathlib.Path(os.environ.get('VOTE_LOADER_SOURCE',
    str(root / 'CvGameCoreDLL/CvInfo_Civilization.cpp'))).read_text()
start = source.index('bool CvLeaderHeadInfo::readPass3(')
method = source[start:source.index('\n}', start) + 2]
fixture = r'''
#include <cassert>
#include <cstdlib>
#include <string>
#include <vector>
typedef std::string CvString;
enum PlayerVoteTypes { PLAYER_VOTE_NEVER=-5, PLAYER_VOTE_ABSTAIN=-4,
    PLAYER_VOTE_NO=-3, PLAYER_VOTE_YES=-2, NO_PLAYER_VOTE=-1 };
struct Node {
    std::string name,value; Node* parent; std::vector<Node*> children;
    Node(std::string n,std::string v="",Node* p=NULL):name(n),value(v),parent(p){}
    ~Node(){for(unsigned i=0;i<children.size();++i)delete children[i];}
    Node* add(std::string n,std::string v=""){
        Node* p=new Node(n,v,this);children.push_back(p);return p;
    }
};
struct Cursor { Node* at; };
struct XMLInterface {
    bool SetToChildByTagName(Cursor* c,char const* n){
        for(unsigned i=0;i<c->at->children.size();++i)
            if(c->at->children[i]->name==n){c->at=c->at->children[i];return true;}
        return false;
    }
    int GetNumChildren(Cursor* c){return static_cast<int>(c->at->children.size());}
    bool SetToChild(Cursor* c){if(c->at->children.empty())return false;
        c->at=c->at->children[0];return true;}
    bool SetToParent(Cursor* c){if(!c->at->parent)return false;
        c->at=c->at->parent;return true;}
    bool NextSibling(Cursor* c){Node* p=c->at->parent;if(!p)return false;
        for(unsigned i=0;i+1<p->children.size();++i)
            if(p->children[i]==c->at){c->at=p->children[i+1];return true;}
        return false;
    }
} iface;
struct DLL { XMLInterface* getXMLIFace(){return &iface;} } dll;
DLL* gDLL=&dll;
struct Globals { int votes; int getNumVoteInfos()const{return votes;} } GC;
int invalidDecisions=0;
#define FAssert(b) do {if(!(b))++invalidDecisions;} while(false)
struct CvXMLLoadUtility {
    Cursor cursor;
    explicit CvXMLLoadUtility(Node* n){cursor.at=n;}
    Cursor* GetXML(){return &cursor;}
    bool SkipToNextVal(){return true;}
    template<class T>void InitList(T** p,int n,T value=T()){
        *p=new T[n];for(int i=0;i<n;++i)(*p)[i]=value;
    }
    bool GetChildXmlVal(CvString& s){s.clear();if(!iface.SetToChild(&cursor))return false;
        s=cursor.at->value;return true;}
    bool GetXmlVal(CvString& s){s=cursor.at->value;return true;}
    bool GetNextXmlVal(int& n,int defaultValue=0){n=defaultValue;
        if(!iface.NextSibling(&cursor))return false;
        n=std::atoi(cursor.at->value.c_str());return true;}
};
struct CvLeaderHeadInfo {
    PlayerVoteTypes* m_paeFavoriteVoteDecision;
    int *m_piFavoriteVoteDecisionAttitude,*m_piHateVoteDecisionAttitude;
    CvLeaderHeadInfo():m_paeFavoriteVoteDecision(NULL),
        m_piFavoriteVoteDecisionAttitude(NULL),m_piHateVoteDecisionAttitude(NULL){}
    ~CvLeaderHeadInfo(){delete[]m_paeFavoriteVoteDecision;
        delete[]m_piFavoriteVoteDecisionAttitude;delete[]m_piHateVoteDecisionAttitude;}
    bool readPass3(CvXMLLoadUtility*);
};
'''
cases = r'''
void row(Node* list,char const* decision,bool numbers=true){
    Node* entry=list->add("Entry");entry->add("Decision",decision);
    if(numbers){entry->add("Favorite","7");entry->add("Hate","-3");}
}
int main(){
    char const* values[]={"PLAYER_VOTE_YES","PLAYER_VOTE_NO",
        "PLAYER_VOTE_ABSTAIN","PLAYER_VOTE_NEVER","UNKNOWN"};
    int expected[]={-2,-3,-4,-5,-1};
    // Absent, empty, partial, exact and excessive lists, including zero votes.
    for(int n=0;n<=5;++n)for(int rows=-1;rows<=7;++rows){
        GC.votes=n;Node root("Leader");Node* list=NULL;
        if(rows>=0)list=root.add("VoteDecisionAttitudes");
        for(int i=0;i<rows;++i)row(list,values[i%5]);
        CvXMLLoadUtility xml(&root);CvLeaderHeadInfo info;
        bool ok=info.readPass3(&xml);
        assert(xml.cursor.at==&root);
        assert(ok==(rows<=n));
        if(rows>n || rows<0){assert(info.m_paeFavoriteVoteDecision==NULL);continue;}
        for(int i=0;i<n;++i){
            bool valid=i<rows && i%5!=4;
            assert(info.m_paeFavoriteVoteDecision[i]==(i<rows?expected[i%5]:-1));
            assert(info.m_piFavoriteVoteDecisionAttitude[i]==(valid?7:0));
            assert(info.m_piHateVoteDecisionAttitude[i]==(valid?-3:0));
        }
    }
    GC.votes=1;Node root("Leader");row(root.add("VoteDecisionAttitudes"),values[0],false);
    CvXMLLoadUtility xml(&root);CvLeaderHeadInfo info;
    assert(info.readPass3(&xml));assert(xml.cursor.at==&root);
    assert(info.m_piFavoriteVoteDecisionAttitude[0]==0);
    assert(info.m_piHateVoteDecisionAttitude[0]==0);
}
'''
with tempfile.TemporaryDirectory() as temp:
    cpp = pathlib.Path(temp) / 'check.cpp'
    exe = pathlib.Path(temp) / 'check'
    cpp.write_text(fixture + method + cases)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(cpp), '-o', str(exe)], check=True)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1')
    subprocess.run([str(exe)], check=True, env=env)
print('55 list/cursor cases passed; C++03/ASan/UBSan, XML tree stub only')
