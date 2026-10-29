#include <cassert>
class Info {public:
	int getShareRelativeProgressAttitudeChange() const { return m_iShareRelativeProgressAttitudeChange; }
	int getShareRelativeProgressAttitudeChangeDivisor() const { return m_iShareRelativeProgressAttitudeChangeDivisor; }
	int getShareRelativeProgressAttitudeChangeLimit() const { return m_iShareRelativeProgressAttitudeChangeLimit; }
	int getShareRelativeProgressCooperationAttitudeThreshold() const { return m_iShareRelativeProgressCooperationAttitudeThreshold; }
Info():m_iShareRelativeProgressAttitudeChange(2),m_iShareRelativeProgressAttitudeChangeDivisor(3),m_iShareRelativeProgressAttitudeChangeLimit(4),m_iShareRelativeProgressCooperationAttitudeThreshold(1){}
private:
	int m_iShareRelativeProgressAttitudeChange;
	int m_iShareRelativeProgressAttitudeChangeDivisor;
	int m_iShareRelativeProgressAttitudeChangeLimit;
	int m_iShareRelativeProgressCooperationAttitudeThreshold;
};
int main(){Info x;assert(x.getShareRelativeProgressAttitudeChange()==2);assert(x.getShareRelativeProgressAttitudeChangeDivisor()==3);assert(x.getShareRelativeProgressAttitudeChangeLimit()==4);assert(x.getShareRelativeProgressCooperationAttitudeThreshold()==1);}
