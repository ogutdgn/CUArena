#include <QtTest/QtTest>

#include "core/TileCache.h"

using mw::TileCache;
using mw::TileIndex;
using mw::TileKey;

class TestTileCache : public QObject {
    Q_OBJECT
private slots:
    // A put tile is a hit returning its bytes; a different tile, or the same tile at a
    // different zoom, is a miss.
    void putThenGet_hits_andMissReturnsNull() {
        TileCache cache;
        const TileKey k{{2, 1}, 100};
        const TileCache::Bytes payload{0xDE, 0xAD, 0xBE, 0xEF};
        cache.put(k, payload);

        const auto* hit = cache.get(k);
        QVERIFY(hit != nullptr);
        QVERIFY(*hit == payload);

        QVERIFY(cache.get(TileKey{{0, 0}, 100}) == nullptr);   // different tile
        QVERIFY(cache.get(TileKey{{2, 1}, 200}) == nullptr);   // same tile, other zoom
        QCOMPARE(static_cast<int>(cache.size()), 1);
    }

    // A document edit dirties a tile: that tile is dropped at EVERY cached zoom, and only
    // that tile — its neighbours stay hot so the render path repaints just the dirty one.
    void invalidate_dropsOnlyDirtyTiles_acrossAllZooms() {
        TileCache cache;
        cache.put(TileKey{{0, 0}, 100}, TileCache::Bytes{1});
        cache.put(TileKey{{1, 0}, 100}, TileCache::Bytes{2});
        cache.put(TileKey{{2, 0}, 100}, TileCache::Bytes{3});
        cache.put(TileKey{{1, 0}, 200}, TileCache::Bytes{4});  // same tile, other zoom
        QCOMPARE(static_cast<int>(cache.size()), 4);

        cache.invalidate(std::vector<TileIndex>{TileIndex{1, 0}});

        QVERIFY(cache.get(TileKey{{1, 0}, 100}) == nullptr);  // dropped at 100%
        QVERIFY(cache.get(TileKey{{1, 0}, 200}) == nullptr);  // and at 200%
        QVERIFY(cache.contains(TileKey{{0, 0}, 100}));        // neighbour survives
        QVERIFY(cache.contains(TileKey{{2, 0}, 100}));        // neighbour survives
        QCOMPARE(static_cast<int>(cache.size()), 2);
    }
};

QTEST_GUILESS_MAIN(TestTileCache)
#include "tst_tilecache.moc"
