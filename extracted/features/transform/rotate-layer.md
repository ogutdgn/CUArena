# Rotate layer

- **Category:** transform
- **One-line summary:** Rotate a selected layer (or selection set) around its center.

## Triggers
- Pointer drag in the "rotation region" — the area just outside a corner handle (cursor changes to a curved-arrow).
- Right-sidebar Position section: type a rotation value (°) into the rotation input + Enter.

## Preconditions
- Selection is non-empty.
- Drag path: pointer is near a corner, outside the bounding box — cursor has changed to the rotation glyph.

## Inputs
- Drag: pointer-down + pointer-move (angle computed from vector from selection center to pointer).
- Panel: typed numeric degree value.
- Modifiers during drag:
  - `Shift` — constrain to 15° increments.

## Behavior

**Drag path:**
1. Pointer-down near a corner outside the bounding box: record initial angle (from center to pointer).
2. Pointer-move: compute new angle; set selection rotation as delta from initial.
3. Shift snaps to 15° increments.
4. Readout near cursor shows current angle.
5. Pointer-up: commit.

**Panel path:**
1. Edit rotation input.
2. Enter: apply. For multi-selection, docs are ambiguous on anchor (individual vs group center); treat as group-center default.

## Outputs
- **Scene graph changes:** selected layer's `rotation` property updated.
- **Selection changes:** none.

## UI feedback
- Cursor becomes the rotation glyph in the corner-outside region.
- Angle readout appears near cursor during drag.
- Bounding box rotates; handles rotate with it.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → position-section (rotation input)
- `regions/canvas-overlays.md` → selection-bounding-box (rotation-cursor in corner-outside regions)

## Semantic event(s) candidate
- `rotate_layer { layer_ids: [...], from: deg, to: deg, modifiers: { shift_snap_15 }, trigger: "drag_corner_rotation" | "panel_input" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Rotation direction convention (CW positive vs CCW positive) not explicitly stated in docs; match industry convention (Figma uses CW-positive so degrees increase rotating clockwise? — needs validation at build time).
- Multi-selection rotation anchor: individual center vs group center ambiguous; default to group center.
