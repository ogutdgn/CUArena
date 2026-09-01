#pragma once

#include <vector>

namespace mw {

// A tile's position in the document tile grid (col = x, row = y), addressed row-major.
struct TileIndex {
    int col = 0;
    int row = 0;

    bool operator==(const TileIndex& o) const { return col == o.col && row == o.row; }
    // Row-major ordering — deterministic comparison in tests and stable de-duplication.
    bool operator<(const TileIndex& o) const {
        return row != o.row ? row < o.row : col < o.col;
    }
};

// A rectangle in document coordinates, in twips (1 twip = 1/1440 inch). Mirrors the
// LOK_CALLBACK_INVALIDATE_TILES payload (x, y, width, height in twips).
struct TwipRect {
    long x = 0;
    long y = 0;
    long width = 0;
    long height = 0;

    bool isEmpty() const { return width <= 0 || height <= 0; }
};

// The document's tile grid: a (docWidth x docHeight)-twip document divided into square
// tiles of `tileTwips` each. Pure geometry — no engine, no toolkit.
//
// Reason to exist: turn an INVALIDATE_TILES dirty rect into the *minimal* set of tiles
// to repaint, so the render path never full-repaints on a small edit. That is the
// Phase-1 "honor the dirty rect" requirement, expressed as testable logic.
class TileGrid {
public:
    TileGrid(long docWidthTwips, long docHeightTwips, long tileTwips);

    int columns() const { return columns_; }
    int rows() const { return rows_; }
    long tileTwips() const { return tileTwips_; }

    // Tiles whose twip extent intersects `rect`, clamped to the grid, row-major sorted
    // and de-duplicated. An empty rect yields no tiles.
    std::vector<TileIndex> tilesIntersecting(const TwipRect& rect) const;

    // Every tile in the grid — the legitimate whole-document repaint (load, zoom change).
    std::vector<TileIndex> allTiles() const;

private:
    long docWidthTwips_;
    long docHeightTwips_;
    long tileTwips_;
    int columns_;
    int rows_;
};

}  // namespace mw
