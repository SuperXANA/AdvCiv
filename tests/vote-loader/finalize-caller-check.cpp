#include <cassert>
#include <cstddef>
#include <iostream>
#define FOR_EACH_ENUM(Name) for(int eLoopLeaderHead=0;eLoopLeaderHead<GC.count;++eLoopLeaderHead)
struct Info{bool ok;int calls;Info():ok(true),calls(0){}bool readPass3(){++calls;return ok;}};
struct Globals{Info info[5];int count;bool cleared;Info& getInfo(int i){return info[i];}void setCurrentXMLFile(const char* p){assert(p==NULL);cleared=true;}} GC;
struct Loader{int destroys;Loader():destroys(0){}void DestroyFXml(){++destroys;}bool run(){
	FOR_EACH_ENUM(LeaderHead)
	{
		if (!GC.getInfo(eLoopLeaderHead).readPass3())
		{
			DestroyFXml();
			GC.setCurrentXMLFile(NULL);
			return false;
		}
	}
DestroyFXml();GC.setCurrentXMLFile(NULL);return true;
}};
int main(){int cases=0;for(int n=0;n<=5;++n)for(int failure=-1;failure<n;++failure){GC.count=n;GC.cleared=false;for(int i=0;i<5;++i){GC.info[i].ok=i!=failure;GC.info[i].calls=0;}Loader l;assert(l.run()==(failure<0));assert(l.destroys==1);assert(GC.cleared);for(int i=0;i<n;++i)assert(GC.info[i].calls==((failure<0||i<=failure)?1:0));++cases;}std::cout<<cases<<" caller failure/cleanup cases passed\n";}
