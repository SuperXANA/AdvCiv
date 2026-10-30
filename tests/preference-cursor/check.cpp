// Actual preference declarations and implementation with cursor/XML interfaces stubbed.
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
enum { NO_TECH=-1,NO_EVENT=-1,NO_UNITCOMBAT=-1,NO_UNITCLASS=-1,NO_UNIT=-1 };
struct Node { std::string tag,value; Node* parent; std::vector<Node> children; Node():parent(0){} };
struct Xml { Node* node; };
struct Iface {
 bool SetToChild(Xml* x) { if(x->node->children.empty())return false;x->node=&x->node->children[0];return true; }
 bool SetToParent(Xml* x) { if(!x->node->parent)return false;x->node=x->node->parent;return true; }
};
struct DLL { Iface iface; Iface* getXMLIFace(){return &iface;} } dll;
DLL* gDLL=&dll;
struct CvXMLLoadUtility {
 Xml xml; Xml* GetXML(){return &xml;}
 bool value(std::string const& tag,std::string& out) {
  for(unsigned i=0;i<xml.node->children.size();++i)
   if(xml.node->children[i].tag==tag){out=xml.node->children[i].value;return true;}
  return false;
 }
 void SetInfoIDFromChildXmlVal(int& id,char const* tag) {
  std::string s;value(tag,s);
  id=(s=="TYPE_A"?7:(s=="TECH_ROCKETRY"?11:(s=="TECH_COMPUTERS"?12:(s=="TECH_MUSIC"?13:-1))));
 }
 void GetChildXmlValByName(int* out,char const* tag) {std::string s;*out=value(tag,s)?std::atoi(s.c_str()):0;}
 void GetChildXmlValByName(bool* out,char const* tag) {std::string s;*out=value(tag,s)?std::atoi(s.c_str())!=0:false;}
};

#ifndef CVXMLSTRUCTS_H
#define CVXMLSTRUCTS_H

// XANA: 04-26-2025 Favorite Technologies for Advanced Civ
struct TechPreferenceData
{
	TechPreferenceData() : iTech(NO_TECH), iTechValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getTechType() const;
	int getTechValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iTech;
	int iTechValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 04-26-2025 Favorite Technologies for Advanced Civ


// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
struct EventPreferenceData
{
	EventPreferenceData() : iEvent(NO_EVENT), iEventValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getEventType() const;
	int getEventValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iEvent;
	int iEventValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process


// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
struct UnitCombatPreferenceData
{
	UnitCombatPreferenceData() : iUnitCombat(NO_UNITCOMBAT), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitCombatType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnitCombat;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

struct UnitClassPreferenceData
{
	UnitClassPreferenceData() : iUnitClass(NO_UNITCLASS), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitClassType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnitClass;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};

struct UnitPreferenceData
{
	UnitPreferenceData() : iUnit(NO_UNIT), iUnitValueModifierPercent(0), 
	bPreferredChoice(false), bNotPreferredChoice(false) {}
	
	int getUnitType() const;
	int getUnitValueModifierPercent() const;
	bool isPreferredChoice() const;
	bool isNotPreferredChoice() const;
	
	bool read(CvXMLLoadUtility* pXML);
	
