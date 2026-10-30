#include <cassert>
#include <iostream>
#include <map>
#include <string>
// Surrogate enum declaration; production MAKE_INFO_ENUM also declares an enum.
enum WarUtilityAspectAITypes { NO_WARUTILITYASPECTAI=-1, TEST_MAX_ASPECT_ID=1000 };
struct Globals {std::map<std::string,int> ids;mutable int calls;Globals():calls(0){}
int getInfoTypeForString(const char* s)const{++calls;std::map<std::string,int>::const_iterator i=ids.find(s);return i==ids.end()?-1:i->second;}
} GC;
struct Case0 {mutable WarUtilityAspectAITypes m_eXMLID;Case0():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_GREED_FOR_ASSETS")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case1 {mutable WarUtilityAspectAITypes m_eXMLID;Case1():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_GREED_FOR_VASSALS")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case2 {mutable WarUtilityAspectAITypes m_eXMLID;Case2():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_GREED_FOR_SPACE")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case3 {mutable WarUtilityAspectAITypes m_eXMLID;Case3():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_GREED_FOR_CASH")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case4 {mutable WarUtilityAspectAITypes m_eXMLID;Case4():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_LOATHING")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case5 {mutable WarUtilityAspectAITypes m_eXMLID;Case5():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_MILITARY_VICTORY")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case6 {mutable WarUtilityAspectAITypes m_eXMLID;Case6():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_PRESERVATION_OF_PARTNERS")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case7 {mutable WarUtilityAspectAITypes m_eXMLID;Case7():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_RECONQUISTA")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case8 {mutable WarUtilityAspectAITypes m_eXMLID;Case8():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_REBUKE")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case9 {mutable WarUtilityAspectAITypes m_eXMLID;Case9():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_FIDELITY")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case10 {mutable WarUtilityAspectAITypes m_eXMLID;Case10():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_HIRED_HAND")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case11 {mutable WarUtilityAspectAITypes m_eXMLID;Case11():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_BORDER_DISPUTES")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case12 {mutable WarUtilityAspectAITypes m_eXMLID;Case12():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_SUCKING_UP")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case13 {mutable WarUtilityAspectAITypes m_eXMLID;Case13():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_PREEMPTIVE_WAR")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case14 {mutable WarUtilityAspectAITypes m_eXMLID;Case14():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_KING_MAKING")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case15 {mutable WarUtilityAspectAITypes m_eXMLID;Case15():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_EFFORT")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case16 {mutable WarUtilityAspectAITypes m_eXMLID;Case16():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_RISK")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case17 {mutable WarUtilityAspectAITypes m_eXMLID;Case17():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_ILL_WIL")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case18 {mutable WarUtilityAspectAITypes m_eXMLID;Case18():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_AFFECTION")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case19 {mutable WarUtilityAspectAITypes m_eXMLID;Case19():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_DISTRACTION")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case20 {mutable WarUtilityAspectAITypes m_eXMLID;Case20():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_PUBLIC_OPPOSITION")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case21 {mutable WarUtilityAspectAITypes m_eXMLID;Case21():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_REVOLTS")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case22 {mutable WarUtilityAspectAITypes m_eXMLID;Case22():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_ULTERIOR_MOTIVES")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case23 {mutable WarUtilityAspectAITypes m_eXMLID;Case23():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_FAIR_PLAY")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case24 {mutable WarUtilityAspectAITypes m_eXMLID;Case24():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_BELLICOSITY")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case25 {mutable WarUtilityAspectAITypes m_eXMLID;Case25():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_TACTICAL_SITUATION")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case26 {mutable WarUtilityAspectAITypes m_eXMLID;Case26():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_LOVE_OF_PEACE")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case27 {mutable WarUtilityAspectAITypes m_eXMLID;Case27():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_THIRD_PARTY_INTERVENTION")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
struct Case28 {mutable WarUtilityAspectAITypes m_eXMLID;Case28():m_eXMLID(NO_WARUTILITYASPECTAI){}
	WarUtilityAspectAITypes xmlID() const { return (m_eXMLID == NO_WARUTILITYASPECTAI) ? (m_eXMLID = (WarUtilityAspectAITypes)GC.getInfoTypeForString("WARUTILITYASPECTAI_DRAMATIC_ARC")) : m_eXMLID; } /* XANA (note): m_eXMLID is mutuable, so can be changed here */
};
int main(){int cases=0;
for(int reverse=0;reverse<2;++reverse){GC.ids.clear();
GC.ids["WARUTILITYASPECTAI_GREED_FOR_ASSETS"]=reverse?28:0;
GC.ids["WARUTILITYASPECTAI_GREED_FOR_VASSALS"]=reverse?27:1;
GC.ids["WARUTILITYASPECTAI_GREED_FOR_SPACE"]=reverse?26:2;
GC.ids["WARUTILITYASPECTAI_GREED_FOR_CASH"]=reverse?25:3;
GC.ids["WARUTILITYASPECTAI_LOATHING"]=reverse?24:4;
GC.ids["WARUTILITYASPECTAI_MILITARY_VICTORY"]=reverse?23:5;
GC.ids["WARUTILITYASPECTAI_PRESERVATION_OF_PARTNERS"]=reverse?22:6;
GC.ids["WARUTILITYASPECTAI_RECONQUISTA"]=reverse?21:7;
GC.ids["WARUTILITYASPECTAI_REBUKE"]=reverse?20:8;
GC.ids["WARUTILITYASPECTAI_FIDELITY"]=reverse?19:9;
GC.ids["WARUTILITYASPECTAI_HIRED_HAND"]=reverse?18:10;
GC.ids["WARUTILITYASPECTAI_BORDER_DISPUTES"]=reverse?17:11;
GC.ids["WARUTILITYASPECTAI_SUCKING_UP"]=reverse?16:12;
GC.ids["WARUTILITYASPECTAI_PREEMPTIVE_WAR"]=reverse?15:13;
GC.ids["WARUTILITYASPECTAI_KING_MAKING"]=reverse?14:14;
GC.ids["WARUTILITYASPECTAI_EFFORT"]=reverse?13:15;
GC.ids["WARUTILITYASPECTAI_RISK"]=reverse?12:16;
GC.ids["WARUTILITYASPECTAI_ILL_WIL"]=reverse?11:17;
GC.ids["WARUTILITYASPECTAI_AFFECTION"]=reverse?10:18;
GC.ids["WARUTILITYASPECTAI_DISTRACTION"]=reverse?9:19;
GC.ids["WARUTILITYASPECTAI_PUBLIC_OPPOSITION"]=reverse?8:20;
GC.ids["WARUTILITYASPECTAI_REVOLTS"]=reverse?7:21;
GC.ids["WARUTILITYASPECTAI_ULTERIOR_MOTIVES"]=reverse?6:22;
GC.ids["WARUTILITYASPECTAI_FAIR_PLAY"]=reverse?5:23;
GC.ids["WARUTILITYASPECTAI_BELLICOSITY"]=reverse?4:24;
GC.ids["WARUTILITYASPECTAI_TACTICAL_SITUATION"]=reverse?3:25;
GC.ids["WARUTILITYASPECTAI_LOVE_OF_PEACE"]=reverse?2:26;
GC.ids["WARUTILITYASPECTAI_THIRD_PARTY_INTERVENTION"]=reverse?1:27;
GC.ids["WARUTILITYASPECTAI_DRAMATIC_ARC"]=reverse?0:28;
{const Case0 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_GREED_FOR_ASSETS"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case1 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_GREED_FOR_VASSALS"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case2 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_GREED_FOR_SPACE"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case3 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_GREED_FOR_CASH"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case4 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_LOATHING"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case5 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_MILITARY_VICTORY"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case6 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_PRESERVATION_OF_PARTNERS"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case7 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_RECONQUISTA"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case8 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_REBUKE"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case9 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_FIDELITY"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case10 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_HIRED_HAND"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case11 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_BORDER_DISPUTES"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case12 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_SUCKING_UP"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case13 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_PREEMPTIVE_WAR"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case14 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_KING_MAKING"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case15 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_EFFORT"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case16 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_RISK"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case17 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_ILL_WIL"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case18 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_AFFECTION"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case19 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_DISTRACTION"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case20 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_PUBLIC_OPPOSITION"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case21 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_REVOLTS"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case22 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_ULTERIOR_MOTIVES"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case23 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_FAIR_PLAY"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case24 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_BELLICOSITY"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case25 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_TACTICAL_SITUATION"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case26 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_LOVE_OF_PEACE"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case27 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_THIRD_PARTY_INTERVENTION"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
{const Case28 x;int before=GC.calls;int expected=GC.ids["WARUTILITYASPECTAI_DRAMATIC_ARC"];assert(x.xmlID()==expected);assert(x.xmlID()==expected);assert(GC.calls==before+1);++cases;}
}
GC.ids.clear();
{const Case0 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case1 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case2 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case3 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case4 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case5 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case6 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case7 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case8 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case9 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case10 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case11 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case12 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case13 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case14 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case15 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case16 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case17 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case18 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case19 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case20 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case21 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case22 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case23 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case24 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case25 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case26 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case27 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
{const Case28 x;int before=GC.calls;assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(x.xmlID()==NO_WARUTILITYASPECTAI);assert(GC.calls==before+2);++cases;}
std::cout<<cases<<" lookup/cache cases passed\n";
}
