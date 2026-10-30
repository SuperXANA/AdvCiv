// Scoped extracted UWAI report-name methods; engine interfaces and ASCII conversion stubbed.
#include <cassert>
#include <cctype>
#include <cwchar>
#include <string>
#include <iostream>
typedef wchar_t wchar;
typedef unsigned int uint;
enum WarUtilityAspectAITypes { NO_WARUTILITYASPECTAI = -1, ASPECT_0, ASPECT_1, ASPECT_2 };
struct Info { std::wstring name; wchar const* getDescription() const { return name.c_str(); } };
struct Globals { Info infos[3]; int getNumWarUtilityAspectAIInfos() const { return 3; } Info const& getInfo(WarUtilityAspectAITypes e) const { assert(e>=0 && e<3); return infos[e]; } } GC;
#define FAssertBounds(lo, hi, value) assert((value)>=(lo) && (value)<(hi))
class CvString : public std::string {
public:
 CvString& operator=(char const* s) { assign(s); return *this; }
 void Copy(wchar const* w) { clear(); if(w) for(;*w;++w) { assert(*w>=0 && *w<128); push_back(static_cast<char>(*w)); } }
 char const* GetCString() const { return c_str(); }
};
struct Report { bool mute; bool isMute() const { return mute; } };
class UWAI { public:
	wchar const* aspectName(WarUtilityAspectAITypes eAspect) const
	{
		FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), eAspect);
		return GC.getInfo(eAspect).getDescription();
	}
};
UWAI globalUWAI;
class WarUtilityAspect {
public:
 Report m_kReport; WarUtilityAspectAITypes id;
 WarUtilityAspectAITypes xmlID() const { return id; }
 UWAI const& getUWAI() const { return globalUWAI; }
 char const* aspectName() const;
};
char const* WarUtilityAspect::aspectName() const
{
	// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
	static CvString szBuffer;
	szBuffer.Copy(getUWAI().aspectName(xmlID()));
	if (m_kReport.isMute()) // Skip report-name formatting when muted
		return szBuffer.GetCString();
	// XANA: 11-01-2025 Leader Specific War Utility Aspect Weights
	// Convert from upper case to mixed case and replace underscores with spaces
	for (uint i = 0; i < szBuffer.length(); i++)
	{
		if (szBuffer[i] == '_')
			szBuffer[i] = ' ';
		if (i > 0 && szBuffer[i - 1] != ' ')
			szBuffer[i] = static_cast<char>(::tolower(szBuffer[i]));
	}
	return szBuffer.GetCString();
}

std::string expected(std::string s, bool mute) {
 if(mute) return s;
 for(size_t i=0;i<s.size();++i) {
  if(s[i]=='_') s[i]=' ';
  if(i>0 && s[i-1]!=' ') s[i]=static_cast<char>(std::tolower(s[i]));
 }
 return s;
}
int main() {
 const char* names[]={"", "GREED_FOR_ASSETS", "A", "ALREADY mixed Case", "__TWO__SPACES_", "123_ABC", "RISK & EFFORT"};
 unsigned count=0;
 for(unsigned i=0;i<7;++i) for(unsigned j=0;j<7;++j) for(int mute=0;mute<2;++mute) {
  for(int k=0;k<3;++k) { std::string s=names[(i+k)%7]; GC.infos[k].name.assign(s.begin(),s.end()); }
  WarUtilityAspect a; a.id=ASPECT_0; a.m_kReport.mute=(mute!=0);
  char const* p=a.aspectName(); assert(std::string(p)==expected(names[i],mute!=0));
  WarUtilityAspect b; b.id=ASPECT_1; b.m_kReport.mute=(mute==0);
  assert(std::string(b.aspectName())==expected(names[(i+1)%7],mute==0));
  std::string replacement=names[j]; GC.infos[0].name.assign(replacement.begin(),replacement.end());
  assert(std::string(a.aspectName())==expected(replacement,mute!=0));
  assert(globalUWAI.aspectName(ASPECT_2)==GC.infos[2].getDescription());
  ++count;
 }
 std::cout << count << " report-name sequences passed\n";
}
