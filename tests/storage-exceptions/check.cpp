#include <cassert>
#include <cstddef>
#include <set>
#include <iostream>
#define FAssert(x) assert(x)
#define SAFE_DELETE_ARRAY(p) do { delete[] p; p=NULL; } while(0)
#define SAFE_DELETE_HEADERED_ARRAY(p,n) do { delete[] (reinterpret_cast<char*>(p)-(n)); p=NULL; } while(0)
struct FDataStreamBase {template<class T>void Read(T*){} template<class T>void Read(int,T*){} template<class T>void Write(T){} template<class T>void Write(int,T const*){}};
struct CvXMLLoadUtility {
    static int assignments,copies,defaults;
    template<class T> void SetVariableListTagPair(T** out,char const*,int n) {
        *out=new T[n];
        for(int i=0;i<n;++i)*(*out)[i].payload=30+i;
        T::assignmentsLeft=assignments;T::copiesLeft=copies;T::defaultsLeft=defaults;
    }
};
int CvXMLLoadUtility::assignments=-1;
int CvXMLLoadUtility::copies=-1;
int CvXMLLoadUtility::defaults=-1;
#include "FSimpleDataStorage.h"
struct Failure {};
struct Tracked {
    static std::set<Tracked const*> live;
    static int assignmentsLeft,copiesLeft,defaultsLeft;
    int* payload;
    static void consume(int& budget){if(budget==0)throw Failure();if(budget>0)--budget;}
    explicit Tracked(int v=0):payload(NULL){consume(defaultsLeft);payload=new int(v);assert(live.insert(this).second);}
    Tracked(Tracked const& other):payload(NULL){assert(live.count(&other)==1);consume(copiesLeft);payload=new int(*other.payload);assert(live.insert(this).second);}
    Tracked& operator=(Tracked const& other){assert(live.count(this)==1&&live.count(&other)==1);consume(assignmentsLeft);*payload=*other.payload;return *this;}
    ~Tracked(){assert(live.erase(this)==1);delete payload;}
    int value()const{assert(live.count(this)==1);return *payload;}
    static void unlimited(){assignmentsLeft=copiesLeft=defaultsLeft=-1;}
};
std::set<Tracked const*> Tracked::live;
int Tracked::assignmentsLeft=-1;
int Tracked::copiesLeft=-1;
int Tracked::defaultsLeft=-1;
void initialize(FDynamicArray<Tracked>& a,int n){a.init(n);}
template<int N>void initialize(FStaticArray<Tracked,N>& a,int n){assert(n==N);a.init();}

template<int N>int constructors(){int cases=0;
    {
        FStaticArray<Tracked,N> empty;FStaticArray<Tracked,N> copy(empty);
        copy.clear();assert(Tracked::live.empty());++cases;
    }
    for(int budget=0;budget<=2*N+1;++budget){
        assert(Tracked::live.empty());
        {
            FStaticArray<Tracked,N> source;source.init();
            for(int i=0;i<N;++i)*source[i].payload=10+i;
            size_t const before=Tracked::live.size();Tracked::assignmentsLeft=budget;
            bool threw=false;
            try {
                FStaticArray<Tracked,N> copy(source);
                Tracked::unlimited();
                for(int i=0;i<N;++i)assert(copy[i].value()==10+i);
                copy[0]=Tracked(90);assert(source[0].value()==10);
            }catch(Failure const&){threw=true;}
            Tracked::unlimited();assert(threw==(budget<2*N));
            assert(Tracked::live.size()==before);
            for(int i=0;i<N;++i)assert(source[i].value()==10+i);
        }
        assert(Tracked::live.empty());++cases;
    }
    for(int budget=0;budget<=N+1;++budget){
        FStaticArray<Tracked,N> source;source.init();size_t const before=Tracked::live.size();
        Tracked::defaultsLeft=budget;
        try {FStaticArray<Tracked,N> copy(source);}catch(Failure const&){}
        Tracked::unlimited();assert(Tracked::live.size()==before);++cases;
    }
    assert(Tracked::live.empty());return cases;
}

template<class Array>int xmlFailures(int n,int assignmentStages){int cases=0;
    for(int mode=0;mode<3;++mode){
        int const attempts=mode==0?assignmentStages+1:1;
        for(int budget=0;budget<attempts;++budget){
            assert(Tracked::live.empty());
            Array a;initialize(a,n);CvXMLLoadUtility xml;
            CvXMLLoadUtility::assignments=mode==0?budget:-1;
            CvXMLLoadUtility::copies=mode==1?0:-1;
            CvXMLLoadUtility::defaults=mode==2?0:-1;
            bool threw=false;
            try {a.readArray(&xml,"Values");}catch(Failure const&){threw=true;}
            Tracked::unlimited();
            assert(threw==(mode!=0||budget<assignmentStages));
            if(!threw)for(int i=0;i<n;++i)assert(a.get(i).value()==30+i);
            a.clear();assert(Tracked::live.empty());++cases;
        }
    }
    CvXMLLoadUtility::assignments=CvXMLLoadUtility::copies=CvXMLLoadUtility::defaults=-1;
    return cases;
}

template<class Array>int directLoad(int n){int cases=0;
    for(int budget=0;budget<n;++budget){
        Array a;initialize(a,n);Tracked* raw=new Tracked[n];Tracked* const original=raw;
        for(int i=0;i<n;++i)*raw[i].payload=50+i;
        Tracked::assignmentsLeft=budget;bool threw=false;
        try {a.load(raw);}catch(Failure const&){threw=true;}
        Tracked::unlimited();assert(threw&&raw==original);
        for(int i=0;i<n;++i)assert(raw[i].value()==50+i);
        a.clear();assert(Tracked::live.size()==static_cast<size_t>(n));
        delete[] raw;assert(Tracked::live.empty());++cases;
    }
    return cases;
}
int main(){
    int cases=constructors<1>()+constructors<2>()+constructors<3>()+constructors<4>()+constructors<8>();
    for(int n=1;n<=8;++n)cases+=xmlFailures<FDynamicArray<Tracked> >(n,n);
    cases+=xmlFailures<FStaticArray<Tracked,1> >(1,2);
    cases+=xmlFailures<FStaticArray<Tracked,2> >(2,4);
    cases+=xmlFailures<FStaticArray<Tracked,3> >(3,6);
    cases+=xmlFailures<FStaticArray<Tracked,4> >(4,8);
    cases+=xmlFailures<FStaticArray<Tracked,8> >(8,16);
    cases+=directLoad<FStaticArray<Tracked,1> >(1)+directLoad<FStaticArray<Tracked,4> >(4);
    assert(Tracked::live.empty());std::cout<<cases<<" static-construction/XML exception ownership cases passed\n";
}
