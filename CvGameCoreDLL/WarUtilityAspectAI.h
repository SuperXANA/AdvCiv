#pragma once

#ifndef CV_INFO_WARUTILITYASPECTAI_H
#define CV_INFO_WARUTILITYASPECTAI_H

// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//  class : CvWarUtilityAspectAIInfo
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class CvWarUtilityAspectAIInfo : public CvInfoBase
{
	typedef CvInfoBase base_t;
public

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