#pragma once

#include <cstddef>
#include <cstdint>
#include <map>
#include <vector>

#include "core/TileGrid.h"  // TileIndex

namespace mw {

// A cached tile is identified by its grid position AND the zoom it was rendered at —
// the same document region is cached separately per zoom level.
struct TileKey {
    TileIndex tile;
    int zoomPercent = 100;

    bool operator<(const TileKey& o) const {
        if (!(tile == o.tile)) {
            return tile < o.tile;
        }
        return zoomPercent < o.zoomPercent;
    }
};

// Caches rendered tile buffers so the render path repaints only invalidated tiles rather
// than re-rendering the whole document each frame. Pure logic — the payload is opaque
// bytes (an RGBA tile buffer in production); this class owns only the caching policy.
//
// On a document edit the LOK INVALIDATE_TILES dirty rect maps (via TileGrid) to a set of
// dirty tiles; invalidate() drops exactly those — at every cached zoom — and leaves the
// rest hot. A cache that dropped everything (or nothing) would defeat the dirty-rect
// render path, which is the "dead tile cache" failure the audit flagged.
class TileCache {
public:
    using Bytes = std::vector<std::uint8_t>;

    void put(const TileKey& key, Bytes bytes);

    // Pointer to the cached bytes on a hit, nullptr on a miss.
    const Bytes* get(const TileKey& key) const;

    bool contains(const TileKey& key) const { return get(key) != nullptr; }
    std::size_t size() const { return entries_.size(); }

    // Drop every cached entry whose tile position is in `dirtyTiles`, regardless of the
    // zoom it was rendered at (a document edit invalidates that region at all zooms).
    void invalidate(const std::vector<TileIndex>& dirtyTiles);

private:
    std::map<TileKey, Bytes> entries_;
};

}  // namespace mw
