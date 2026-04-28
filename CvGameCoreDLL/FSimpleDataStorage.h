#pragma once

#ifndef F_SIMPLE_DATA_STORAGE_H
#define F_SIMPLE_DATA_STORAGE_H

static const int iHEADERSIZE = 8; /* 8 bytes for likely-safe alignment of 32-bit double and long-long data */
// XANA (note): if we ever get 64-bit compatibility in the DLL/EXE, I believe we would only need to double the size of the header in order to support doubles/long-long data types once more

class FDataStreamBase;

template <typename T>
class FDynamicArray
{
public:
	FDynamicArray() : m_pArray(NULL) {}
	~FDynamicArray() { clear(); }
	void clear()
	{
		SAFE_DELETE_HEADERED_ARRAY(m_pArray, iHEADERSIZE);
	}
	void init(int iSize, T defaultValue = T())
	{
		if (iSize <= 0 || (m_pArray != NULL && size() == iSize)) return;
		// Allocate: (Size of Header) + (Size of Data)
		// We use 8 safe bytes at the start for the 'int' size to support double/long-long values
		char* pBuffer = new char[iHEADERSIZE + (sizeof(T) * iSize)];
		// Store the size at the very beginning
		*(int*)pBuffer = iSize;
		// Set our member pointer to the start of the DATA (skipping the header)
		m_pArray = (reinterpret_cast<T*>(pBuffer + iHEADERSIZE);
		for (int i = 0; i < iSize; ++i)
		{
			m_pArray[i] = defaultValue;
		}
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
	T get(int i) const
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
	void change(int i, T delta)
	{
		if (i >= 0 && i < size())
		{
			m_pArray[i] += delta;
		}
	}
	void change(int i, bool b)
	{
		set(i, (T)b); 
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
			init(iSize);
			pStream->Read(iSize, m_pArray);
		}
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
		load(tempArray, iSize);
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
private:
	T* m_pArray; // Size: 4 bytes
	FDynamicArray(const FDynamicArray&);
	FDynamicArray& operator=(const FDynamicArray&);
};

template <typename T>
class FDynamic2DArray
{
public:
	FDynamic2DArray() : m_pArray(NULL) {}
	~FDynamic2DArray() { clear(); }
	void clear()
	{
		SAFE_DELETE_HEADERED_ARRAY(m_pArray, iHEADERSIZE);
	}
	void init(int iSizeX, int iSizeY, T defaultValue = T())
	{
		int const iSize = (iSizeX * iSizeY);
		if ((iSize <= 0 || (m_pArray != NULL && size() == iSize)) return;
		// Allocate: (Size of Header) + (Size of Data)
		// We use 8 safe bytes at the start for the 'int' size to support double/long-long values
		char* pBuffer = new char[iHEADERSIZE + (sizeof(T) * iSize)];
		// Store the size at the very beginning
		*(int*)pBuffer = iSize;
		// Set our member pointer to the start of the DATA (skipping the header)
		m_pArray = (reinterpret_cast<T*>(pBuffer + iHEADERSIZE);
		for (int i = 0; i < iSize; ++i)
		{
			m_pArray[i] = defaultValue;
		}
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
		int const iToSize = size());
		if (iToSize < (iToSizeX * iToSizeY))
		{
			clear();
			init(iToSizeX, iToSizeY);
		}
	}
	T get(int i) const
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
	void change(int i, T delta)
	{
		if (i >= 0 && i < size())
		{
			m_pArray[i] += delta;
		}
	}
	void change(int i, bool b)
	{
		set(i, (T)b); 
	}
	/**
	 * Converts a raw array (from XML load) into our header-managed format.
	 * @param pRawArray: The pointer filled by setVariableListTagPair
	 * @param iSizeX/iSizeY: The size passed to setVariableListTagPair
	 */
	void load(T**& pRawArray, int iSizeX, int iSizeY)
	{
		if (pRawArray == NULL || (iSizeX * iSizeY) <= 0) return;
		// 1. Initialize our internal storage (allocates header + data)
		reset(iSizeX, iSizeY);
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
			init(iSize);
			pStream->Read(iSize, m_pArray);
		}
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
private:
	T* m_pArray; // Size: 4 bytes
	FDynamic2DArray(const FDynamic2DArray&);
	FDynamic2DArray& operator=(const FDynamic2DArray&);
};

template <typename T, int iSIZE>
class FStaticArray
{
public:
	FStaticArray() : m_pArray(NULL) {}
	~FStaticArray() { clear(); }
	void clear()
	{
		SAFE_DELETE_ARRAY(m_pArray);
	}
	void init(T defaultValue = T())
	{
		if (m_pArray == NULL)
		{
			m_pArray = new T[iSIZE];
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
	T& operator[](int i) const
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
		FAssert(i >= 0 && i < iSIZE);
		return m_pArray[i];
	}
	void set(int i, T value)
	{
		FAssert(i >= 0 && i < iSIZE);
		m_pArray[i] = value;
	}
	void change(int i, T value)
	{
		FAssert(i >= 0 && i < iSIZE);
		m_pArray[i] += value;
	}
	void change(int i, bool b)
	{
		set(i, (T)b); 
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
		pStream->Read(iSIZE, m_pArray);
	}
	void Write(FDataStreamBase* pStream)
	{
		pStream->Write(iSIZE, m_pArray);
	}
	void readArray(CvXMLLoadUtility* pXML, const char* szXMLTag)
	{
		T* tempArray = NULL;
		pXML->SetVariableListTagPair(&tempArray, szXMLTag, iSIZE);
		load(tempArray);
	}
private:
	T* m_pArray;
	FStaticArray(const FStaticArray&);
	FStaticArray& operator=(const FStaticArray&);
};

#endif