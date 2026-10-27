"""Compile the actual header loader against a cursor-faithful XML tree stub.

This checks traversal and map calls, not Civ4's XML parser or gameplay.
Run from any directory; requires Python 3 and g++.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
header = (ROOT / "CvGameCoreDLL/CvXMLLoadUtility.h").read_text()
start = header.index("// XANA: 11-22-2025 Free Promotions per Unit Combats")
end = header.index("// XANA: 11-22-2025 Free Promotions per Unit Combats", start + 1)
loader = header[start:end]
STUB = r"""
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <utility>
#include <vector>
typedef char TCHAR;
struct Node {
    std::string tag, value; Node* parent; std::vector<Node*> children;
    Node(const char* t, const char* v = "") : tag(t), value(v), parent(NULL) {}
    ~Node() { for (size_t i=0;i<children.size();++i) delete children[i]; }
    Node* add(const char* t, const char* v="") {
        Node* n=new Node(t,v); n->parent=this; children.push_back(n); return n;
    }
};
struct FXml { Node* current; };
struct XML {
    bool SetToChild(FXml* x) {
        if(x->current->children.empty()) return false;
        x->current=x->current->children[0]; return true;
    }
    bool SetToChildByTagName(FXml* x,const char* t) {
        for(size_t i=0;i<x->current->children.size();++i)
            if(x->current->children[i]->tag==t) {
                x->current=x->current->children[i]; return true;
            }
        return false;
    }
    bool NextSibling(FXml* x) {
        Node* p=x->current->parent;
        if(!p) return false;
        for(size_t i=0;i+1<p->children.size();++i)
            if(p->children[i]==x->current) {
                x->current=p->children[i+1]; return true;
            }
        return false;
    }
    void SetToParent(FXml* x) { assert(x->current->parent); x->current=x->current->parent; }
};
struct DLL { XML xml; XML* getXMLIFace() { return &xml; } } dll;
DLL* gDLL=&dll;
struct Map {
    // Match the important baseline API: ValueType is a pointer, insert's
    // three-argument overload consumes a scalar bool.
    typedef Map* ValueType;
    std::map<std::pair<int,int>,bool> values;
    void reset() { values.clear(); }
    void insert(int x,int y,bool b) { assert(x>=0&&x<3&&y>=0&&y<2); values[std::make_pair(x,y)]=b; }
    bool get(int x,int y) { return values[std::make_pair(x,y)]; }
};
struct CvXMLLoadUtility {
    FXml* m_pFXml; int errors;
    CvXMLLoadUtility(FXml* x):m_pFXml(x),errors(0) {}
    void errorMessage(const char*) { ++errors; }
    bool SkipToNextVal() {
        while(m_pFXml->current->tag=="#comment")
            if(!gDLL->xml.NextSibling(m_pFXml)) return false;
        return true;
    }
    bool GetXmlVal(char* out) {
        if(!SkipToNextVal()) return false;
        std::strcpy(out,m_pFXml->current->value.c_str()); return true;
    }
    bool GetXmlVal(bool& out) {
        if(!SkipToNextVal()) return false;
        const std::string& v=m_pFXml->current->value;
        if(v!="0"&&v!="1") return false;
        out=(v=="1"); return true;
    }
    int getGlobalEnumFromString(const char* s) {
        if(!std::strcmp(s,"bad")) return -1;
        return std::atoi(s);
    }
__LOADER__
};
static Node* outer(Node* root,const char* key) {
    Node* e=root->add("entry"); e->add("#comment"); e->add("key",key);
    e->add("#comment"); return e->add("list");
}
static void pair(Node* list,const char* key,const char* value) {
    Node* e=list->add("entry"); e->add("#comment"); e->add("key",key);
    e->add("#comment"); e->add("value",value);
}
int main() {
    Node trait("trait"); FXml xml={&trait}; CvXMLLoadUtility util(&xml); Map map;
    map.insert(0,0,true);
    util.SetVariableListTagPairFor2DEnumMaps(map,"missing",3,2,true);
    assert(map.values.empty()&&xml.current==&trait);
    Node* root=trait.add("root"); root->add("#comment");
    Node* list=outer(root,"1"); list->add("#comment");
    pair(list,"2","1"); pair(list,"0","1"); pair(list,"0","0");
    pair(list,"3","1"); pair(list,"bad","1");
    list->add("empty"); pair(list,"1","bogus");
    Node* incomplete=list->add("entry"); incomplete->add("key","1");
    root->add("empty"); list=outer(root,"2"); pair(list,"1","1");
    list=outer(root,"0"); pair(list,"1","1"); list->add("#comment");
    root->add("#comment");
    util.SetVariableListTagPairFor2DEnumMaps(map,"root",3,2,true);
    assert(xml.current==&trait&&util.errors==3);
    assert(map.get(2,1)&&!map.get(0,1)&&map.get(1,0)&&!map.get(1,1));
    // Normal order with asymmetric dimensions, and reread clearing stale values.
    // Use a separate root so malformed-case state cannot mask normal behavior.
    Node* normal=trait.add("normal"); list=outer(normal,"2"); pair(list,"1","1");
    util.SetVariableListTagPairFor2DEnumMaps(map,"normal",3,2,false);
    assert(xml.current==&trait&&map.values.size()==1&&map.get(2,1));
    util.SetVariableListTagPairFor2DEnumMaps(map,"normal",0,2,false);
    assert(xml.current==&trait&&map.values.empty()&&util.errors==4);
}
"""
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "check.cpp"
    binary = Path(tmp) / "check"
    source.write_text(STUB.replace("__LOADER__", loader))
    flags = (["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
             if "--sanitize" in sys.argv else [])
    subprocess.run(["g++", "-std=c++03", "-Wall", "-Wextra", "-Werror",
                    "-pedantic"] + flags + [str(source), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print("C++03 boolean loader checks passed")
