#!/usr/bin/env python3
"""Compile the actual temporary-change map and five CvPlot timer wrappers.

Engine objects and ArrayEnumMap are instrumented stubs; this is not a DLL test.
"""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / 'CvGameCoreDLL/CvPlot.cpp').read_text()
kinds = ['Terrain', 'Feature', 'Bonus', 'Improvement', 'Route']

def function(signature):
    start = source.index(signature)
    opening, depth = source.index('{', start), 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

wrappers = '\n'.join(function('void CvPlot::changeTemp' + kind + 'Timer(') for kind in kinds)
plot = r'''
#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <map>
#include <utility>
enum PlotNumTypes { PLOT_0, PLOT_1, PLOT_2 };
enum TerrainTypes { NO_TERRAIN = -1, TERRAIN_0, TERRAIN_1 };
enum FeatureTypes { NO_FEATURE = -1, FEATURE_0, FEATURE_1 };
enum BonusTypes { NO_BONUS = -1, BONUS_0, BONUS_1 };
enum ImprovementTypes { NO_IMPROVEMENT = -1, IMPROVEMENT_0, IMPROVEMENT_1 };
enum RouteTypes { NO_ROUTE = -1, ROUTE_0, ROUTE_1 };
class CvPlot {
    PlotNumTypes id;
public:
    TerrainTypes terrain;
    FeatureTypes feature;
    BonusTypes bonus;
    ImprovementTypes improvement;
    RouteTypes route;
    int variety, changes[5];
    explicit CvPlot(PlotNumTypes p) : id(p), terrain(TERRAIN_1), feature(FEATURE_1),
        bonus(BONUS_1), improvement(IMPROVEMENT_1), route(ROUTE_1), variety(2) {
        for (int i = 0; i < 5; ++i) changes[i] = 0;
    }
    PlotNumTypes plotNum() const { return id; }
    void setTerrainType(TerrainTypes t, bool = true, bool = true) { terrain = t; ++changes[0]; }
    void setFeatureType(FeatureTypes t, int v = -1) { feature = t; variety = v; ++changes[1]; }
    void setBonusType(BonusTypes t) { bonus = t; ++changes[2]; }
    void setImprovementType(ImprovementTypes t) { improvement = t; ++changes[3]; }
    void setRouteType(RouteTypes t, bool = true) { route = t; ++changes[4]; }
    void changeTempTerrainTimer(int, bool = true) const;
    void changeTempFeatureTimer(int, bool = true) const;
    void changeTempBonusTimer(int, bool = true) const;
    void changeTempImprovementTimer(int, bool = true) const;
    void changeTempRouteTimer(int, bool = true) const;
};
'''
core = r'''
#pragma once
#include "CvPlot.h"
class FDataStreamBase {};
template<class V> struct DefaultValue { static V get() { return static_cast<V>(-1); } };
template<> struct DefaultValue<int> { static int get() { return 0; } };
template<class E, class V, class CV = V> class ArrayEnumMap {
    std::map<E, CV> values;
public:
    V get(E key) const {
        typename std::map<E, CV>::const_iterator i = values.find(key);
        return i == values.end() ? DefaultValue<V>::get() : static_cast<V>(i->second);
    }
    void set(E key, V value) {
        if (sizeof(CV) == sizeof(short)) assert(value >= SHRT_MIN && value <= SHRT_MAX);
        values[key] = static_cast<CV>(value);
    }
    void reset() { values.clear(); }
    void read(FDataStreamBase*) {}
    void write(FDataStreamBase*) const {}
};
class PlotTempChangeMap;
struct Map {
    PlotTempChangeMap* changes;
    PlotTempChangeMap& getPlotTempChangeMap() { assert(changes); return *changes; }
};
struct Globals { Map map; Map& getMap() { return map; } };
extern Globals GC;
'''
checks = r'''
#include "CvGameCoreDLL.h"
#include "PlotTempChangeMap.h"
Globals GC;
typedef void (PlotTempChangeMap::*Setter)(CvPlot const&, int);
typedef int (PlotTempChangeMap::*Getter)(CvPlot const&) const;
typedef void (CvPlot::*Wrapper)(int, bool) const;
'''
checks += 'Setter setters[] = {' + ','.join('&PlotTempChangeMap::setTemp' + k + 'Timer' for k in kinds) + '};\n'
checks += 'Setter changers[] = {' + ','.join('&PlotTempChangeMap::changeTemp' + k + 'Timer' for k in kinds) + '};\n'
checks += 'Getter getters[] = {' + ','.join('&PlotTempChangeMap::getTemp' + k + 'Timer' for k in kinds) + '};\n'
checks += 'Wrapper wrappers[] = {' + ','.join('&CvPlot::changeTemp' + k + 'Timer' for k in kinds) + '};\n'
checks += r'''
int main() {
    PlotTempChangeMap changes;
    GC.map.changes = &changes;
    CvPlot p(PLOT_0), q(PLOT_1);
    for (int k = 0; k < 5; ++k) {
        changes.reset();
        for (int j = 0; j < 5; ++j) (changes.*setters[j])(p, 10 + j);
        (changes.*changers[k])(p, 3);
        for (int j = 0; j < 5; ++j) {
            assert((changes.*getters[j])(p) == 10 + j + (j == k ? 3 : 0));
            assert((changes.*getters[j])(q) == 0);
        }
        (p.*wrappers[k])(-2, true);
        assert((changes.*getters[k])(p) == 11 + k);
        for (int j = 0; j < 5; ++j)
            if (j != k) assert((changes.*getters[j])(p) == 10 + j);
        // Repeated -1 must decrease, not nearly double, the timer.
        (changes.*changers[k])(p, -1);
        assert((changes.*getters[k])(p) == 10 + k);
        (changes.*setters[k])(p, -1);
        assert((changes.*getters[k])(p) == 0);
        (p.*wrappers[k])(9, true); // Ignore inactive countdowns by default.
        assert((changes.*getters[k])(p) == 0);
        (p.*wrappers[k])(9, false); // Explicitly allow forwarding from zero.
        assert((changes.*getters[k])(p) == 9);
        (changes.*setters[k])(p, INT_MAX);
        assert((changes.*getters[k])(p) == SHRT_MAX);
        (changes.*changers[k])(p, INT_MAX);
        assert((changes.*getters[k])(p) == SHRT_MAX);
        (changes.*changers[k])(p, INT_MIN);
        assert((changes.*getters[k])(p) == 0);
        (changes.*setters[k])(p, SHRT_MAX - 1);
        (changes.*changers[k])(p, 1);
        assert((changes.*getters[k])(p) == SHRT_MAX);
        (changes.*changers[k])(p, -SHRT_MAX);
        assert((changes.*getters[k])(p) == 0);
        (changes.*setters[k])(p, INT_MIN);
        assert((changes.*getters[k])(p) == 0);
    }
    // Compile/exercise the actual feature overloads and the existing expiry loop.
    changes.reset();
    changes.setRealTerrainType(p, TERRAIN_0);
    changes.setRealFeatureType(p, FEATURE_0, 7);
    changes.setRealBonusType(p, BONUS_0);
    changes.setRealImprovementType(p, IMPROVEMENT_0);
    changes.setRealRouteType(p, ROUTE_0);
    changes.setTempTerrainType(p, TERRAIN_1);
    changes.setTempFeatureType(p, FEATURE_1, 2);
    changes.setTempBonusType(p, BONUS_1);
    changes.setTempImprovementType(p, IMPROVEMENT_1);
    changes.setTempRouteType(p, ROUTE_1);
    for (int k = 0; k < 5; ++k) (changes.*setters[k])(p, k + 1);
    assert(changes.getTempTerrainTimer(p) == 1 && changes.getTempFeatureTimer(p) == 2);
    for (int tick = 1; tick <= 6; ++tick) {
        changes.update(p);
        for (int k = 0; k < 5; ++k) {
            assert((changes.*getters[k])(p) == std::max(0, k + 1 - tick));
            assert(p.changes[k] == (tick >= k + 1 ? 1 : 0));
        }
    }
    assert(p.terrain == TERRAIN_0 && p.feature == FEATURE_0 && p.variety == 7);
    assert(p.bonus == BONUS_0 && p.improvement == IMPROVEMENT_0 && p.route == ROUTE_0);
    changes.reset();
    for (int k = 0; k < 5; ++k) assert((changes.*getters[k])(p) == 0);
    return 0;
}
'''
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    (tmp / 'CvPlot.h').write_text(plot)
    (tmp / 'CvGameCoreDLL.h').write_text(core)
    for name in ['PlotTempChangeMap.h', 'PlotTempChangeMap.cpp']:
        (tmp / name).write_text((root / 'CvGameCoreDLL' / name).read_text())
    (tmp / 'wrappers.cpp').write_text('#include "CvGameCoreDLL.h"\n#include "PlotTempChangeMap.h"\n' + wrappers)
    (tmp / 'checks.cpp').write_text(checks)
    command = ['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-pedantic',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g',
               str(tmp / 'PlotTempChangeMap.cpp'), str(tmp / 'wrappers.cpp'),
               str(tmp / 'checks.cpp'), '-o', str(tmp / 'checks')]
    subprocess.run(command, check=True)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0')
    subprocess.run([str(tmp / 'checks')], check=True, env=env)
print('PASS: actual map/header and five timer wrappers; C++03 + ASan/UBSan (engine/enum-map stubs).')
