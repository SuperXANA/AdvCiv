#include <cassert>
#include <climits>
#include <cstddef>
#include <iostream>
#define FAssert(x) assert(x)
#define FAssertMsg(x,m) FAssert(x)
#define SAFE_DELETE_ARRAY(p) do{delete[] p;p=NULL;}while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do{delete[](reinterpret_cast<char*>(p)-(n));p=NULL;}while(0)
struct FDataStreamBase {template<class T>void Read(T*){}template<class T>void Read(int,T*){}template<class T>void Write(T){}template<class T>void Write(int,const T*){}};
struct CvXMLLoadUtility{template<class T>void SetVariableListTagPair(T**,const char*,int){}};
#include "FSimpleDataStorage.h"
template<class T>int check(T value){int cases=0;
for(int x=1;x<=5;++x)for(int y=1;y<=5;++y){
FDynamic2DArray<T> a;a.init(x,y,value);assert(a.size()==x*y);for(int i=0;i<a.size();++i)assert(a.get(i)==value);
T** raw=new T*[x];for(int i=0;i<x;++i){raw[i]=(i%2)?NULL:new T[y];if(raw[i])for(int j=0;j<y;++j)raw[i][j]=value;}
a.load(raw,x,y);assert(raw==NULL);assert(a.size()==x*y);for(int i=0;i<x;++i)for(int j=0;j<y;++j)assert(a.get(i*y+j)==((i%2)?T():value));++cases;}
const int invalid[][2]={{-1,-1},{-2,3},{3,-2},{0,3},{3,0},{0,0},{INT_MIN,-1},{-1,INT_MIN},{INT_MIN,INT_MIN},{INT_MAX,2},{2,INT_MAX},{46341,46341}};
for(unsigned k=0;k<sizeof(invalid)/sizeof(invalid[0]);++k){int x=invalid[k][0],y=invalid[k][1];FDynamic2DArray<T> a;a.init(x,y,value);assert(a.size()==0);
a.init(2,2,value);a.init(x,y);assert(a.size()==4);for(int i=0;i<4;++i)assert(a.get(i)==value);
T** raw=new T*[1];raw[0]=new T[1];raw[0][0]=value;T** saved=raw;a.load(raw,x,y);assert(raw==saved);assert(raw[0][0]==value);assert(a.size()==4);delete[]raw[0];delete[]raw;
a.reset(x,y);assert(a.size()==0);++cases;}
return cases;}
int main(){int cases=check<int>(17)+check<double>(2.5)+check<bool>(true);
#ifndef STORAGE_DIMENSION_ORIGINAL
assert(FStorage2DSize(INT_MAX,1)==INT_MAX);++cases;
assert(FStorage2DSize(1,INT_MAX)==INT_MAX);++cases;
assert(FStorage2DSize(INT_MAX/2,2)==INT_MAX-1);++cases;
assert(FStorage2DSize(INT_MAX/2+1,2)==0);++cases;
assert(FStorage2DSize(46340,46340)==2147395600);++cases;
assert(FStorage2DSize(46341,46341)==0);++cases;
assert(FStorage2DSize(-1,-1)==0);++cases;
assert(FStorage2DSize(INT_MIN,-1)==0);++cases;
assert(FStorage2DSize(0,INT_MAX)==0);++cases;
#endif
std::cout<<cases<<" dimension/allocation/load cases passed\n";}
