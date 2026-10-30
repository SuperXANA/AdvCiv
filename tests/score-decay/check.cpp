// Actual decay method bodies with reduced engine/score interfaces.
// scaled below is a floating-point contract stub, NOT the game's fixed-point implementation.
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>
#define FAssert(x) assert(x)
struct scaled {
 double value; explicit scaled(double v) : value(v) {}
 scaled pow(int e) const { return scaled(std::pow(value,e)); }
 int round() const { return static_cast<int>(value<0?std::ceil(value-0.5):std::floor(value+0.5)); }
};
scaled per100(int p) { return scaled(p/100.0); }
scaled operator*(int n, scaled r) { return scaled(n*r.value); }
struct AlignmentValue { int iHigh, iLow; };
struct AlignmentScore {
 AlignmentValue m_buffer[10]; int m_iCount,m_iHead,m_iHighDecay,m_iLowDecay;
 int index(int i) const { int n=m_iHead-i; return n<0?n+10:n; }
 void decay();
};
struct ReputationScore {
 std::vector<int> m_aiValues; char m_iMovingAvgSamples;
 int size() const { return static_cast<int>(m_aiValues.size()); }
 void decay();
};
void AlignmentScore::decay()
{
	scaled const iHighFactor = per100(m_iHighDecay);
	scaled const iLowFactor = per100(m_iLowDecay);
	for (int i = 0; i < m_iCount; ++i)
	{
		AlignmentValue& kAlignmentValue = m_buffer[index(i)];
		// XANA: 10-30-2026 Explicit fixed-point decay rounding (ChatGPT)
		kAlignmentValue.iHigh = (kAlignmentValue.iHigh * iHighFactor).round();
		kAlignmentValue.iLow = (kAlignmentValue.iLow * iLowFactor).round();
		// XANA: 10-30-2026 Explicit fixed-point decay rounding (ChatGPT)
	}
}

void ReputationScore::decay()
{
	FAssert(size() >= 0);
	if (m_aiValues.empty())
	{
		return;
	}
	int const iSize = size();
	int const iLastValidIndex = iSize - 1;
	int const iGameTurns = iSize - std::min(m_iMovingAvgSamples - 1, iLastValidIndex);
	if (iGameTurns <= 0)
	{
		return;
	}
	scaled const rSmoothFactor = per100(95);
	for (int iTurn = iLastValidIndex; iTurn >= iGameTurns; --iTurn)
	{
		if (iLastValidIndex - iTurn != 0)
		{
			// XANA: 10-30-2026 Explicit fixed-point decay rounding (ChatGPT)
			m_aiValues[iTurn] = (m_aiValues[iTurn] *
					rSmoothFactor.pow(iLastValidIndex - iTurn)).round();
			// XANA: 10-30-2026 Explicit fixed-point decay rounding (ChatGPT)
		}
	}
}

int nearest(double v) { return static_cast<int>(v<0?std::ceil(v-0.5):std::floor(v+0.5)); }
int main() {
 int const values[]={-100,-3,-1,0,1,3,100};
 int const factors[]={0,25,50,75,100};
 unsigned ac=0,rc=0;
 for(int v=0;v<7;++v) for(int h=0;h<5;++h) for(int l=0;l<5;++l) for(int count=0;count<=10;++count) {
  AlignmentScore a; a.m_iCount=count; a.m_iHead=(v+count)%10;
  a.m_iHighDecay=factors[h]; a.m_iLowDecay=factors[l];
  int hi[10],lo[10];
  for(int i=0;i<10;++i) { hi[i]=a.m_buffer[i].iHigh=values[v]+i; lo[i]=a.m_buffer[i].iLow=-values[v]-i; }
  for(int step=0;step<3;++step) {
   for(int i=0;i<count;++i) { int k=a.index(i); hi[k]=nearest(hi[k]*(factors[h]/100.0)); lo[k]=nearest(lo[k]*(factors[l]/100.0)); }
   a.decay();
   for(int i=0;i<10;++i) { assert(a.m_buffer[i].iHigh==hi[i]); assert(a.m_buffer[i].iLow==lo[i]); }
   assert(a.m_iCount==count);
  }
  ++ac;
 }
 for(int v=0;v<7;++v) for(int n=0;n<=12;++n) for(int samples=1;samples<=8;++samples) {
  ReputationScore r; r.m_iMovingAvgSamples=static_cast<char>(samples);
  for(int i=0;i<n;++i) r.m_aiValues.push_back(values[v]+i);
  std::vector<int> expected=r.m_aiValues;
  for(int step=0;step<3;++step) {
   for(int i=n-1;i>=n-std::min(samples-1,n-1) && i>=0;--i)
    if(n-1-i!=0) expected[i]=nearest(expected[i]*std::pow(0.95,n-1-i));
   r.decay(); assert(r.m_aiValues==expected);
  }
  ++rc;
 }
 std::cout<<ac<<" alignment and "<<rc<<" reputation configurations passed\n";
}
