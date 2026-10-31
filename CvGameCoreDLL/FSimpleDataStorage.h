#pragma once

#ifndef F_SIMPLE_DATA_STORAGE_H
#define F_SIMPLE_DATA_STORAGE_H

#include <limits>
#include <cstddef>
#include <new>

// XANA: 10-31-2026 Native failure returns; element operations must not raise exceptions (ChatGPT)

static const int iHEADERSIZE = 8; /* 8 bytes for likely-safe alignment of 32-bit double and long-long data */
// XANA (note): if we ever get 64-bit compatibility in the DLL/EXE, I believe we would only need to double the size of the header in order to support doubles/long-long data types once more

// XANA: 10-30-2026 Checked headered allocation bytes (ChatGPT)
inline std::size_t FStorageAllocationSize(int iSize, std::size_t iElementSize)
{
	std::size_t const iMaxBytes = (std::numeric_limits<std::size_t>::max)();
	if (iSize < 0 || iElementSize == 0 ||
		static_cast<std::size_t>(iSize) >
		(iMaxBytes - iHEADERSIZE) / iElementSize)
	{
		FAssertMsg(false, "Invalid storage allocation size");
		return 0;
	}
	return iHEADERSIZE + iElementSize * static_cast<std::size_t>(iSize);
}
// XANA: 10-30-2026 Checked headered allocation bytes (ChatGPT)

// XANA: 10-31-2026 Headered element lifetime (ChatGPT)
template<typename T>
T* FStorageConstructArray(int iSize, T const& defaultValue)
{
	std::size_t const iBytes = FStorageAllocationSize(iSize, sizeof(T));
	if (iBytes == 0) return NULL;
	char* pBuffer = new (std::nothrow) char[iBytes];
	FAssertMsg(pBuffer != NULL, "Storage allocation failed");
	if (pBuffer == NULL) return NULL;
	// Store the size at the very beginning.
	*(int*)pBuffer = iSize;
	T* pArray = reinterpret_cast<T*>(pBuffer + iHEADERSIZE);
	// Element operations must not raise exceptions across the DLL interface.
	for (int i = 0; i < iSize; ++i)
		new (pArray + i) T(defaultValue);
	return pArray;
}
// XANA: 10-31-2026 Headered element lifetime (ChatGPT)

class FDataStreamBase;
class CvXMLLoadUtility;

// XANA: 10-28-2026 Array change dispatch (ChatGPT)
template<class T, class U>
struct FStorageChange
{
	static void apply(T& target, U value) { target += static_cast<T>(value); }
};
template<class T>
struct FStorageChange<T, bool>
{
	static void apply(T& target, bool value) { target = static_cast<T>(value); }
};
// XANA: 10-28-2026 Array change dispatch (ChatGPT)

