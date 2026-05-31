#pragma once

#include "FDataStreamBase.h"
#include "EnumTraits.h"
#include "BoostPythonPCH.h"

class CvDataStream /* aka: FDataStreamExtended */
{
public:
	// Explicit constructor accepts the raw EXE stream pointer
	explicit CvDataStream(FDataStreamBase* pStream) : m_pStream(pStream) 
	{
		// Assert that the stream is not null on initialization
		FAssert(m_pStream != NULL);
	}
	// --- Clean, Type-Safe Enum Handlers ---
	template <typename EnumType>
	void WriteEnum(EnumType eValue)
	{
		BOOST_STATIC_ASSERT(enum_traits<EnumType>::is_enum);
		if (m_pStream != NULL)
		{
			m_pStream->Write(static_cast<int>(eValue));
		}
	}
	template <typename EnumType>
	void ReadEnum(EnumType& eValue)
	{
		BOOST_STATIC_ASSERT(enum_traits<EnumType>::is_enum);
		if (m_pStream != NULL)
		{
			int iTempValue = 0;
			m_pStream->Read(&iTempValue);
			eValue = static_cast<EnumType>(iTempValue);
		}
	}
	// --- Standard Primitive Boilerplate Reduction ---
	void Write(int iValue)			{ if (m_pStream) m_pStream->Write(iValue); }
	void Write(bool bValue)			{ if (m_pStream) m_pStream->Write(bValue); }
	void Write(const TCHAR* szVal)	{ if (m_pStream) m_pStream->Write(szVal); }
	void Read(int* piValue)			{ if (m_pStream) m_pStream->Read(piValue); }
	void Read(bool* pbValue)		{ if (m_pStream) m_pStream->Read(pbValue); }
	void Read(TCHAR* szVal)			{ if (m_pStream) m_pStream->Read(szVal); }
private:
	// Prevent copying to ensure it remains a thin temporary wrapper
	CvDataStream(const CvDataStream&);
	CvDataStream& operator=(const CvDataStream&);

	FDataStreamBase* m_pStream;
};