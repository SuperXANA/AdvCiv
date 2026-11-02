
#include <vector>
#include <climits>
#include <cstdio>
#include <cstdlib>
typedef double scaled;
typedef wchar_t wchar;
scaled per100(int x) { return x / 100.0; }
enum WarUtilityAspectAITypes { FIRST_ID = INT_MIN, LAST_ID = INT_MAX };
int assertions = 0;
#define FAssertBounds(a,b,c) ((void)(((c) >= (a) && (c) < (b)) || (++assertions, false)))
struct Info {
    int weight;
    int getAIWeight() const { return weight; }
    wchar_t const* getDescription() const { return L"ASPECT_NAME"; }
};
struct Globals {
    std::vector<Info> infos;
    mutable int accesses;
    int getNumWarUtilityAspectAIInfos() const { return (int)infos.size(); }
    Info const& getInfo(WarUtilityAspectAITypes e) const {
        ++accesses;
        if (e < 0 || e >= getNumWarUtilityAspectAIInfos()) {
            std::fprintf(stderr, "invalid global metadata access: %d\n", (int)e);
            std::abort();
        }
        return infos[e];
    }
} GC;
struct UWAI {
scaled aspectWeight(WarUtilityAspectAITypes eAspect) const
	{
		FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), eAspect);
		if (eAspect < 0 || eAspect >= GC.getNumWarUtilityAspectAIInfos())
			return 0;
		return per100(GC.getInfo(eAspect).getAIWeight());
	}
wchar const* aspectName(WarUtilityAspectAITypes eAspect) const
	{
		FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), eAspect);
		if (eAspect < 0 || eAspect >= GC.getNumWarUtilityAspectAIInfos())
			return L"";
		return GC.getInfo(eAspect).getDescription();
	}
};
struct CvLeaderHeadInfo {
    int* m_prWarUtilityAspects;
    scaled getWarUtilityAspect(int i) const;
};
scaled CvLeaderHeadInfo::getWarUtilityAspect(int i) const
{
	FAssertBounds(0, GC.getNumWarUtilityAspectAIInfos(), i);
	if (i < 0 || i >= GC.getNumWarUtilityAspectAIInfos())
		return 0;
	return m_prWarUtilityAspects ? per100(m_prWarUtilityAspects[i]) : 0; // advc.003t
}
void require(bool ok) { if (!ok) std::abort(); }
int main(int argc, char** argv) {
    UWAI uwai;
    CvLeaderHeadInfo leaderInfo;
    if (argc == 2) {
        GC.infos.resize(1);
        int* storage = new int[1]; storage[0] = 100;
        leaderInfo.m_prWarUtilityAspects = storage;
        if (argv[1][0] == 'w') return (int)uwai.aspectWeight((WarUtilityAspectAITypes)-1);
        if (argv[1][0] == 'n') return uwai.aspectName((WarUtilityAspectAITypes)-1)[0];
        return (int)leaderInfo.getWarUtilityAspect(-1);
    }
    int const counts[] = {0, 1, 2, 29, 64};
    int cases = 0;
    for (int n = 0; n < 5; ++n) {
        int count = counts[n]; GC.infos.resize(count);
        int* storage = count ? new int[count] : NULL;
        for (int j = 0; j < count; ++j) {
            GC.infos[j].weight = (j % 3 == 0 ? -100 : j % 3 == 1 ? 0 : 175);
            storage[j] = (j % 3 == 0 ? 0 : j % 3 == 1 ? -50 : 250);
        }
        std::vector<int> ids;
        ids.push_back(INT_MIN); ids.push_back(-2); ids.push_back(-1);
        for (int j = 0; j < count; ++j) ids.push_back(j);
        ids.push_back(count); ids.push_back(count + 1); ids.push_back(INT_MAX);
        for (int nullStorage = 0; nullStorage < 2; ++nullStorage) {
            leaderInfo.m_prWarUtilityAspects = nullStorage ? NULL : storage;
            for (unsigned j = 0; j < ids.size(); ++j) {
                int id = ids[j]; bool valid = id >= 0 && id < count;
                int before = assertions; GC.accesses = 0;
                scaled w = uwai.aspectWeight((WarUtilityAspectAITypes)id);
                wchar_t const* label = uwai.aspectName((WarUtilityAspectAITypes)id);
                scaled overrideWeight = leaderInfo.getWarUtilityAspect(id);
                require(w == (valid ? per100(GC.infos[id].weight) : 0));
                require(label != NULL);
                require(valid ? label == GC.infos[id].getDescription() : label[0] == 0);
                require(overrideWeight == (valid && !nullStorage ? per100(storage[id]) : 0));
                require(GC.accesses == (valid ? 2 : 0));
                require(assertions - before == (valid ? 0 : 3));
                ++cases;
            }
        }
        delete[] storage;
    }
    std::printf("%d cases passed; invalid IDs never dereference metadata or leader arrays\n", cases);
}
