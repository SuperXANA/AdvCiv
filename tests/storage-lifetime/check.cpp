#include <cassert>
#include <cstddef>
#include <set>
#include <iostream>
#define FAssert(x) assert(x)
#define SAFE_DELETE_ARRAY(p) do { delete[] p; p=NULL; } while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do { delete[] (reinterpret_cast<char*>(p)-(n)); p=NULL; } while(0)
struct FDataStreamBase {template<class T>void Read(T*){} template<class T>void Read(int,T*){} template<class T>void Write(T){} template<class T>void Write(int,T const*){}};
struct CvXMLLoadUtility {template<class T>void SetVariableListTagPair(T**,char const*,int){}};
#include "FSimpleDataStorage.h"

struct Failure {};
struct Tracked {
    static std::set<Tracked const*> live;
    static int copiesLeft,assignmentsLeft;
    int* payload;
    explicit Tracked(int value=0):payload(new int(value)){assert(live.insert(this).second);}
    Tracked(Tracked const& other):payload(NULL){
        assert(live.count(&other)==1);
        if(copiesLeft==0)throw Failure();
        if(copiesLeft>0)--copiesLeft;
        payload=new int(*other.payload);assert(live.insert(this).second);
    }
    Tracked& operator=(Tracked const& other){
        // Detect assignment to raw storage before reading its uninitialized pointer.
        assert(live.count(this)==1&&live.count(&other)==1);
        if(assignmentsLeft==0)throw Failure();
        if(assignmentsLeft>0)--assignmentsLeft;
        *payload=*other.payload;return *this;
    }
    ~Tracked(){assert(live.erase(this)==1);delete payload;}
    int value()const{assert(live.count(this)==1);return *payload;}
};
std::set<Tracked const*> Tracked::live;
int Tracked::copiesLeft=-1;
int Tracked::assignmentsLeft=-1;
typedef FDynamicArray<Tracked> One;
typedef FDynamic2DArray<Tracked> Two;
void initialize(One& a,int n,Tracked const& v){a.init(n,v);}
void initialize(Two& a,int n,Tracked const& v){a.init(n,1,v);}
void reset(One& a,int n){a.reset(n);}
void reset(Two& a,int n){a.reset(n,1);}

template<class Array>int lifecycle(){int cases=0;
 for(int n=0;n<=8;++n){
    assert(Tracked::live.empty());
    {
        Tracked value(7);Array a;initialize(a,n,value);
        assert(a.size()==n&&Tracked::live.size()==static_cast<size_t>(n+1));
        for(int i=0;i<n;++i)assert(a()[i].value()==7);
        Array copied(a);assert(copied.size()==n);
        Array assigned;assigned=copied;assert(assigned.size()==n);
        for(int i=0;i<n;++i)assert(copied()[i].value()==7&&assigned()[i].value()==7);
        if(n>0){a.set(0,Tracked(9));assert(a()[0].value()==9&&copied()[0].value()==7);}
        copied.clear();assigned.clear();
        assert(Tracked::live.size()==static_cast<size_t>(n+1));
        reset(a,2);assert(a.size()==2);assert(a()[0].value()==0&&a()[1].value()==0);
        a.clear();a.clear();assert(Tracked::live.size()==1);
    }
    assert(Tracked::live.empty());++cases;
 }
 // Public init may copy the by-value default argument as well as the elements.
 for(int n=1;n<=8;++n)for(int budget=0;budget<=n+1;++budget){
    assert(Tracked::live.empty());
    {
        Tracked value(13);Array a;Tracked::copiesLeft=budget;
        try {initialize(a,n,value);}catch(Failure const&){}
        Tracked::copiesLeft=-1;
        assert(a.size()==0||a.size()==n);
        assert(Tracked::live.size()==static_cast<size_t>(a.size()+1));
        a.clear();assert(Tracked::live.size()==1);
    }
    assert(Tracked::live.empty());++cases;
 }
 // Assignment can throw during the container's copy-constructor body.
 for(int n=1;n<=8;++n)for(int budget=0;budget<n;++budget){
    assert(Tracked::live.empty());
    {
        Tracked value(17);Array source;initialize(source,n,value);
        size_t const before=Tracked::live.size();Tracked::assignmentsLeft=budget;
        bool threw=false;
        try {Array copy(source);}catch(Failure const&){threw=true;}
        Tracked::assignmentsLeft=-1;
        assert(threw&&Tracked::live.size()==before);
        for(int i=0;i<n;++i)assert(source()[i].value()==17);
    }
    assert(Tracked::live.empty());++cases;
 }
 return cases;
}

int loads(){int cases=0;
 for(int n=1;n<=4;++n){
    assert(Tracked::live.empty());
    {
        Tracked* raw=new Tracked[n];for(int i=0;i<n;++i)raw[i]=Tracked(20+i);
        One a;a.load(raw,n);assert(raw==NULL&&a.size()==n);
        for(int i=0;i<n;++i)assert(a()[i].value()==20+i);
        assert(Tracked::live.size()==static_cast<size_t>(n));
    }
    assert(Tracked::live.empty());++cases;
    {
        Tracked** raw=new Tracked*[1];raw[0]=new Tracked[n];
        for(int i=0;i<n;++i)raw[0][i]=Tracked(30+i);
        Two a;a.load(raw,1,n);assert(raw==NULL&&a.size()==n);
        for(int i=0;i<n;++i)assert(a()[i].value()==30+i);
        assert(Tracked::live.size()==static_cast<size_t>(n));
    }
    assert(Tracked::live.empty());++cases;
 }
 return cases;
}
int main(){int count=lifecycle<One>()+lifecycle<Two>()+loads();assert(count==202);std::cout<<count<<" tracked lifetime/exception/ownership cases passed\n";}
