// Actual organization pass-3 bodies and derived declarations; reduced class/global interfaces.
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#define FAssert(x) ((void)0) // Release-style error return remains observable.
struct Globals {
 int calls;
 int getInfoTypeForString(std::string const& s) {
  ++calls;
  if(s=="CIV_A")return 11;
 if(s=="CIV_B")return 12;
  if(s=="LEADER_A")return 21;
 if(s=="HYBRID_A")return 31;
  return -1;
 }
} GC;
struct CvOrganizationInfo {
 std::vector<std::string> m_aszExtraXMLforPass3;
 int m_iPrereqCivilization,m_iPrereqLeader;
 CvOrganizationInfo():m_iPrereqCivilization(101),m_iPrereqLeader(102){}
 bool readPass3();
};
struct CvReligionInfo: CvOrganizationInfo {
 int m_iHybridOrganization; CvReligionInfo():m_iHybridOrganization(103){}
 bool readPass3();
};
struct CvCorporationInfo: CvOrganizationInfo {
 int m_iHybridOrganization; CvCorporationInfo():m_iHybridOrganization(103){}
 bool readPass3();
};
bool CvOrganizationInfo::readPass3()
{
	if (m_aszExtraXMLforPass3.size() < 2)
	{
		FAssert(false);
		return false;
	}

	m_iPrereqCivilization = GC.getInfoTypeForString(m_aszExtraXMLforPass3[0]);
	m_iPrereqLeader = GC.getInfoTypeForString(m_aszExtraXMLforPass3[1]);

	return true;
}

bool CvReligionInfo::readPass3()
{
	if (m_aszExtraXMLforPass3.size() < 3)
	{
		FAssert(false);
		return false;
	}
	
	if (CvOrganizationInfo::readPass3())
	{
		m_iHybridOrganization = GC.getInfoTypeForString(m_aszExtraXMLforPass3[2]);
		m_aszExtraXMLforPass3.clear();
		return true;
	}
	return false;
}

bool CvCorporationInfo::readPass3()
{
	if (m_aszExtraXMLforPass3.size() < 3)
	{
		FAssert(false);
		return false;
	}
	
	if (CvOrganizationInfo::readPass3())
	{
		m_iHybridOrganization = GC.getInfoTypeForString(m_aszExtraXMLforPass3[2]);
		m_aszExtraXMLforPass3.clear();
		return true;
	}
	return false;
}

int lookup(std::string const& s) {
 if(s=="CIV_A")return 11;
 if(s=="CIV_B")return 12;
 if(s=="LEADER_A")return 21;
 if(s=="HYBRID_A")return 31;
 return -1;
}
template<class T> void check(int n,std::string const* keys,int code) {
 T obj; obj.m_aszExtraXMLforPass3=std::vector<std::string>(n);
 for(int i=0;i<n;++i){obj.m_aszExtraXMLforPass3[i]=keys[code%7];code/=7;}
 std::vector<std::string> before=obj.m_aszExtraXMLforPass3;GC.calls=0;
 bool ok=obj.readPass3();
 if(n<3) {
  assert(!ok);assert(GC.calls==0);assert(obj.m_iPrereqCivilization==101);
  assert(obj.m_iPrereqLeader==102);assert(obj.m_iHybridOrganization==103);
  assert(obj.m_aszExtraXMLforPass3==before);
 } else {
  assert(ok);assert(GC.calls==3);
  assert(obj.m_iPrereqCivilization==lookup(before[0]));
  assert(obj.m_iPrereqLeader==lookup(before[1]));
  assert(obj.m_iHybridOrganization==lookup(before[2]));
  assert(obj.m_aszExtraXMLforPass3.empty());
  int oldC=obj.m_iPrereqCivilization,oldL=obj.m_iPrereqLeader,oldH=obj.m_iHybridOrganization;
  GC.calls=0;assert(!obj.readPass3());assert(GC.calls==0);
  assert(obj.m_iPrereqCivilization==oldC && obj.m_iPrereqLeader==oldL && obj.m_iHybridOrganization==oldH);
 }
}
int main() {
 std::string const keys[]={"","NONE","CIV_A","CIV_B","LEADER_A","HYBRID_A","UNKNOWN"};
 int count=0;
 for(int n=0;n<=5;++n)for(int code=0;code<343;++code) {
  check<CvReligionInfo>(n,keys,code);check<CvCorporationInfo>(n,keys,code);count+=2;
 }
 std::cout<<count<<" staged-list configurations passed\n";
}
