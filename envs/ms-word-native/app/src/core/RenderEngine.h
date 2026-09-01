#pragma once

#include "core/TileCache.h"  // TileCache::Bytes
#include "core/TileGrid.h"   // TwipRect, TileIndex

namespace mw {

// The render-relevant slice of the engine seam (Boundary A). The production implementation
// wraps LOK — documentSize() ← getDocumentSize, paintTile() ← paintTile into a tile buffer.
// Keeping it abstract lets the our-layer render orchestration (RenderController) be tested
// against a fake engine with no LOK present, then driven by the real engine in Track 3.
class IRenderEngine {
public:
    virtual ~IRenderEngine() = default;

    // Document size in twips, as (0, 0, width, height).
    virtual TwipRect documentSize() const = 0;

    // Render the document region `tileRectTwips` into a pixel buffer of `pixelW` x `pixelH`
    // (an RGBA tile in production) and return its bytes. One call == one engine repaint.
    virtual TileCache::Bytes paintTile(const TwipRect& tileRectTwips, int pixelW, int pixelH) = 0;
};

}  // namespace mw
