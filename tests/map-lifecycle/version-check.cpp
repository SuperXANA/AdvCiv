#include <cassert>
#include <iostream>
#include <vector>
typedef unsigned int uint;
struct FDataStreamBase {std::vector<int> words;unsigned cursor;int reads;FDataStreamBase():cursor(0),reads(0){}
void Read(int* n){assert(cursor<words.size());*n=words[cursor++];++reads;}
void Read(uint* n){int value;Read(&value);*n=static_cast<uint>(value);}
void Write(int n){words.push_back(n);}void Write(uint n){words.push_back(static_cast<int>(n));}
};
struct MapStandIn {int value;MapStandIn():value(0){}void read(FDataStreamBase* p){p->Read(&value);}void write(FDataStreamBase* p)const{p->Write(value);}};
struct PlotTempChangeMap {
MapStandIn m_RealTerrainTypeMap;
MapStandIn m_RealFeatureTypeMap;
MapStandIn m_RealFeatureVarietyMap;
MapStandIn m_RealBonusTypeMap;
MapStandIn m_RealImprovementTypeMap;
MapStandIn m_RealRouteTypeMap;
MapStandIn m_TempTerrainTypeMap;
MapStandIn m_TempFeatureTypeMap;
MapStandIn m_TempFeatureVarietyMap;
MapStandIn m_TempBonusTypeMap;
MapStandIn m_TempImprovementTypeMap;
MapStandIn m_TempRouteTypeMap;
MapStandIn m_TempTerrainTimerMap;
MapStandIn m_TempFeatureTimerMap;
MapStandIn m_TempBonusTimerMap;
MapStandIn m_TempImprovementTimerMap;
MapStandIn m_TempRouteTimerMap;
	void read(FDataStreamBase* pStream)
	{
		m_RealTerrainTypeMap.read(pStream);
		m_RealFeatureTypeMap.read(pStream);
		m_RealFeatureVarietyMap.read(pStream);
		m_RealBonusTypeMap.read(pStream);
		m_RealImprovementTypeMap.read(pStream);
		m_RealRouteTypeMap.read(pStream);
		
		m_TempTerrainTypeMap.read(pStream);
		m_TempFeatureTypeMap.read(pStream);
		m_TempFeatureVarietyMap.read(pStream);
		m_TempBonusTypeMap.read(pStream);
		m_TempImprovementTypeMap.read(pStream);
		m_TempRouteTypeMap.read(pStream);
		
		m_TempTerrainTimerMap.read(pStream);
		m_TempFeatureTimerMap.read(pStream);
		m_TempBonusTimerMap.read(pStream);
		m_TempImprovementTimerMap.read(pStream);
		m_TempRouteTimerMap.read(pStream);
	}
	void write(FDataStreamBase* pStream) const
	{
		m_RealTerrainTypeMap.write(pStream);
		m_RealFeatureTypeMap.write(pStream);
		m_RealFeatureVarietyMap.write(pStream);
		m_RealBonusTypeMap.write(pStream);
		m_RealImprovementTypeMap.write(pStream);
		m_RealRouteTypeMap.write(pStream);
		
		m_TempTerrainTypeMap.write(pStream);
		m_TempFeatureTypeMap.write(pStream);
		m_TempFeatureVarietyMap.write(pStream);
		m_TempBonusTypeMap.write(pStream);
		m_TempImprovementTypeMap.write(pStream);
		m_TempRouteTypeMap.write(pStream);
		
		m_TempTerrainTimerMap.write(pStream);
		m_TempFeatureTimerMap.write(pStream);
		m_TempBonusTimerMap.write(pStream);
		m_TempImprovementTimerMap.write(pStream);
		m_TempRouteTimerMap.write(pStream);
	}
void fill(int seed){m_RealTerrainTypeMap.value=seed*100+1;
m_RealFeatureTypeMap.value=seed*100+2;
m_RealFeatureVarietyMap.value=seed*100+3;
m_RealBonusTypeMap.value=seed*100+4;
m_RealImprovementTypeMap.value=seed*100+5;
m_RealRouteTypeMap.value=seed*100+6;
m_TempTerrainTypeMap.value=seed*100+7;
m_TempFeatureTypeMap.value=seed*100+8;
m_TempFeatureVarietyMap.value=seed*100+9;
m_TempBonusTypeMap.value=seed*100+10;
m_TempImprovementTypeMap.value=seed*100+11;
m_TempRouteTypeMap.value=seed*100+12;
m_TempTerrainTimerMap.value=seed*100+13;
m_TempFeatureTimerMap.value=seed*100+14;
m_TempBonusTimerMap.value=seed*100+15;
m_TempImprovementTimerMap.value=seed*100+16;
m_TempRouteTimerMap.value=seed*100+17;}
void check(int seed)const{assert(m_RealTerrainTypeMap.value==seed*100+1);
assert(m_RealFeatureTypeMap.value==seed*100+2);
assert(m_RealFeatureVarietyMap.value==seed*100+3);
assert(m_RealBonusTypeMap.value==seed*100+4);
assert(m_RealImprovementTypeMap.value==seed*100+5);
assert(m_RealRouteTypeMap.value==seed*100+6);
assert(m_TempTerrainTypeMap.value==seed*100+7);
assert(m_TempFeatureTypeMap.value==seed*100+8);
assert(m_TempFeatureVarietyMap.value==seed*100+9);
assert(m_TempBonusTypeMap.value==seed*100+10);
assert(m_TempImprovementTypeMap.value==seed*100+11);
assert(m_TempRouteTypeMap.value==seed*100+12);
assert(m_TempTerrainTimerMap.value==seed*100+13);
assert(m_TempFeatureTimerMap.value==seed*100+14);
assert(m_TempBonusTimerMap.value==seed*100+15);
assert(m_TempImprovementTimerMap.value==seed*100+16);
assert(m_TempRouteTimerMap.value==seed*100+17);}
};
struct MapHarness {PlotTempChangeMap storage;PlotTempChangeMap* m_pTempChangesMap;MapHarness():m_pTempChangesMap(&storage){}
void readTail(FDataStreamBase* pStream,uint uiFlag){
	if (uiFlag >= 8)
		m_pTempChangesMap->read(pStream);
}
void writeFlag(FDataStreamBase* pStream){uint uiFlag;
	uiFlag = 8; // Temporary plot-change maps appended to the map stream.
pStream->Write(uiFlag);
}
void writeTail(FDataStreamBase* pStream){
	m_pTempChangesMap->write(pStream);
}
};
int main(){int cases=0;
for(uint flag=0;flag<8;++flag){FDataStreamBase s;for(int n=0;n<20;++n)s.Write(9000+n);MapHarness m;m.readTail(&s,flag);assert(s.cursor==0);assert(s.reads==0);int next;s.Read(&next);assert(next==9000);++cases;}
for(int seed=0;seed<16;++seed){MapHarness source;source.storage.fill(seed);FDataStreamBase s;source.writeFlag(&s);source.writeTail(&s);s.Write(9000);assert(s.words[0]==8);assert(s.words.size()==19);
uint flag;s.Read(&flag);MapHarness dest;dest.readTail(&s,flag);dest.storage.check(seed);assert(s.cursor==18);int next;s.Read(&next);assert(next==9000);assert(s.cursor==s.words.size());++cases;}
std::cout<<cases<<" version/payload boundary cases passed\n";
}
