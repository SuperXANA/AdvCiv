// Complete FSimpleDataStorage.h included; engine macros/stream/XML interfaces stubbed.
#include <cassert>
#include <cstddef>
#include <iostream>
#define FAssert(x) assert(x)
#define FAssertMsg(x,m) FAssert(x)
#define SAFE_DELETE_ARRAY(p) do { delete[] (p); (p)=NULL; } while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,h) do { delete[] (reinterpret_cast<char*>(p)-(h)); (p)=NULL; } while(0)
struct FDataStreamBase {
 template<class T>void Read(T*) {}
 template<class T>void Read(int,T*) {}
 template<class T>void Write(T) {}
 template<class T>void Write(int,T*) {}
};
struct CvXMLLoadUtility { template<class T>void SetVariableListTagPair(T**,char const*,int) {} };
#include "FSimpleDataStorage.h"
char readKind(int const&); long readKind(int&);
char readKind(double const&); long readKind(double&);
char readKind(bool const&); long readKind(bool&);
template<class T,int N>void check() {
 FStaticArray<T,N> a; a.init(T());
 for(int i=0;i<N;++i)a[i]=static_cast<T>(i+1);
 FStaticArray<T,N> const& c=a;
 for(int i=0;i<N;++i) {
  assert(c[i]==static_cast<T>(i+1));
  assert(&c[i]==&a[i]);
  assert(sizeof(readKind(c[i]))==sizeof(char));
  assert(sizeof(readKind(a[i]))==sizeof(long));
 }
 a[0]=T();assert(c[0]==T());
 FStaticArray<T,N> copy(c);
 for(int i=0;i<N;++i)assert(copy.get(i)==c[i]);
 T* raw=new T[N];for(int i=0;i<N;++i)raw[i]=static_cast<T>(2);
 a.load(raw);assert(raw==NULL);
 for(int i=0;i<N;++i)assert(c[i]==static_cast<T>(2));
 a.reset();for(int i=0;i<N;++i)assert(c[i]==T());
}
int main(){
#ifdef MUTATE_CONST
 FStaticArray<int,3> a;a.init(1);
 FStaticArray<int,3> const& c=a;c[0]=7;
 assert(a.get(0)==7);std::cout<<"const mutation accepted\n";
#else
 check<int,1>();check<int,3>();check<int,8>();
 check<double,1>();check<double,3>();check<double,8>();
 check<bool,1>();check<bool,3>();check<bool,8>();
 std::cout<<"9 type/size configurations passed; const-reference and mutable-reference access distinguished\n";
#endif
}