template <typename T>
class FDynamicArray
{
public:
	FDynamicArray() : m_pArray(NULL) {}
	~FDynamicArray() { clear(); }
	void clear()
	{
		if (m_pArray == NULL) return;
		// XANA: 10-31-2026 Destroy constructed headered elements (ChatGPT)
		for (int i = size(); i > 0; --i)
			m_pArray[i - 1].~T();
		SAFE_DELETE_HEADERED_ARRAY(m_pArray, iHEADERSIZE);
	}
	void init(int iSize, T defaultValue = T())
	{
		if (iSize <= 0 || m_pArray != NULL) return;
		// Allocate: (Size of Header) + (Size of Data)
		// We use 8 safe bytes at the start for the 'int' size to support double/long-long values
		// Construct the elements before publishing the managed data pointer.
		m_pArray = FStorageConstructArray(iSize, defaultValue);
	}
	void uninit()
	{
		clear();
	}
	// The array "knows" its size without storing it in the class!
	int size() const
	{
		if (!m_pArray) return 0;
		const char* pBuffer = reinterpret_cast<const char*>(m_pArray);
		return *(int*)(pBuffer - iHEADERSIZE);
	}
	void reset(int iToSize = 0)
	{
		int const iSize = (iToSize > 0 ? iToSize : size());
		if (iSize > 0)
		{
			clear();
			init(iSize);
		}
	}
	T get(int i) const // XANA: 10-29-2026 Value-returning read access (ChatGPT)
	{
		if (i >= 0 && i < size())
		{
			return m_pArray[i];
		}
		return T();
	}
	void set(int i, T value)
	{
		if (i >= 0 && i < size())
		{
			m_pArray[i] = value;
		}
	}
	template<class U>
	void change(int i, U value)
	{
		if (i >= 0 && i < size())
			FStorageChange<T, U>::apply(m_pArray[i], value);
	}
	/**
	 * Converts a raw array (from XML load) into our header-managed format.
	 * @param pRawArray: The pointer filled by setVariableListTagPair
	 * @param iSize: The size passed to setVariableListTagPair
	 */
	void load(T*& pRawArray, int iSize)
	{
		if (pRawArray == NULL || iSize <= 0) return;
		// 1. Initialize our internal storage (allocates header + data)
		reset(iSize);
		if (m_pArray == NULL) return;
		// 2. Copy data from the XML-allocated pointer to our managed pointer
		for (int i = 0; i < iSize; ++i)
		{
			set(i, pRawArray[i]);
		}
		// 3. Clean up the temporary XML-allocated memory
		SAFE_DELETE_ARRAY(pRawArray); 
		pRawArray = NULL; // Ensure the outside caller doesn't keep a dangling pointer
	}
	void Read(FDataStreamBase* pStream)
	{
		int iSize = 0;
		pStream->Read(&iSize);
		if (iSize > 0)
		{
			reset(iSize);
			if (m_pArray == NULL) return;
			pStream->Read(iSize, m_pArray);
		}
		else clear(); // XANA: 10-29-2026 Empty 1D stream replaces old data (ChatGPT)
	}
	void Write(FDataStreamBase* pStream)
	{
		int const iSize = size();
		pStream->Write(iSize);
		if (iSize > 0)
		{
			pStream->Write(iSize, m_pArray);
		}
	}
	void readArray(CvXMLLoadUtility* pXML, const char* szXMLTag)
	{
		int const iSize = size();
		T* tempArray = NULL;
		pXML->SetVariableListTagPair(&tempArray, szXMLTag, iSize);
		// XANA: 10-31-2026 Release local XML staging on failed transfer (ChatGPT)
		load(tempArray, iSize);
		SAFE_DELETE_ARRAY(tempArray);
		// XANA: 10-31-2026 Release local XML staging on failed transfer (ChatGPT)
	}
	struct ConstProxyArray
	{
		const T* pArray;
		const int iSize;
		const T& operator[](int i) const
		{
			FAssert(i >= 0 && i < iSize);
			return pArray[i];
		}
	};
	// No need to pass size! It's fetched from the "hidden" header
	ConstProxyArray operator()() const
	{
		ConstProxyArray p = { m_pArray, size() };
		return p;
	}
	struct ProxyArray
	{
		T* pArray;
		const int iSize;
		T& operator[](int i)
		{
			FAssert(i >= 0 && i < iSize);
			return pArray[i];
		}
	};
	ProxyArray operator()()
	{
		ProxyArray p = { m_pArray, size() };
		return p;
	}
	FDynamicArray(const FDynamicArray& kOther) : m_pArray(NULL) 
	{
		if (kOther.m_pArray != NULL)
		{
			this->reset(kOther.size());
			// XANA: 10-31-2026 Clean up failed element-copy construction (ChatGPT)
			for (int i = 0; m_pArray != NULL && i < kOther.size(); ++i)
				this->m_pArray[i] = kOther.m_pArray[i];
		}
	}
	FDynamicArray& operator=(const FDynamicArray& kOther)
	{
		if (this != &kOther)
		{
			// XANA: 10-29-2026 Empty 1D assignment replaces old data (ChatGPT)
			if (kOther.size() == 0) clear();
			else this->reset(kOther.size());
			if (kOther.m_pArray != NULL && m_pArray != NULL)
			{
				for (int i = 0; i < kOther.size(); ++i)
				{
					this->m_pArray[i] = kOther.m_pArray[i];
				}
			}
		}
		return *this;
	}
private:
	T* m_pArray; // Size: 4 bytes
};

// XANA: 10-30-2026 Checked 2D dimensions (ChatGPT)
inline int FStorage2DSize(int iSizeX, int iSizeY)
{
	if (iSizeX <= 0 || iSizeY <= 0 ||
		iSizeX > (std::numeric_limits<int>::max)() / iSizeY)
		return 0;
	return iSizeX * iSizeY;
}
// XANA: 10-30-2026 Checked 2D dimensions (ChatGPT)