	int iUnit;
	int iUnitValueModifierPercent;
	bool bPreferredChoice;
	bool bNotPreferredChoice;
};
// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
	
#endif	// CVXMLSTRUCTS_H



// XANA: 04-26-2025 Favorite Technologies for Advanced Civ
int TechPreferenceData::getTechType() const
{
	return iTech;
}

int TechPreferenceData::getTechValueModifierPercent() const
{
	return iTechValueModifierPercent;
}

bool TechPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool TechPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool TechPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	pXML->SetInfoIDFromChildXmlVal(iTech, "TechType");
	pXML->GetChildXmlValByName(&iTechValueModifierPercent, "iTechValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}
// XANA: 04-26-2025 Favorite Technologies for Advanced Civ


// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process
int EventPreferenceData::getEventType() const
{
	return iEvent;
}

int EventPreferenceData::getEventValueModifierPercent() const
{
	return iEventValueModifierPercent;
}

bool EventPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool EventPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool EventPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	pXML->SetInfoIDFromChildXmlVal(iEvent, "Event");
	pXML->GetChildXmlValByName(&iEventValueModifierPercent, "iEventValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}
// XANA: 09-05-2026 Event Preferences for AI Decision-Making Process


// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type
int UnitCombatPreferenceData::getUnitCombatType() const
{
	return iUnitCombat;
}

int UnitCombatPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitCombatPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitCombatPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitCombatPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	pXML->SetInfoIDFromChildXmlVal(iUnitCombat, "UnitCombatType");
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}

int UnitClassPreferenceData::getUnitClassType() const
{
	return iUnitClass;
}

int UnitClassPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitClassPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitClassPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitClassPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	pXML->SetInfoIDFromChildXmlVal(iUnitClass, "UnitClassType");
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}

int UnitPreferenceData::getUnitType() const
{
	return iUnit;
}

int UnitPreferenceData::getUnitValueModifierPercent() const
{
	return iUnitValueModifierPercent;
}

bool UnitPreferenceData::isPreferredChoice() const
{
	return bPreferredChoice;
}

bool UnitPreferenceData::isNotPreferredChoice() const
{
	return bNotPreferredChoice;
}

bool UnitPreferenceData::read(CvXMLLoadUtility* pXML)
{
	// Caller already positioned the XML cursor on this preference record.
	pXML->SetInfoIDFromChildXmlVal(iUnit, "UnitType");
	pXML->GetChildXmlValByName(&iUnitValueModifierPercent, "iUnitValueModifierPercent");
	pXML->GetChildXmlValByName(&bPreferredChoice, "bPreferredChoice");
	pXML->GetChildXmlValByName(&bNotPreferredChoice, "bNotPreferredChoice");
	return true;
}
// XANA: 06-07-2025 Leader-Specific Favorite Unit Combat Type


void field(Node& row,char const* tag,std::string const& value) {
 Node n;n.tag=tag;n.value=value;n.parent=&row;row.children.push_back(n);
}
std::string number(int n) { if(n==-25)return "-25";if(n==75)return "75";return "0"; }
template<class T> int check(char const* idTag,char const* modifierTag,int T::* id,int T::* modifier) {
 int count=0;int values[]={-25,0,75};char const* ids[]={"TYPE_A","NONE","MISSING"};
 for(int mask=0;mask<16;++mask)for(int v=0;v<3;++v)for(int flags=0;flags<4;++flags)for(int kind=0;kind<3;++kind) {
  Node row;row.tag="Preference";row.children.reserve(4);
  if(mask&1)field(row,idTag,ids[kind]);
  if(mask&2)field(row,modifierTag,number(values[v]));
  if(mask&4)field(row,"bPreferredChoice",(flags&1)?"1":"0");
  if(mask&8)field(row,"bNotPreferredChoice",(flags&2)?"1":"0");
  CvXMLLoadUtility xml;xml.xml.node=&row;T data;
  assert(data.read(&xml));assert(xml.xml.node==&row);
  assert(data.*id==((mask&1)&&kind==0?7:-1));
  assert(data.*modifier==((mask&2)?values[v]:0));
  assert(data.isPreferredChoice()==((mask&4)&&(flags&1)));
  assert(data.isNotPreferredChoice()==((mask&8)&&(flags&2)));
  Node next;next.tag="Preference";xml.xml.node=&next;
  assert(data.read(&xml));assert(xml.xml.node==&next);
  assert(data.*id==-1 && data.*modifier==0);
  assert(!data.isPreferredChoice() && !data.isNotPreferredChoice());
  ++count;
 }
 return count;
}
int main() {
 int n=0;
 n+=check<TechPreferenceData>("TechType","iTechValueModifierPercent",&TechPreferenceData::iTech,&TechPreferenceData::iTechValueModifierPercent);
 n+=check<EventPreferenceData>("Event","iEventValueModifierPercent",&EventPreferenceData::iEvent,&EventPreferenceData::iEventValueModifierPercent);
 n+=check<UnitCombatPreferenceData>("UnitCombatType","iUnitValueModifierPercent",&UnitCombatPreferenceData::iUnitCombat,&UnitCombatPreferenceData::iUnitValueModifierPercent);
 n+=check<UnitClassPreferenceData>("UnitClassType","iUnitValueModifierPercent",&UnitClassPreferenceData::iUnitClass,&UnitClassPreferenceData::iUnitValueModifierPercent);
 n+=check<UnitPreferenceData>("UnitType","iUnitValueModifierPercent",&UnitPreferenceData::iUnit,&UnitPreferenceData::iUnitValueModifierPercent);
 char const* keys[]={"TECH_ROCKETRY","TECH_COMPUTERS","TECH_MUSIC"};
 char const* modifiers[]={"33","50","0"};int expected[]={33,50,0};
 for(int i=0;i<3;++i) {
  Node row;field(row,"TechType",keys[i]);field(row,"iTechValueModifierPercent",modifiers[i]);field(row,"bPreferredChoice",i==2?"1":"0");field(row,"bNotPreferredChoice","0");
  CvXMLLoadUtility xml;xml.xml.node=&row;TechPreferenceData data;
  assert(data.read(&xml));assert(data.getTechType()==11+i);assert(data.getTechValueModifierPercent()==expected[i]);
  assert(data.isPreferredChoice()==(i==2));assert(!data.isNotPreferredChoice());assert(xml.xml.node==&row);
 }
 std::cout<<n<<" record configurations and 3 supplied tech XML rows passed\n";
}
