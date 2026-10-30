#include <cassert>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>
typedef wchar_t wchar;
enum GenderTypes { NO_GENDER=-1,G0,G1,GENDER_BOUND=127 };
struct Player {GenderTypes gender;int favorite,hate;GenderTypes getGender()const{return gender;}int AI_getFavoriteGenderAttitude(int)const{return favorite;}int AI_getHateGenderAttitude(int)const{return hate;}} players[1];
#define GET_PLAYER(x) players[x]
struct Info {const wchar* text;const wchar* getDescription()const{return text;}};
struct Globals {int count,queries;Info infos[2];int getNumGenderInfos()const{return count;}Info const& getInfo(GenderTypes g){assert(g>=0&&g<count);++queries;return infos[g];}} GC;
struct CvWString {std::wstring text;void Format(const wchar*,const wchar*,const wchar* value){text=value;}const wchar* GetCString()const{return text.c_str();}};
struct CvWStringBuffer {std::wstring text;void append(const wchar* s){text+=s;}void append(const CvWString& s){text+=s.text;}};
struct DLL {std::vector<std::string> keys;std::vector<int> values;CvWString getText(const char* key,int value,const wchar* extra){keys.push_back(key);values.push_back(value);CvWString s;s.text=extra;return s;}} dll;
DLL* gDLL=&dll;
#define SETCOLR L""
#define ENDCOLR L""
#define TEXT_COLOR(x) L"color"
#define NEWLINE L"\n"
struct CvGameTextMgr {
	void appendToAttitudeBreakdownWithExtraDescription(CvWStringBuffer& szBreakdown, int iPass,
			int iAttitudeChange, int& iTotal,
			char const* szTextKey, char const* szTextKeyAlt = NULL, 
			wchar const* szExtraDescription = NULL);
void render(CvWStringBuffer& szBreakdown,int iPass,const Player& kPlayer,int eTargetPlayer,int& iTotal){
		GenderTypes const eTargetGender = GET_PLAYER(eTargetPlayer).getGender();
		if (eTargetGender >= 0 && eTargetGender < GC.getNumGenderInfos())
		{
			appendToAttitudeBreakdownWithExtraDescription(szBreakdown, iPass,
					kPlayer.AI_getFavoriteGenderAttitude(eTargetPlayer), iTotal,
					"TXT_KEY_MISC_ATTITUDE_FAVORED_GENDER",
					"TXT_KEY_MISC_ATTITUDE_DISFAVORED_GENDER",
					GC.getInfo(eTargetGender).getDescription());
			appendToAttitudeBreakdownWithExtraDescription(szBreakdown, iPass,
					kPlayer.AI_getHateGenderAttitude(eTargetPlayer), iTotal,
					"TXT_KEY_MISC_ATTITUDE_GENDER_ALLY",
					"TXT_KEY_MISC_ATTITUDE_GENDER_ENEMY",
					GC.getInfo(eTargetGender).getDescription());
		}

}
};
void CvGameTextMgr::appendToAttitudeBreakdownWithExtraDescription(CvWStringBuffer& szBreakdown, int iPass,
	int iAttitudeChange, int& iTotal, char const* szTextKey, char const* szTextKeyAlt,
	wchar const* szExtraDescription)
{
	if ((iPass == 0) ? (iAttitudeChange > 0) : (iAttitudeChange < 0))
	{
		CvWString szTempBuffer;
		szTempBuffer.Format(SETCOLR L"%s" ENDCOLR,
				TEXT_COLOR(iAttitudeChange > 0 ?
				"COLOR_POSITIVE_TEXT" : "COLOR_NEGATIVE_TEXT"),
				gDLL->getText(iAttitudeChange > 0 || szTextKeyAlt == NULL ?
				szTextKey : szTextKeyAlt, iAttitudeChange,
				szExtraDescription).GetCString());
		szBreakdown.append(NEWLINE);
		szBreakdown.append(szTempBuffer);
		iTotal += iAttitudeChange;
	}
}
int main(){int cases=0;GC.infos[0].text=L"Mare \u2605";GC.infos[1].text=L"Stallion \u03a9";int genders[]={-1,0,1,2,99};
for(int available=0;available<=2;++available)for(int g=0;g<5;++g)for(int pass=0;pass<2;++pass)for(int fav=-2;fav<=2;++fav)for(int hate=-2;hate<=2;++hate){
GC.count=available;GC.queries=0;players[0].gender=static_cast<GenderTypes>(genders[g]);players[0].favorite=fav;players[0].hate=hate;dll.keys.clear();dll.values.clear();CvWStringBuffer buf;int total=10;CvGameTextMgr mgr;mgr.render(buf,pass,players[0],0,total);
bool valid=genders[g]>=0&&genders[g]<available;int expected=10,entries=0;if(valid){if((pass==0&&fav>0)||(pass==1&&fav<0)){expected+=fav;++entries;}if((pass==0&&hate>0)||(pass==1&&hate<0)){expected+=hate;++entries;}}
assert(total==expected);assert(GC.queries==(valid?2:0));assert(dll.keys.size()==static_cast<unsigned>(entries));assert(dll.values.size()==dll.keys.size());
if(entries>0)assert(buf.text.find(GC.infos[genders[g]].text)!=std::wstring::npos);else assert(buf.text.empty());
int index=0;if(valid&&((pass==0&&fav>0)||(pass==1&&fav<0))){assert(dll.keys[index]==(fav>0?"TXT_KEY_MISC_ATTITUDE_FAVORED_GENDER":"TXT_KEY_MISC_ATTITUDE_DISFAVORED_GENDER"));assert(dll.values[index++]==fav);}
if(valid&&((pass==0&&hate>0)||(pass==1&&hate<0))){assert(dll.keys[index]==(hate>0?"TXT_KEY_MISC_ATTITUDE_GENDER_ALLY":"TXT_KEY_MISC_ATTITUDE_GENDER_ENEMY"));assert(dll.values[index++]==hate);}++cases;
}std::cout<<cases<<" wide-description/pass/lookup cases passed\n";}
