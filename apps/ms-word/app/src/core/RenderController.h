#pragma once

#include "core/RenderEngine.h"
#include "core/TileCache.h"
#include "core/TileGrid.h"

namespace mw {

// Ties the tile geometry (TileGrid) and the tile cache (TileCache) to the engine seam to
// implement the dirty-rect render fast path: a tile is painted by the engine only on a
// cache miss, and an INVALIDATE_TILES rect drops exactly the tiles it touches — so a small
// edit repaints only what changed, never the whole document. This is the our-layer half of
// the Phase-1 "honor the dirty rect" render path; the engine half is the LOK binding.
class RenderController {
public:
    RenderController(IRenderEngine& engine, long tileTwips);

    // The cached bytes for `tile` at `zoomPercent`, painting via the engine only on a miss.
    const TileCache::Bytes& ensureTile(const TileIndex& tile, int zoomPercent);

    // An engine INVALIDATE_TILES rect arrived: drop exactly the tiles it intersects.
    void invalidate(const TwipRect& dirtyTwips);

    const TileGrid& grid() const { return grid_; }

private:
    IRenderEngine& engine_;
    long tileTwips_;
    TileGrid grid_;
    TileCache cache_;
};

}  // namespace mw
