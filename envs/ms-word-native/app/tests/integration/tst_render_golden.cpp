// Type-C test: render a real fixture through the binding + RenderController (the same
// TileGrid/TileCache render path the A-tests exercise, now backed by the REAL LOK engine), and
// assert the rendered tile holds REAL laid-out content — never a blank page, never "did not
// crash". Plain C++ (no Qt). CMake injects MW_LOK_INSTDIR and MW_FIXTURE_FODT.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>

#include "core/RenderController.h"
#include "engine/LokEngine.h"

namespace {
int g_fail = 0;
std::string fileUrl(const char* p) { return std::string("file://") + p; }
void check(bool c, const char* w) {
    std::fprintf(stderr, "%s: %s\n", c ? "ok " : "FAIL", w);
    if (!c) ++g_fail;
}
constexpr long kTileTwip = 3840;  // 256 px tile at 100% / 96dpi
constexpr int kPx = 256;
// Committed golden: FNV-1a of the rendered top-left tile of sample.fodt at 100% on the pinned
// (bundled-font, svp, release) engine build. Byte-stable across runs.
constexpr std::uint64_t kGoldenHash = 0x9abaffb323ecb275ULL;

// FNV-1a over the tile bytes — a stable content fingerprint for the golden frame.
std::uint64_t hash64(const mw::TileCache::Bytes& b) {
    std::uint64_t h = 1469598103934665603ULL;
    for (std::uint8_t x : b) { h ^= x; h *= 1099511628211ULL; }
    return h;
}
}  // namespace

int main() {
    mw::LokEngine eng;
    check(eng.init(MW_LOK_INSTDIR, "file:///tmp/mw-lok-profile-c"), "LOK init");
    if (g_fail) { std::fflush(stderr); std::_Exit(2); }
    check(eng.loadDocument(fileUrl(MW_FIXTURE_FODT)), "load fixture");

    // Drive the real engine through the our-layer render path.
    mw::RenderController rc(eng, kTileTwip);
    const mw::TileCache::Bytes& tile = rc.ensureTile(mw::TileIndex{0, 0}, 100);

    check(tile.size() == static_cast<std::size_t>(kPx) * kPx * 4, "tile is 256x256 BGRA (P*P*4)");

    // Real content: count opaque, non-near-white pixels. The fixture's first paragraph lands in
    // the top-left tile, so text must render dark ink there. A blank page would score 0.
    long ink = 0;
    for (std::size_t i = 0; i + 3 < tile.size(); i += 4) {
        const std::uint8_t b = tile[i], g = tile[i + 1], r = tile[i + 2], a = tile[i + 3];
        if (a > 10 && (r < 180 || g < 180 || b < 180)) ++ink;
    }
    std::fprintf(stderr, "  ink pixels: %ld   tile-hash: %016llx\n", ink,
                 static_cast<unsigned long long>(hash64(tile)));
    check(ink > 100, "rendered tile holds REAL text content (not a blank page)");
    check(hash64(tile) == kGoldenHash, "rendered tile matches the committed golden frame");

    std::fprintf(stderr, "%s\n", g_fail ? "C-TEST FAILED" : "C-TEST PASSED");
    std::fflush(stderr);
    std::_Exit(g_fail ? 1 : 0);
}
