#include "core/RenderController.h"

namespace mw {

RenderController::RenderController(IRenderEngine& engine, long tileTwips)
    : engine_(engine),
      tileTwips_(tileTwips),
      grid_(engine.documentSize().width, engine.documentSize().height, tileTwips) {}

namespace {
TwipRect tileRect(const TileIndex& tile, long tileTwips) {
    return TwipRect{tile.col * tileTwips, tile.row * tileTwips, tileTwips, tileTwips};
}
// 1 px = 15 twips at 100% / 96dpi (a 256px tile == 3840 twips).
int tilePixels(long tileTwips, int zoomPercent) {
    return static_cast<int>(tileTwips * static_cast<long>(zoomPercent) / 100 / 15);
}
}  // namespace

const TileCache::Bytes& RenderController::ensureTile(const TileIndex& tile, int zoomPercent) {
    const TileKey key{tile, zoomPercent};
    if (const auto* hit = cache_.get(key)) {
        return *hit;
    }
    const int px = tilePixels(tileTwips_, zoomPercent);
    cache_.put(key, engine_.paintTile(tileRect(tile, tileTwips_), px, px));
    return *cache_.get(key);
}

void RenderController::invalidate(const TwipRect& dirtyTwips) {
    cache_.invalidate(grid_.tilesIntersecting(dirtyTwips));
}

}  // namespace mw
