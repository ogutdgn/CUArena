# Snap to objects (and pixel grid)

- **Category:** transform
- **One-line summary:** When dragging or resizing a layer, snap to alignment with other layers' centers and edges; red guide lines indicate snap targets.

## Triggers
- Active drag / resize / vector-point drag.
- Pre-condition: snap settings enabled (Snap to objects / Snap to geometry / Snap to pixel grid).

## Preconditions
- Snap setting enabled in Preferences (per `adjust-alignment-rotation-position-and-dimensions`).

## Inputs
- Pointer drag.
- Modifier: hold `⌃ Control` to temporarily disable snap.

## Behavior
1. **Snap to objects** — snaps to centers and outermost points of other objects.
2. **Snap to geometry** — vector-edit-mode only; snap vector points to other vector points.
3. **Snap to pixel grid** — snap to integer pixel boundaries (works even when pixel grid not visible).
4. Red guide lines appear during drag to indicate which target is being snapped to.
5. **`⌃ Control` modifier** disables snap-to-objects / snap-to-geometry temporarily.
6. To temporarily disable snap-to-pixel-grid, must be in vector edit mode and zoomed in.

## Outputs
- **Scene graph changes:** drag/resize result snaps to a snapped position.
- **Selection changes:** none.

## UI feedback
- Red snap-guide lines on canvas.
- Position snaps to integer or alignment value.

## Side effects
- Undo stack: standard per-drag.

## Related UI schema entries
- `regions/canvas-overlays.md` → snap-guides

## Semantic event(s) candidate
- `snap_during_drag { axis: "x" | "y", snap_target_layer_id?, snap_target_kind: "edge" | "center" | "pixel_grid" | "geometry" }`
- (Typically silent unless logger is interested.)

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Settings live under file menu → Preferences. In mock, treat as default-on for snap-to-objects and snap-to-pixel-grid.
