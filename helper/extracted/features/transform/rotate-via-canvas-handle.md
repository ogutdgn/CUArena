# Rotate via canvas handle

- **Category:** transform
- **One-line summary:** Rotate selected layer(s) by hovering near a corner of the bounding box (until the rotate cursor appears) and dragging.

## Triggers
- Selection non-empty.
- Pointer hover just **outside** a corner of the layer's bounds → rotate cursor.
- Click and drag.

## Preconditions
- A layer is selected.

## Inputs
- Pointer drag from outside a corner.
- Modifier: `Shift` — snap rotation in 15° increments.

## Behavior
1. Engine reads pointer angle relative to selection center (or custom rotation origin — see `change-rotation-origin.md`).
2. Continuously updates rotation as pointer moves.
3. Direction: **clockwise** drag → negative angle (toward -180°). **Counterclockwise** → positive.
4. Past 180° in either direction, value wraps to the opposite signed value (e.g. 195° → -165°).
5. Effects on the layer are NOT rotated (per `adjust-alignment-rotation-position-and-dimensions`).

## Outputs
- **Scene graph changes:** layer's `rotation` updated.
- **Selection changes:** none.

## UI feedback
- Rotate cursor near corners.
- Live tooltip shows current angle during drag.
- Right sidebar rotation field updates live.

## Side effects
- Undo stack: one entry per drag commit.

## Related UI schema entries
- `regions/canvas-overlays.md` → rotation-cursor + angle-tooltip
- `regions/right-properties.md` → position-section → rotation field

## Semantic event(s) candidate
- `rotate_layer { layer_ids, from_rotation, to_rotation, modifiers: { shift }, trigger: "canvas_drag" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Effects (drop shadow, etc.) don't rotate with the layer; that's a documented Figma quirk.
