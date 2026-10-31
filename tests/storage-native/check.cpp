#include <cassert>
#include <climits>
#include <cstddef>
#include <new>
#include <set>
#include <iostream>
static int failures = 0, assertions = 0;
#define FAssert(x) do { if (!(x)) ++assertions; } while (0)
#define FAssertMsg(x,m) FAssert(x)
#define SAFE_DELETE_ARRAY(p) do { delete[] p; p=NULL; } while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do { delete[] (reinterpret_cast<char*>(p)-(n)); p=NULL; } while(0)
extern "C" void* __real__ZnamRKSt9nothrow_t(std::size_t, std::nothrow_t const&);
extern "C" void* __wrap__ZnamRKSt9nothrow_t(std::size_t n, std::nothrow_t const& tag) {
    if (failures > 0) { --failures; return NULL; }
    return __real__ZnamRKSt9nothrow_t(n,tag);
}
struct FDataStreamBase {
    int count, payloadReads, writes;
    explicit FDataStreamBase(int n=0):count(n),payloadReads(0),writes(0){}
    void Read(int* n){*n=count;}
    template<class T> void Read(int n,T* p){assert(p!=NULL);++payloadReads;for(int i=0;i<n;++i)p[i]=T(40+i);}
    template<class T> void Write(T){++writes;}
    template<class T> void Write(int n,T const* p){assert(n==0||p!=NULL);++writes;}
};
struct CvXMLLoadUtility {
    bool failDestination;
    explicit CvXMLLoadUtility(bool f=false):failDestination(f){}
    template<class T> void SetVariableListTagPair(T** p,char const*,int n) {
        *p=new T[n];for(int i=0;i<n;++i)(*p)[i]=T(30+i);
        if(failDestination)failures=1;
    }
};
#include "FSimpleDataStorage.h"
struct Tracked {
    static std::set<Tracked const*> live;
    int value;
    explicit Tracked(int v=0):value(v){assert(live.insert(this).second);}
    Tracked(Tracked const& t):value(t.value){assert(live.count(&t));assert(live.insert(this).second);}
    Tracked& operator=(Tracked const& t){assert(live.count(this)&&live.count(&t));value=t.value;return *this;}
    ~Tracked(){assert(live.erase(this)==1);}
};
std::set<Tracked const*> Tracked::live;
template<class A> void initialize(A& a,int n){a.init(n);}
void initialize(FDynamic2DArray<Tracked>& a,int n){a.init(n,1);}
int main(){int cases=0;
    assert(FStorageAllocationSize(-1,1)==0);++cases;
    assert(FStorageAllocationSize(1,0)==0);++cases;
    assert(FStorageAllocationSize(1,(std::numeric_limits<std::size_t>::max)())==0);++cases;
    assert(FStorageAllocationSize(2,3)==14);++cases;
    assert(FStorageConstructArray<Tracked>(-1,Tracked())==NULL);++cases;
    for(int n=1;n<=16;++n){
        {
            FDynamicArray<Tracked> a; a.init(n,Tracked(7));
            FDynamicArray<Tracked> b(a),c;c=a;
            for(int i=0;i<n;++i)assert(b.get(i).value==7&&c.get(i).value==7);
            a.clear();a.clear();assert(b.size()==n);++cases;
            failures=1;FDynamicArray<Tracked> failed(b);assert(failed.size()==0);++cases;
            failures=1;c=b;assert(c.size()==0);++cases;
            Tracked* raw=new Tracked[n];Tracked* same=raw;
            failures=1;c.load(raw,n);assert(raw==same&&c.size()==0);delete[]raw;++cases;
            raw=new Tracked[n];c.load(raw,n);assert(raw==NULL&&c.size()==n);++cases;
            CvXMLLoadUtility xml(true);std::size_t before=Tracked::live.size();
            c.readArray(&xml,"test");assert(c.size()==0&&Tracked::live.size()==before-n);++cases;
            c.init(n);CvXMLLoadUtility ok;c.readArray(&ok,"test");
            for(int i=0;i<n;++i)assert(c.get(i).value==30+i);
            ++cases;
        }
        assert(Tracked::live.empty());
        {
            FDynamic2DArray<Tracked> a;a.init(n,2,Tracked(9));
            FDynamic2DArray<Tracked> b(a),c;c=a;
            assert(b.size()==2*n&&c.size()==2*n);++cases;
            failures=1;FDynamic2DArray<Tracked> failed(b);assert(failed.size()==0);++cases;
            failures=1;c=b;assert(c.size()==0);++cases;
            Tracked** rows=new Tracked*[n];for(int i=0;i<n;++i)rows[i]=new Tracked[2];
            Tracked** same=rows;failures=1;c.load(rows,n,2);assert(rows==same&&c.size()==0);++cases;
            c.load(rows,n,2);assert(rows==NULL&&c.size()==2*n);++cases;
        }
        assert(Tracked::live.empty());
        {
            FDynamicArray<int> a;FDataStreamBase stream(n);failures=1;a.Read(&stream);
            assert(a.size()==0&&stream.payloadReads==0);++cases;
            a.Read(&stream);assert(a.size()==n&&a.get(n-1)==40+n-1);++cases;
            FDynamic2DArray<int> b;failures=1;b.Read(&stream);assert(b.size()==0&&stream.payloadReads==1);++cases;
        }
    }
    {
        FStaticArray<Tracked,4> a;a.init(Tracked(8));FStaticArray<Tracked,4>b(a);
        assert(b.get(0).value==8);++cases;
        failures=1;FStaticArray<Tracked,4>c(a);assert(c.get(0).value==0);++cases;
        failures=1;b=a;assert(b.get(0).value==0);b.set(0,Tracked(2));++cases;
        Tracked* raw=new Tracked[4];Tracked* same=raw;failures=1;b.load(raw);assert(raw==same);++cases;
        b.load(raw);assert(raw==NULL&&b.get(0).value==0);++cases;
        std::size_t before=Tracked::live.size();CvXMLLoadUtility xml(true);b.readArray(&xml,"test");
        assert(Tracked::live.size()==before-4);++cases;
        FStaticArray<int,4> d;FDataStreamBase stream(4);failures=1;d.Read(&stream);assert(stream.payloadReads==0);++cases;
        d.Write(&stream);assert(stream.writes==0);d.change(0,5);assert(d.get(0)==0);++cases;
    }
    assert(Tracked::live.empty());assert(failures==0);assert(assertions>0);
    std::cout<<cases<<" native-return/lifetime cases passed\n";
}
