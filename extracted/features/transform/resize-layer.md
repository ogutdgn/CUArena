# Resize layer

- **Category:** transform
- **One-line summary:** Change a layer's width and/or height by dragging bounding-box handles or editing W/H inputs.

## Triggers
- Pointer drag on a corner or mid-edge handle of the selection bounding box.
- Right-sidebar Layout section: type a new value into W or H input + Enter.
- Right-sidebar lock-aspect toggle: when locked, editing one dimension scales the other proportionally.

## Preconditions
- Selection is non-empty.
- For drag path: Move tool active, bounding box visible, pointer-down on a handle.

## Inputs
- Drag: pointer delta while the handle is being dragged.
- Panel: typed numeric value.
- Modifiers during drag:
  - `Shift` — preserve aspect ratio.
  - `Alt/Option` — resize from center (both opposing edges move symmetrically).

## Behavior

**Drag path:**
1. Pointer-down on handle: record initial bounds + which handle is grabbed.
2. Pointer-move: update W / H based on handle and pointer delta.
3. Apply modifiers: Shift locks aspect, Alt mirrors across the opposite anchor.
4. Live W×H label updates.
5. Red snap / measure guides may appear if edges align with siblings.
6. Pointer-up: commit.

**Panel path:**
1. Edit W or H input.
2. Enter: apply new dimension. If lock-aspect is on, the complementary dimension scales proportionally.

## Outputs
- **Scene graph changes:** selected layer's `w` and/or `h` updated; dependent properties (stroke thickness, children if frame) not scaled (resize is distinct from scale).
- **Selection changes:** none.

## UI feedback
- Handles follow the pointer; W×H label updates live.
- Panel values reflect new dimensions.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → layout-section (W, H, lock-aspect)
- `regions/canvas-overlays.md` → selection-bounding-box (corner + edge handles)

## Semantic event(s) candidate
- `resize_layer { layer_ids: [...], handle: "tl" | "tr" | "bl" | "br" | "top" | "bottom" | "left" | "right" | "w_input" | "h_input", from: {w, h}, to: {w, h}, modifiers: { shift_aspect_lock, alt_center }, trigger: "drag_handle" | "panel_input" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Resize behavior for text layers differs (auto-fit vs fixed); covered implicitly by text-resizing modes (`visual-only` in our scope — covered in `text/` specs).
- Negative W / H (flipping by dragging a handle past the opposite edge) — documented behavior in many editors; corpus doesn't detail, but default is "allow flip via negative scale".
