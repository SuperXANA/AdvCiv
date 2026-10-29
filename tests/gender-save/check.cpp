#include <cassert>
#include <vector>
#include <cstddef>
const int MAX_PLAYERS=3;
struct Stream{std::vector<int> data;std::size_t pos;Stream():pos(0){}void Write(int n,const int*p){for(int i=0;i<n;++i)data.push_back(p[i]);}void Read(int n,int*p){for(int i=0;i<n;++i){assert(pos<data.size());p[i]=data[pos++];}}};
struct AI{int m_aiFavoriteGenderCounter[MAX_PLAYERS],m_aiHateGenderCounter[MAX_PLAYERS];void write(Stream*pStream){
	pStream->Write(MAX_PLAYERS, m_aiFavoriteGenderCounter);
	pStream->Write(MAX_PLAYERS, m_aiHateGenderCounter);
}void read(Stream*pStream){
	pStream->Read(MAX_PLAYERS, m_aiFavoriteGenderCounter);
	pStream->Read(MAX_PLAYERS, m_aiHateGenderCounter);
}};
int main(){AI a,b;for(int i=0;i<MAX_PLAYERS;++i){a.m_aiFavoriteGenderCounter[i]=10+i;a.m_aiHateGenderCounter[i]=100+i;b.m_aiFavoriteGenderCounter[i]=b.m_aiHateGenderCounter[i]=-1;}Stream stream;a.write(&stream);int sentinel=7654321;stream.Write(1,&sentinel);b.read(&stream);for(int i=0;i<MAX_PLAYERS;++i){assert(b.m_aiFavoriteGenderCounter[i]==10+i);assert(b.m_aiHateGenderCounter[i]==100+i);}int end=0;stream.Read(1,&end);assert(end==sentinel);assert(stream.pos==stream.data.size());}