template <typename T>
class FDynamic2DArray
{
public:
	FDynamic2DArray() : m_pArray(NULL) {}
	~FDynamic2DArray() { clear(); }
	void clear()
	{
		if (m_pArray == NULL) return;
		// XANA: 10-31-2026 Destroy constructed headered elements (ChatGPT)
		for (int i = size(); i > 0; --i)
			m_pArray[i - 1].~T();
		SAFE_DELETE_HEADERED_ARRAY(m_pArray, iHEADERSIZE);
	}
	void init(int iSizeX, int iSizeY, T defaultValue = T())
	{
		int const iSize = FStorage2DSize(iSizeX, iSizeY);
		if ((iSize <= 0 || m_pArray != NULL)) return;
		// Allocate: (Size of Header) + (Size of Data)
		// We use 8 safe bytes at the start for the 'int' size to support double/long-long values
		// Construct the elements before publishing the managed data pointer.
		m_pArray = FStorageConstructArray(iSize, defaultValue);
	}
	void uninit()
	{
		clear();
	}
	// The array "knows" its size without storing it in the class!
	int size() const
	{
		if (!m_pArray) return 0;
		const char* pBuffer = reinterpret_cast<const char*>(m_pArray);
		return *(int*)(pBuffer - iHEADERSIZE);
	}
	void reset(int iToSizeX = 0, int iToSizeY = 0)
	{
		clear();
		init(iToSizeX, iToSizeY);
	}
	T get(int i) const // XANA: 10-29-2026 Value-returning read access (ChatGPT)
	{
		if (i >= 0 && i < size())
		{
			return m_pArray[i];
		}
		return T();
	}
	void set(int i, T value)
	{
		if (i >= 0 && i < size())
		{
			m_pArray[i] = value;
		}
	}
	template<class U>
	void change(int i, U value)
	{
		if (i >= 0 && i < size())
			FStorageChange<T, U>::apply(m_pArray[i], value);
	}
	/**
	 * Converts a raw array (from XML load) into our header-managed format.
	 * @param pRawArray: The pointer filled by setVariableListTagPair
	 * @param iSizeX/iSizeY: The size passed to setVariableListTagPair
	 */
	void load(T**& pRawArray, int iSizeX, int iSizeY)
	{
		if (pRawArray == NULL || FStorage2DSize(iSizeX, iSizeY) == 0) return;
		// 1. Initialize our internal storage (allocates header + data)
		reset(iSizeX, iSizeY);
		if (m_pArray == NULL) return;
		// 2. Copy data from the XML-allocated pointer to our managed pointer
		for (int i = 0; i < iSizeX; ++i)
		{
			if (pRawArray[i] != NULL)
			{
				for (int j = 0; j < iSizeY; ++j)
				{
					set(((i * iSizeY) + j), pRawArray[i][j]);
				}
			}
		}
		// 3. Clean up the temporary XML-allocated memory
		for (int i = 0; i < iSizeX; i++)
		{
			SAFE_DELETE_ARRAY(pRawArray[i]);
		}
		SAFE_DELETE_ARRAY(pRawArray);
		pRawArray = NULL; // Ensure the outside caller doesn't keep a dangling pointer
	}
	void Read(FDataStreamBase* pStream)
	{
		int iSize = 0;
		pStream->Read(&iSize);
		if (iSize > 0)
		{
			reset(iSize, 1); // XANA: 10-28-2026 Preserve flat allocation (ChatGPT)
			if (m_pArray == NULL) return;
			pStream->Read(iSize, m_pArray);
		}
		else clear(); // XANA: 10-28-2026 Empty stream replaces old data (ChatGPT)
	}
	void Write(FDataStreamBase* pStream)
	{
		int const iSize = size();
		pStream->Write(iSize);
		if (iSize > 0)
		{
			pStream->Write(iSize, m_pArray);
		}
	}
	struct ConstProxyArray
	{
		const T* pArray;
		const int iSize;
		const T& operator[](int i) const
		{
			FAssert(i >= 0 && i < iSize);
			return pArray[i];
		}
	};
	// No need to pass size! It's fetched from the "hidden" header
	ConstProxyArray operator()() const
	{
		ConstProxyArray p = { m_pArray, size() };
		return p;
	}
	struct ProxyArray
	{
		T* pArray;
		const int iSize;
		T& operator[](int i)
		{
			FAssert(i >= 0 && i < iSize);
			return pArray[i];
		}
	};
	ProxyArray operator()()
	{
		ProxyArray p = { m_pArray, size() };
		return p;
	}
	FDynamic2DArray(const FDynamic2DArray& kOther) : m_pArray(NULL) 
	{
		if (kOther.m_pArray != NULL)
		{
			this->reset(kOther.size(), 1); // XANA: 10-28-2026 Preserve flat allocation (ChatGPT)
			// XANA: 10-31-2026 Clean up failed element-copy construction (ChatGPT)
			for (int i = 0; m_pArray != NULL && i < kOther.size(); ++i)
				this->m_pArray[i] = kOther.m_pArray[i];
		}
	}
	FDynamic2DArray& operator=(const FDynamic2DArray& kOther)
	{
		if (this != &kOther)
		{
			this->reset(kOther.size(), 1); // XANA: 10-28-2026 Preserve flat allocation (ChatGPT)
			if (kOther.m_pArray != NULL && m_pArray != NULL)
			{
				for (int i = 0; i < kOther.size(); ++i)
				{
					this->m_pArray[i] = kOther.m_pArray[i];
				}
			}
		}
		return *this;
	}
private:
	T* m_pArray; // Size: 4 bytes
};

