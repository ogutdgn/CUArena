#include "core/TileCache.h"

#include <algorithm>
#include <utility>

namespace mw {

void TileCache::put(const TileKey& key, Bytes bytes) {
    entries_[key] = std::move(bytes);
}

const TileCache::Bytes* TileCache::get(const TileKey& key) const {
    const auto it = entries_.find(key);
    return it == entries_.end() ? nullptr : &it->second;
}

void TileCache::invalidate(const std::vector<TileIndex>& dirtyTiles) {
    for (auto it = entries_.begin(); it != entries_.end();) {
        const TileIndex& tile = it->first.tile;
        const bool dirty = std::any_of(
            dirtyTiles.begin(), dirtyTiles.end(),
            [&tile](const TileIndex& d) { return d == tile; });
        if (dirty) {
            it = entries_.erase(it);
        } else {
            ++it;
        }
    }
}

}  // namespace mw
