# Move layer

- **Category:** transform
- **One-line summary:** Reposition a selected layer (or selection set) on the canvas.

## Triggers
- Pointer drag on a selected layer (Move tool active).
- Arrow keys — `← → ↑ ↓` — nudge selection by 1 unit; `Shift + arrow` = 10 units (default nudge amounts; customizable in preferences).
- Right-sidebar Position section: type a new value into X or Y input + Enter.

## Preconditions
- Selection is non-empty.
- For drag path: Move tool active, pointer-down started on a selected layer (or any layer, which also selects it).
- For keyboard path: canvas has focus, no modal / text-edit active.
- For panel path: cursor in the X or Y input.

## Inputs
- Drag: pointer delta (dx, dy).
- Keyboard: arrow-key key + optional Shift.
- Panel: typed numeric value.
- Modifiers during drag:
  - `Shift` — constrain movement to horizontal / vertical axis (whichever has larger delta).
  - `Alt/Option` — duplicate while dragging (creates a copy of the selection and moves it; original stays in place).

## Behavior

**Drag path:**
1. Pointer-down on selected layer: record initial positions of all selected layers.
2. Pointer-move: translate every selected layer's position by (current - start) delta; apply constraint if `Shift`.
3. Red snap-guides appear when edges / centers align with sibling layers' edges / centers.
4. Pointer-up: commit the new positions. Single undo entry for the move.

**Keyboard path:**
1. On arrow key: translate selection by nudge amount; commit immediately (each press = one undo entry, or coalesced if pressed rapidly — `plan/03` decision).

**Panel path:**
1. Edit X or Y input.
2. On Enter: set the respective coordinate on the selection (multi-selection may edit anchor or the selection bounding box origin — engine decision).

## Outputs
- **Scene graph changes:** each selected layer's `x` and/or `y` updated.
- **Selection changes:** none (same layers remain selected).

## UI feedback
- Drag: live position update; red snap / measure guides appear while dragging; W×H label stays attached to the selection.
- Keyboard: instant visual jump.
- Panel: value committed; canvas updates.

## Side effects
- Undo stack: one entry per commit (single drag = single entry; each arrow-key press = one entry or coalesced batch).
- Clipboard: untouched.

## Related UI schema entries
- `regions/right-properties.md` → position-section (X / Y inputs)
- `regions/canvas-overlays.md` → selection-bounding-box, snap-and-measure-guides

## Semantic event(s) candidate
- `move_layer { layer_ids: [...], delta: { dx, dy }, trigger: "drag" | "arrow_key" | "panel_input", modifiers: { shift_constrain, alt_duplicate } }`
- "Alt-duplicate" produces a different semantic event (`duplicate_by_drag`?) since it also creates layers — `plan/03` decides whether to split.

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
- `select-layers-and-objects`

## Notes / gaps
- Default nudge amount: 1px base / 10px with Shift (common defaults). Customizable in Preferences, but customization is `visual-only` for our mock.
- Alt-duplicate is critical for CUA trajectory testing (drag vs duplicate-drag). Must be captured distinctly in the logger.
