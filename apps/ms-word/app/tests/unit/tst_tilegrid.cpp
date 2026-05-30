#include <QtTest/QtTest>

#include <vector>

#include "core/TileGrid.h"

using mw::TileGrid;
using mw::TileIndex;
using mw::TwipRect;

namespace {
// A 4x4 grid: 256px tiles at 100% / 96dpi = 3840 twips; document = 15360 x 15360 twips.
constexpr long kTile = 3840;
constexpr long kDoc = 4 * kTile;  // 15360
}  // namespace

class TestTileGrid : public QObject {
    Q_OBJECT
private slots:
    // A small edit's dirty rect must map to ONLY the tile it touches — never the whole
    // grid. This is the anti-full-repaint guarantee, at the geometry level.
    void smallRect_returnsOnlyContainingTile() {
        TileGrid grid(kDoc, kDoc, kTile);
        QCOMPARE(grid.columns(), 4);
        QCOMPARE(grid.rows(), 4);

        // A 100x100 twip dirty rect well inside tile (col=1, row=1).
        const auto tiles = grid.tilesIntersecting(TwipRect{4000, 4000, 100, 100});

        const std::vector<TileIndex> expected{{1, 1}};
        QVERIFY2(tiles == expected,
                 qPrintable(QStringLiteral("expected exactly tile (1,1), got %1 tile(s)")
                                .arg(tiles.size())));
    }

    // A dirty rect that straddles a tile boundary must repaint both tiles it touches.
    void rectSpanningBoundary_returnsBothTiles() {
        TileGrid grid(kDoc, kDoc, kTile);
        // x in [3800, 3900) crosses the col 0/1 boundary at 3840; y in [4000,4050) is row 1.
        const auto tiles = grid.tilesIntersecting(TwipRect{3800, 4000, 100, 50});
        const std::vector<TileIndex> expected{{0, 1}, {1, 1}};
        QVERIFY2(tiles == expected,
                 qPrintable(QStringLiteral("expected tiles (0,1),(1,1); got %1 tile(s)")
                                .arg(tiles.size())));
    }

    // An empty dirty rect touches nothing — repaint zero tiles.
    void emptyRect_returnsNoTiles() {
        TileGrid grid(kDoc, kDoc, kTile);
        QVERIFY(grid.tilesIntersecting(TwipRect{4000, 4000, 0, 0}).empty());
    }

    // The legitimate whole-document repaint (load / zoom change): every tile, row-major.
    void allTiles_coversWholeGridRowMajor() {
        TileGrid grid(kDoc, kDoc, kTile);
        const auto tiles = grid.allTiles();
        QCOMPARE(static_cast<int>(tiles.size()), 16);
        QCOMPARE(tiles.front(), (TileIndex{0, 0}));
        QCOMPARE(tiles.back(), (TileIndex{3, 3}));
    }

    // A dirty rect spilling past the document edge must clamp to the grid — never emit
    // an out-of-range tile (col 4 in a 4-wide grid).
    void rectBeyondDocEdge_clampsToGrid() {
        TileGrid grid(kDoc, kDoc, kTile);
        const auto tiles = grid.tilesIntersecting(TwipRect{14000, 14000, 5000, 5000});
        const std::vector<TileIndex> expected{{3, 3}};
        QVERIFY2(tiles == expected,
                 qPrintable(QStringLiteral("expected clamped tile (3,3); got %1 tile(s)")
                                .arg(tiles.size())));
    }
};

QTEST_GUILESS_MAIN(TestTileGrid)
#include "tst_tilegrid.moc"
