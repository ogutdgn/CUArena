#include "core/TileGrid.h"

#include <algorithm>

namespace mw {

namespace {
int ceilDiv(long a, long b) { return static_cast<int>((a + b - 1) / b); }
}  // namespace

TileGrid::TileGrid(long docWidthTwips, long docHeightTwips, long tileTwips)
    : docWidthTwips_(docWidthTwips),
      docHeightTwips_(docHeightTwips),
      tileTwips_(tileTwips),
      columns_(ceilDiv(docWidthTwips, tileTwips)),
      rows_(ceilDiv(docHeightTwips, tileTwips)) {}

std::vector<TileIndex> TileGrid::tilesIntersecting(const TwipRect& rect) const {
    if (rect.isEmpty()) {
        return {};
    }
    const long lastX = rect.x + rect.width - 1;
    const long lastY = rect.y + rect.height - 1;
    const int colMin = static_cast<int>(rect.x / tileTwips_);
    const int rowMin = static_cast<int>(rect.y / tileTwips_);
    // Clamp the far edge to the grid so a rect spilling past the document never emits
    // an out-of-range tile.
    const int colMax = std::min(static_cast<int>(lastX / tileTwips_), columns_ - 1);
    const int rowMax = std::min(static_cast<int>(lastY / tileTwips_), rows_ - 1);

    std::vector<TileIndex> out;
    for (int r = rowMin; r <= rowMax; ++r) {
        for (int c = colMin; c <= colMax; ++c) {
            out.push_back(TileIndex{c, r});
        }
    }
    return out;
}

std::vector<TileIndex> TileGrid::allTiles() const {
    std::vector<TileIndex> out;
    out.reserve(static_cast<size_t>(columns_) * rows_);
    for (int r = 0; r < rows_; ++r) {
        for (int c = 0; c < columns_; ++c) {
            out.push_back(TileIndex{c, r});
        }
    }
    return out;
}

}  // namespace mw
