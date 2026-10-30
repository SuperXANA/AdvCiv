#include <cassert>
#include <cstddef>
#include <iostream>
#include <string>
#include <vector>
using std::size_t;
typedef std::string CvString;
enum PlayerVoteTypes { PLAYER_VOTE_NEVER=-5,PLAYER_VOTE_ABSTAIN=-4,PLAYER_VOTE_NO=-3,PLAYER_VOTE_YES=-2,NO_PLAYER_VOTE=-1 };
int assertions=0;
#define FAssert(x) do {if(!(x))++assertions;} while(false)
struct Globals {int votes;int getNumVoteInfos()const{return votes;}} GC;
struct CvLeaderHeadInfo {
std::vector<CvString> m_aszExtraXMLforPass3;
std::vector<int> m_aiFirstExtraXMLforPass3,m_aiSecondExtraXMLforPass3;
PlayerVoteTypes* m_paeFavoriteVoteDecision;
int *m_piFavoriteVoteDecisionAttitude,*m_piHateVoteDecisionAttitude;
CvLeaderHeadInfo():m_paeFavoriteVoteDecision(NULL),m_piFavoriteVoteDecisionAttitude(NULL),m_piHateVoteDecisionAttitude(NULL){}
~CvLeaderHeadInfo(){delete[]m_paeFavoriteVoteDecision;delete[]m_piFavoriteVoteDecisionAttitude;delete[]m_piHateVoteDecisionAttitude;}
bool readPass3();
void inherited(int n,int mask){if(mask&1){m_paeFavoriteVoteDecision=new PlayerVoteTypes[n];for(int i=0;i<n;++i)m_paeFavoriteVoteDecision[i]=PLAYER_VOTE_NO;}
if(mask&2){m_piFavoriteVoteDecisionAttitude=new int[n];for(int i=0;i<n;++i)m_piFavoriteVoteDecisionAttitude[i]=77;}
if(mask&4){m_piHateVoteDecisionAttitude=new int[n];for(int i=0;i<n;++i)m_piHateVoteDecisionAttitude[i]=-88;}}
};
bool CvLeaderHeadInfo::readPass3()
{
	int const iNumVotes = GC.getNumVoteInfos();
	size_t const iRows = m_aszExtraXMLforPass3.size();
	if (iNumVotes < 0 || iRows > static_cast<size_t>(iNumVotes) ||
		m_aiFirstExtraXMLforPass3.size() != iRows ||
		m_aiSecondExtraXMLforPass3.size() != iRows)
	{
		FAssert(false);
		return false;
	}
	// Fixed negative ballot values are not XML info-table identifiers.
	std::vector<PlayerVoteTypes> aeDecisions;
	for (size_t i = 0; i < iRows; i++)
	{
		CvString const& szDecision = m_aszExtraXMLforPass3[i];
		PlayerVoteTypes eDecision = NO_PLAYER_VOTE;
		if (szDecision == "PLAYER_VOTE_YES")
			eDecision = PLAYER_VOTE_YES;
		else if (szDecision == "PLAYER_VOTE_NO")
			eDecision = PLAYER_VOTE_NO;
		else if (szDecision == "PLAYER_VOTE_ABSTAIN")
			eDecision = PLAYER_VOTE_ABSTAIN;
		else if (szDecision == "PLAYER_VOTE_NEVER")
			eDecision = PLAYER_VOTE_NEVER;
		else
		{
			FAssert(false);
			return false;
		}
		aeDecisions.push_back(eDecision);
	}
	if (iRows == 0)
		return true; // No override: retain inherited arrays or null defaults.
	if (m_paeFavoriteVoteDecision == NULL)
	{
		m_paeFavoriteVoteDecision = new PlayerVoteTypes[iNumVotes];
		for (int i = 0; i < iNumVotes; i++)
			m_paeFavoriteVoteDecision[i] = NO_PLAYER_VOTE;
	}
	if (m_piFavoriteVoteDecisionAttitude == NULL)
	{
		m_piFavoriteVoteDecisionAttitude = new int[iNumVotes];
		for (int i = 0; i < iNumVotes; i++)
			m_piFavoriteVoteDecisionAttitude[i] = 0;
	}
	if (m_piHateVoteDecisionAttitude == NULL)
	{
		m_piHateVoteDecisionAttitude = new int[iNumVotes];
		for (int i = 0; i < iNumVotes; i++)
			m_piHateVoteDecisionAttitude[i] = 0;
	}
	for (size_t i = 0; i < iRows; i++)
	{
		m_paeFavoriteVoteDecision[i] = aeDecisions[i];
		m_piFavoriteVoteDecisionAttitude[i] = m_aiFirstExtraXMLforPass3[i];
		m_piHateVoteDecisionAttitude[i] = m_aiSecondExtraXMLforPass3[i];
	}
	m_aszExtraXMLforPass3.clear();
	m_aiFirstExtraXMLforPass3.clear();
	m_aiSecondExtraXMLforPass3.clear();
	return true;
}
int main(){int cases=0;
const char* names[]={"PLAYER_VOTE_YES","PLAYER_VOTE_NO","PLAYER_VOTE_ABSTAIN","PLAYER_VOTE_NEVER","UNIT_WARRIOR"};
PlayerVoteTypes values[]={PLAYER_VOTE_YES,PLAYER_VOTE_NO,PLAYER_VOTE_ABSTAIN,PLAYER_VOTE_NEVER};
for(int n=0;n<=5;++n)for(int rows=0;rows<=7;++rows)for(int kind=0;kind<5;++kind)for(int mask=0;mask<8;++mask){
GC.votes=n;CvLeaderHeadInfo info;info.inherited(n,mask);
for(int i=0;i<rows;++i){info.m_aszExtraXMLforPass3.push_back(names[kind]);info.m_aiFirstExtraXMLforPass3.push_back(10+i);info.m_aiSecondExtraXMLforPass3.push_back(-20-i);}
PlayerVoteTypes* oldDecision=info.m_paeFavoriteVoteDecision;int* oldFavorite=info.m_piFavoriteVoteDecisionAttitude;int* oldHate=info.m_piHateVoteDecisionAttitude;
bool expected=rows<=n&&(rows==0||kind<4);assert(info.readPass3()==expected);
if(!expected){assert(info.m_paeFavoriteVoteDecision==oldDecision);assert(info.m_piFavoriteVoteDecisionAttitude==oldFavorite);assert(info.m_piHateVoteDecisionAttitude==oldHate);assert(info.m_aszExtraXMLforPass3.size()==static_cast<size_t>(rows));}
else {assert(info.m_aszExtraXMLforPass3.empty());assert(info.m_aiFirstExtraXMLforPass3.empty());assert(info.m_aiSecondExtraXMLforPass3.empty());
for(int i=0;i<n;++i){if(rows>0){assert(info.m_paeFavoriteVoteDecision[i]==(i<rows?values[kind]:((mask&1)?PLAYER_VOTE_NO:NO_PLAYER_VOTE)));
assert(info.m_piFavoriteVoteDecisionAttitude[i]==(i<rows?10+i:((mask&2)?77:0)));assert(info.m_piHateVoteDecisionAttitude[i]==(i<rows?-20-i:((mask&4)?-88:0)));}
else {assert((info.m_paeFavoriteVoteDecision!=NULL)==((mask&1)!=0));assert((info.m_piFavoriteVoteDecisionAttitude!=NULL)==((mask&2)!=0));assert((info.m_piHateVoteDecisionAttitude!=NULL)==((mask&4)!=0));}}
PlayerVoteTypes* decisions=info.m_paeFavoriteVoteDecision;int* favorite=info.m_piFavoriteVoteDecisionAttitude;int* hate=info.m_piHateVoteDecisionAttitude;assert(info.readPass3());assert(info.m_paeFavoriteVoteDecision==decisions);assert(info.m_piFavoriteVoteDecisionAttitude==favorite);assert(info.m_piHateVoteDecisionAttitude==hate);
}
if(!expected)for(int i=0;i<n;++i){if(mask&1)assert(info.m_paeFavoriteVoteDecision[i]==PLAYER_VOTE_NO);if(mask&2)assert(info.m_piFavoriteVoteDecisionAttitude[i]==77);if(mask&4)assert(info.m_piHateVoteDecisionAttitude[i]==-88);}
++cases;
}
for(int n=0;n<=5;++n)for(int missing=0;missing<2;++missing){GC.votes=n;CvLeaderHeadInfo info;info.m_aszExtraXMLforPass3.push_back("PLAYER_VOTE_YES");if(missing==0)info.m_aiFirstExtraXMLforPass3.push_back(1);else info.m_aiSecondExtraXMLforPass3.push_back(2);assert(!info.readPass3());assert(info.m_paeFavoriteVoteDecision==NULL);++cases;}
GC.votes=-1;CvLeaderHeadInfo info;assert(!info.readPass3());++cases;
std::cout<<cases<<" staged-finalizer cases passed\n";
}
