#include <cassert>
#include <cstddef>
#define FAssert(x) assert(x)
#define FAssertMsg(x,m) FAssert(x)
#define SAFE_DELETE_ARRAY(p) do{delete[] p;p=NULL;}while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do{delete[](reinterpret_cast<char*>(p)-(n));p=NULL;}while(0)
struct FDataStreamBase {template<class T>void Read(T*){}template<class T>void Read(int,T*){}template<class T>void Write(T){}template<class T>void Write(int,const T*){}};
struct CvXMLLoadUtility{template<class T>void SetVariableListTagPair(T**,const char*,int){}};
#include "../../CvGameCoreDLL/FSimpleDataStorage.h"
template<class T>void check(T value){FDynamicArray<T> a;FDynamic2DArray<T> b;assert(a.get(0)==T());assert(b.get(-1)==T());a.init(3);b.init(1,3);a.set(1,value);b.set(1,value);const FDynamicArray<T>& ca=a;const FDynamic2DArray<T>& cb=b;for(int i=-2;i<=5;++i){assert(ca.get(i)==(i==1?value:T()));assert(cb.get(i)==(i==1?value:T()));}T snapshot=ca.get(1);a.set(1,T());assert(snapshot==value);b()[1]=T();assert(cb.get(1)==T());}
int main(){check<int>(17);check<double>(2.5);check<bool>(true);}