template <typename T, int iSIZE>
class FStaticArray
{
public:
	FStaticArray() : m_pArray(NULL) {}
	~FStaticArray() { clear(); }
	void clear()
	{
		if (m_pArray == NULL) return;
		SAFE_DELETE_ARRAY(m_pArray);
	}
	void init(T defaultValue = T())
	{
		if (m_pArray == NULL && iSIZE > 0)
		{
			m_pArray = new (std::nothrow) T[iSIZE];
			FAssertMsg(m_pArray != NULL, "Storage allocation failed");
			if (m_pArray == NULL) return;
			for (int i = 0; i < iSIZE; ++i)
			{
				m_pArray[i] = defaultValue;
			}
		}
	}
	void uninit()
	{
		clear();
	}
	void reset()
	{
		clear();
		init();
	}
	T const& operator[](int i) const // XANA: 10-30-2026 Const static-array access (ChatGPT)
	{
		FAssert(i >= 0 && i < iSIZE);
		return m_pArray[i];
	}
	T& operator[](int i)
	{
		FAssert(i >= 0 && i < iSIZE);
		return m_pArray[i];
	}
	T get(int i) const
	{
		FAssert(i >= 0 && i < iSIZE && m_pArray != NULL);
		if (i < 0 || i >= iSIZE || m_pArray == NULL) return T();
		return m_pArray[i];
	}
	void set(int i, T value)
	{
		FAssert(i >= 0 && i < iSIZE && m_pArray != NULL);
		if (i < 0 || i >= iSIZE || m_pArray == NULL) return;
		m_pArray[i] = value;
	}
	template<class U>
	void change(int i, U value)
	{
		FAssert(i >= 0 && i < iSIZE && m_pArray != NULL);
		if (i < 0 || i >= iSIZE || m_pArray == NULL) return;
		FStorageChange<T, U>::apply(m_pArray[i], value);
	}
	/**
	 * Converts a raw array (from XML load) into our static format.
	 * @param pRawArray: The pointer filled by setVariableListTagPair
	 */
	void load(T*& pRawArray)
	{
		if (pRawArray == NULL || iSIZE <= 0) return;
		// 1. Initialize our internal storage now
		reset();
		if (m_pArray == NULL) return;
		// 2. Copy data from the XML-allocated pointer to our managed pointer
		for (int i = 0; i < iSIZE; ++i)
		{
			set(i, pRawArray[i]);
		}
		// 3. Clean up the temporary XML-allocated memory
		SAFE_DELETE_ARRAY(pRawArray); 
		pRawArray = NULL; // Ensure the outside caller doesn't keep a dangling pointer
	}
	void Read(FDataStreamBase* pStream)
	{
		reset();
		if (m_pArray == NULL) return;
		pStream->Read(iSIZE, m_pArray);
	}
	void Write(FDataStreamBase* pStream)
	{
		FAssert(m_pArray != NULL);
		if (m_pArray == NULL) return;
		pStream->Write(iSIZE, m_pArray);
	}
	void readArray(CvXMLLoadUtility* pXML, const char* szXMLTag)
	{
		T* tempArray = NULL;
		pXML->SetVariableListTagPair(&tempArray, szXMLTag, iSIZE);
		// XANA: 10-31-2026 Release local XML staging on failed transfer (ChatGPT)
		load(tempArray);
		SAFE_DELETE_ARRAY(tempArray);
		// XANA: 10-31-2026 Release local XML staging on failed transfer (ChatGPT)
	}
	FStaticArray(const FStaticArray& kOther) : m_pArray(NULL) 
	{
		if (kOther.m_pArray != NULL)
		{
			// XANA: 10-31-2026 Clean up failed static-array construction (ChatGPT)
			this->reset();
			for (int i = 0; m_pArray != NULL && i < iSIZE; ++i)
				this->m_pArray[i] = kOther.m_pArray[i];

			// XANA: 10-31-2026 Clean up failed static-array construction (ChatGPT)
		}
	}
	FStaticArray& operator=(const FStaticArray& kOther)
	{
		if (this != &kOther)
		{
			this->reset();
			if (kOther.m_pArray != NULL && m_pArray != NULL)
			{
				for (int i = 0; i < iSIZE; ++i)
				{
					this->m_pArray[i] = kOther.m_pArray[i];
				}
			}
		}
		return *this;
	}
private:
	T* m_pArray;
};

#endif