#pragma once

#include "FDataStreamBase.h"
#include "EnumTraits.h"
#include "BoostPythonPCH.h"
#include <string>

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
	// XANA: 10-27-2026 Strings must use the string codec, not pointer-to-bool conversion.
	void Write(const TCHAR* szVal)	{ if (m_pStream) m_pStream->WriteString(szVal); }
	void Read(int* piValue)			{ if (m_pStream) m_pStream->Read(piValue); }
	void Read(bool* pbValue)		{ if (m_pStream) m_pStream->Read(pbValue); }
	// The caller must provide a sufficiently large buffer, as with the base API.
	void Read(TCHAR* szVal)			{ if (m_pStream) m_pStream->ReadString(szVal); }
	// XANA: 10-27-2026 Use owning strings when the destination size is unknown.
	void WriteString(std::string const& szVal) { if (m_pStream) m_pStream->WriteString(szVal); }
	void WriteString(std::wstring const& szVal) { if (m_pStream) m_pStream->WriteString(szVal); }
	void ReadString(std::string& szVal) { if (m_pStream) m_pStream->ReadString(szVal); }
	void ReadString(std::wstring& szVal) { if (m_pStream) m_pStream->ReadString(szVal); }
private:
	// Prevent copying to ensure it remains a thin temporary wrapper
	CvDataStream(const CvDataStream&);
	CvDataStream& operator=(const CvDataStream&);

	FDataStreamBase* m_pStream;
};