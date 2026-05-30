#include <QtTest/QtTest>

#include <cstdint>
#include <vector>

#include "core/RenderController.h"
#include "core/RenderEngine.h"

namespace {
constexpr long kTile = 3840;        // 256px @ 100%/96dpi
constexpr long kDoc = 4 * kTile;    // 4x4 tile document

// Fake engine that records every paintTile call (one call == one repaint).
class FakeEngine : public mw::IRenderEngine {
public:
    std::vector<mw::TwipRect> painted;

    mw::TwipRect documentSize() const override { return mw::TwipRect{0, 0, kDoc, kDoc}; }

    mw::TileCache::Bytes paintTile(const mw::TwipRect& r, int, int) override {
        painted.push_back(r);
        return mw::TileCache::Bytes{static_cast<std::uint8_t>(r.x / kTile),
                                    static_cast<std::uint8_t>(r.y / kTile)};
    }
};
}  // namespace

class TestRenderController : public QObject {
    Q_OBJECT
private slots:
    // A tile is painted once on a cache miss; requesting it again is a cache hit — the
    // engine is NOT asked to repaint a second time.
    void ensureTile_paintsOnMiss_hitsOnRepeat() {
        FakeEngine engine;
        mw::RenderController rc(engine, kTile);

        rc.ensureTile(mw::TileIndex{1, 0}, 100);
        rc.ensureTile(mw::TileIndex{1, 0}, 100);

        QCOMPARE(static_cast<int>(engine.painted.size()), 1);
    }

    // The whole point of the render path: after a small edit, re-rendering the viewport
    // repaints ONLY the invalidated tile; every other tile is served from cache. A
    // full-repaint regression would paint all 4 again.
    void edit_repaintsOnlyDirtyTile_restStayCached() {
        FakeEngine engine;
        mw::RenderController rc(engine, kTile);

        // Render a 2x2 viewport (tiles (0,0),(1,0),(0,1),(1,1)) at 100%.
        for (int r = 0; r < 2; ++r)
            for (int c = 0; c < 2; ++c) rc.ensureTile(mw::TileIndex{c, r}, 100);
        QCOMPARE(static_cast<int>(engine.painted.size()), 4);

        // A small edit dirties only tile (col=1,row=0): a 50x50 twip rect inside it.
        rc.invalidate(mw::TwipRect{kTile + 100, 100, 50, 50});

        // Re-render the same viewport: exactly one more paint (the dirty tile), 3 cache hits.
        for (int r = 0; r < 2; ++r)
            for (int c = 0; c < 2; ++c) rc.ensureTile(mw::TileIndex{c, r}, 100);
        QCOMPARE(static_cast<int>(engine.painted.size()), 5);
    }
};

QTEST_GUILESS_MAIN(TestRenderController)
#include "tst_rendercontroller.moc"
