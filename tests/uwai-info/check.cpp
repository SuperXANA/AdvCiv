#include <cassert>
#include <cstring>
struct CvXMLLoadUtility { bool baseOK,present; int value; bool GetChildXmlValByName(int* out,const char* key,int fallback){assert(std::strcmp(key,"iAIWeight")==0);*out=present?value:fallback;return present;} };
struct CvInfoBase { bool read(CvXMLLoadUtility* xml){return xml->baseOK;} };


#ifndef CV_INFO_WARUTILITYASPECTAI_H
#define CV_INFO_WARUTILITYASPECTAI_H

// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvWarUtilityAspectAIInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvWarUtilityAspectAIInfo : public CvInfoBase
{
	typedef CvInfoBase base_t;
public:

	CvWarUtilityAspectAIInfo();
	~CvWarUtilityAspectAIInfo();
	
	int getAIWeight() const { return m_iAIWeight; }

	// Array access:

	bool read(CvXMLLoadUtility* pXML);

protected:
int m_iAIWeight;

};
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights

#endif


// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
CvWarUtilityAspectAIInfo::CvWarUtilityAspectAIInfo() : m_iAIWeight(0)
{}

CvWarUtilityAspectAIInfo::~CvWarUtilityAspectAIInfo()
{}

bool CvWarUtilityAspectAIInfo::read(CvXMLLoadUtility* pXML)
{
	if (!base_t::read(pXML))
		return false;

	pXML->GetChildXmlValByName(&m_iAIWeight, "iAIWeight", 100);
	return true;
}
// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
int main(){int vals[]={-100,0,25,100,250};for(int i=0;i<5;++i){CvXMLLoadUtility xml={true,true,vals[i]};CvWarUtilityAspectAIInfo info;assert(info.getAIWeight()==0);assert(info.read(&xml));assert(info.getAIWeight()==vals[i]);}CvXMLLoadUtility missing={true,false,7};CvWarUtilityAspectAIInfo a;assert(a.read(&missing));assert(a.getAIWeight()==100);CvXMLLoadUtility fail={false,true,88};CvWarUtilityAspectAIInfo b;assert(!b.read(&fail));assert(b.getAIWeight()==0);}
