#!/usr/bin/env python3
"""Actual enclosing preference classes/loaders; ID boundaries with XML/record stubs."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
directory = Path(os.environ.get('PREFERENCE_SOURCE_DIR', str(root / 'CvGameCoreDLL')))
classes, implementations = [], []
for filename, kind in [('CvInfo_Civilization', 'Tech'), ('CvInfo_RandomEvent', 'Event'), ('CvInfo_Unit', 'Unit')]:
    name = 'Cv' + kind + 'PreferenceInfo'
    h = (directory / (filename + '.h')).read_text()
    s = (directory / (filename + '.cpp')).read_text()
    a = h.index('class ' + name + ' :')
    classes.append(h[a:h.index('\n};', a) + 4])
    a = s.index(name + '::' + name + '(')
    end = s.index('{', s.index('bool ' + name + '::read(', a)) + 1
    depth = 1
    while depth:
        depth += (s[end] == '{') - (s[end] == '}')
        end += 1
    implementations.append(s[a:end])

prefix = r'''
#include <cassert>
#include <cstddef>
#include <string>
#include <vector>
#include <iostream>
#include <climits>
#define SAFE_DELETE_ARRAY(p) do { delete[] p; p = NULL; } while (0)
#define FAssertBounds(a,b,i) assert((i) >= (a) && (i) < (b))
#define FOR_EACH_ENUM(E) for (int eLoop##E = 0; eLoop##E < GC.getNum##E##Infos(); ++eLoop##E)
typedef int TechTypes;
typedef int EventTypes;
typedef int UnitCombatTypes;
typedef int UnitClassTypes;
typedef int UnitTypes;
enum { NO_TECH=-1, NO_EVENT=-1, NO_UNITCOMBAT=-1, NO_UNITCLASS=-1, NO_UNIT=-1,
       NO_LEADER=-1, NO_CIVILIZATION=-1 };
class CvXMLLoadUtility;
struct CvInfoBase { bool read(CvXMLLoadUtility*); };
struct Globals {
    int counts[5];
    int getNumTechInfos() const { return counts[0]; }
    int getNumEventInfos() const { return counts[1]; }
    int getNumUnitCombatInfos() const { return counts[2]; }
    int getNumUnitClassInfos() const { return counts[3]; }
    int getNumUnitInfos() const { return counts[4]; }
} GC;
struct Record {
    int id;
    Record() : id(-1) {}
    bool read(CvXMLLoadUtility*);
};
struct TechPreferenceData : Record { int getTechType() const { return id; } };
struct EventPreferenceData : Record { int getEventType() const { return id; } };
struct UnitCombatPreferenceData : Record { int getUnitCombatType() const { return id; } };
struct UnitClassPreferenceData : Record { int getUnitClassType() const { return id; } };
struct UnitPreferenceData : Record { int getUnitType() const { return id; } };
'''
xml = r'''
char const* const tags[] = { "TechPreferences", "EventPreferences", "UnitCombatPreferences",
                            "UnitClassPreferences", "UnitPreferences" };
struct Xml {
    bool present[5], baseOK, skipOK;
    std::vector<int> rows[5];
    int list, row;
    Xml() : baseOK(true), skipOK(true), list(-1), row(-1) {
        for (int i=0; i<5; ++i) present[i]=false;
    }
};
struct XmlIface {
    bool SetToChildByTagName(Xml* x, char const* tag) {
        assert(x->list == -1 && x->row == -1);
        for (int i=0; i<5; ++i) if (tag == std::string(tags[i]) && x->present[i]) {
            x->list=i; return true;
        }
        return false;
    }
    int GetNumChildren(Xml* x) { assert(x->list >= 0 && x->row == -1); return static_cast<int>(x->rows[x->list].size()); }
    bool SetToChild(Xml* x) {
        assert(x->list >= 0 && x->row == -1);
        if (x->rows[x->list].empty()) return false;
        x->row=0; return true;
    }
    bool NextSibling(Xml* x) {
        assert(x->list >= 0 && x->row >= 0);
        if (x->row+1 >= static_cast<int>(x->rows[x->list].size())) return false;
        ++x->row; return true;
    }
    bool SetToParent(Xml* x) {
        assert(x->list >= 0);
        if (x->row >= 0) x->row=-1;
        else x->list=-1;
        return true;
    }
};
struct DLL { XmlIface iface; XmlIface* getXMLIFace() { return &iface; } } dll;
DLL* gDLL=&dll;
class CvXMLLoadUtility {
public:
    Xml* xml;
    explicit CvXMLLoadUtility(Xml& x) : xml(&x) {}
    Xml* GetXML() { return xml; }
    bool SkipToNextVal() { return xml->skipOK; }
    void SetInfoIDFromChildXmlVal(int& id, char const*) { id=-1; }
    static size_t size(CvTechPreferenceInfo const& x, int) { return x.m_vTechPrefData.size(); }
    static size_t size(CvEventPreferenceInfo const& x, int) { return x.m_vEventPrefData.size(); }
    static size_t size(CvUnitPreferenceInfo const& x, int kind) {
        if (kind==2) return x.m_vUnitCombatPrefData.size();
        if (kind==3) return x.m_vUnitClassPrefData.size();
        return x.m_vUnitPrefData.size();
    }
};
bool CvInfoBase::read(CvXMLLoadUtility* p) { return p->xml->baseOK; }
bool Record::read(CvXMLLoadUtility* p) {
    Xml* x=p->xml;
    assert(x->list >= 0 && x->row >= 0);
    id=x->rows[x->list][x->row]; return true;
}
'''
checks = r'''
struct Infos {
    CvTechPreferenceInfo tech;
    CvEventPreferenceInfo event;
    CvUnitPreferenceInfo unit;
    void read(Xml& x) {
        CvXMLLoadUtility loader(x);
        assert(tech.read(&loader) == x.baseOK);
        assert(event.read(&loader) == x.baseOK);
        assert(unit.read(&loader) == x.baseOK);
        assert(x.list == -1 && x.row == -1);
    }
    int index(int kind, int id) const {
        if (kind==0) return tech.getTechPreferenceIndex(id);
        if (kind==1) return event.getEventPreferenceIndex(id);
        if (kind==2) return unit.getUnitCombatPreferenceIndex(id);
        if (kind==3) return unit.getUnitClassPreferenceIndex(id);
        return unit.getUnitPreferenceIndex(id);
    }
    int value(int kind, int pos) const {
        if (kind==0) return tech.getTechPreference(pos).id;
        if (kind==1) return event.getEventPreference(pos).id;
        if (kind==2) return unit.getUnitCombatPreference(pos).id;
        if (kind==3) return unit.getUnitClassPreference(pos).id;
        return unit.getUnitPreference(pos).id;
    }
    size_t size(int kind) const {
        if (kind==0) return CvXMLLoadUtility::size(tech,kind);
        if (kind==1) return CvXMLLoadUtility::size(event,kind);
        return CvXMLLoadUtility::size(unit,kind);
    }
    void verify(std::vector<int> const expected[5]) const {
        for (int kind=0; kind<5; ++kind) {
            assert(size(kind) == expected[kind].size());
            for (int id=0; id<GC.counts[kind]; ++id) {
                int last=-1;
                for (size_t i=0; i<expected[kind].size(); ++i)
                    if (expected[kind][i] == id) last=static_cast<int>(i);
                assert(index(kind,id) == last);
                if (last >= 0) assert(value(kind,last) == id);
            }
        }
    }
};
int main() {
    int const ids[]={INT_MIN,-2,-1,0,1,5,6,99,INT_MAX};
    int cases=0;
    for(int rotation=0;rotation<6;++rotation)
    for(int first=0;first<9;++first)
    for(int second=0;second<9;++second)
    for(int mask=0;mask<32;++mask) {
        for(int kind=0;kind<5;++kind)GC.counts[kind]=(rotation+kind)%6;
        Infos infos;
        std::vector<int> expected[5];
        Xml initial;
        for(int kind=0;kind<5;++kind) {
            initial.present[kind]=true;
            if(GC.counts[kind]>0) {
                initial.rows[kind].push_back(0);
                expected[kind].push_back(0);
            }
        }
        infos.read(initial);infos.verify(expected);
        Xml replacement;
        for(int kind=0;kind<5;++kind)if(mask&(1<<kind)) {
            replacement.present[kind]=true;
            int const rows[]={ids[first],ids[second],GC.counts[kind]>0?GC.counts[kind]-1:-1};
            expected[kind].clear();
            for(int row=0;row<3;++row) {
                replacement.rows[kind].push_back(rows[row]);
                if(rows[row]>=0 && rows[row]<GC.counts[kind])expected[kind].push_back(rows[row]);
            }
        }
        infos.read(replacement);infos.verify(expected);
        ++cases;
    }
    assert(cases==15552);
    std::cout<<cases<<" preference ID-boundary configurations passed\n";
}
'''
with tempfile.TemporaryDirectory() as directory_name:
    p = Path(directory_name)
    (p / 'check.cpp').write_text(prefix + '\n'.join(classes) + xml + '\n'.join(implementations) + checks)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
                    '-fsanitize=address,undefined', '-g', str(p / 'check.cpp'), '-o', str(p / 'check')], check=True)
    subprocess.run([str(p / 'check')], check=True,
                   env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
