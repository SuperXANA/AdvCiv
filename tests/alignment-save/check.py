#!/usr/bin/env python3
"""Extract actual alignment stream blocks; host stream bytes, no engine/DLL claim."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
player = (root / 'CvGameCoreDLL/CvPlayer.cpp').read_text()
score = (root / 'CvGameCoreDLL/AlignmentScore.cpp').read_text()
structs = (root / 'CvGameCoreDLL/CvStructs.cpp').read_text()

def method(source, signature):
    start = source.index(signature)
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

def player_block(kind):
    start = player.index('void CvPlayer::' + kind + '(')
    marker = '// XANA: 02-14-2026 FfH Faction Alignment for Advanced Civ'
    start = player.index(marker, start) + len(marker)
    return player[start:player.index(marker, start)]

header = (root / 'CvGameCoreDLL/CvStructs.h').read_text()
start = header.index('struct AlignmentValue')
value = header[start:header.index('};', start) + 2]
code = r'''
#include <algorithm>
#include <vector>
#include <utility>
#include <climits>
#include <cassert>
#include <cstring>
typedef unsigned int uint;
#define MAX_INT INT_MAX
#define PROFILE_FUNC()
struct FDataStreamBase {
    std::vector<char> data;
    size_t pos;
    FDataStreamBase() : pos(0) {}
    template<class T> void Write(T v) {
        char const* p = reinterpret_cast<char const*>(&v);
        data.insert(data.end(), p, p + sizeof(T));
    }
    template<class T> void Read(T* v) {
        assert(pos + sizeof(T) <= data.size());
        std::memcpy(v, &data[pos], sizeof(T));
        pos += sizeof(T);
    }
};
'''
code += value + '\n#include "AlignmentScore.h"\n'
for signature in ['void AlignmentValue::read(', 'void AlignmentValue::write(']:
    code += method(structs, signature) + '\n'
for signature in ['void AlignmentScore::read(', 'void AlignmentScore::write(']:
    code += method(score, signature) + '\n'
code += r'''
enum AlignmentFactionTypes { NO_FACTION = -1, FACTION_A, FACTION_B, FACTION_C };
struct CvPlayer {
    std::vector<AlignmentScore> m_aAlignmentAxisScores;
    std::vector<AlignmentFactionTypes> m_aAlignmentAxisFactions;
    AlignmentFactionTypes m_eAlignmentFaction;
    void read(FDataStreamBase*);
    void write(FDataStreamBase*);
};
'''
code += 'void CvPlayer::read(FDataStreamBase* pStream) {\n' + player_block('read') + '\n}\n'
code += 'void CvPlayer::write(FDataStreamBase* pStream) {\n' + player_block('write') + '\n}\n'
code += r'''
int main() {
    int cases = 0;
    for (int axes = 0; axes <= 4; ++axes)
    for (int factions = 0; factions <= 3; ++factions)
    for (int selected = -1; selected <= 2; ++selected)
    for (int head = 0; head < 10; ++head)
    for (int count = 0; count <= 10; ++count) {
        FDataStreamBase encoded;
        encoded.Write(static_cast<uint>(axes));
        for (int axis = 0; axis < axes; ++axis) {
            encoded.Write(head);
            encoded.Write(count);
            encoded.Write(axis == 0 ? INT_MIN : axis * 17);
            encoded.Write(axis == 0 ? INT_MAX : -axis * 23);
            for (int slot = 0; slot < 10; ++slot) {
                encoded.Write(1000 * axis + slot);
                encoded.Write(-2000 * axis - slot);
            }
        }
        encoded.Write(static_cast<uint>(factions));
        for (int f = 0; f < factions; ++f) encoded.Write(f);
        encoded.Write(selected);
        uint const sentinel = 0x1234abcd;
        encoded.Write(sentinel);
        CvPlayer loaded;
        // Actual read blocks must replace previously populated vectors.
        loaded.m_aAlignmentAxisScores.resize(7);
        loaded.m_aAlignmentAxisFactions.resize(7, FACTION_C);
        loaded.m_eAlignmentFaction = FACTION_C;
        loaded.read(&encoded);
        assert(loaded.m_aAlignmentAxisScores.size() == static_cast<size_t>(axes));
        assert(loaded.m_aAlignmentAxisFactions.size() == static_cast<size_t>(factions));
        for (int f = 0; f < factions; ++f) assert(loaded.m_aAlignmentAxisFactions[f] == f);
        assert(loaded.m_eAlignmentFaction == selected);
        uint tail;
        encoded.Read(&tail);
        assert(tail == sentinel && encoded.pos == encoded.data.size());
        FDataStreamBase rewritten;
        loaded.write(&rewritten);
        assert(rewritten.data.size() + sizeof(sentinel) == encoded.data.size());
        assert(std::equal(rewritten.data.begin(), rewritten.data.end(), encoded.data.begin()));
        ++cases;
    }
    assert(cases == 8800);
}
'''
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    (tmp / 'AlignmentScore.h').write_text((root / 'CvGameCoreDLL/AlignmentScore.h').read_text())
    (tmp / 'check.cpp').write_text(code)
    subprocess.run(['g++', '-std=c++03', '-Wall', '-Wextra', '-Werror', '-Wno-reorder',
                    '-pedantic', '-fsanitize=address,undefined', '-g', str(tmp / 'check.cpp'),
                    '-o', str(tmp / 'check')], check=True)
    subprocess.run([str(tmp / 'check')], check=True,
                   env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0', UBSAN_OPTIONS='halt_on_error=1'))
print('PASS: 8800 actual alignment stream-block round trips, host bytes; C++03/ASan/UBSan.')
