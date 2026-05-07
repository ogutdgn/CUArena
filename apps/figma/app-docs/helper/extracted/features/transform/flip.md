# Flip horizontal / vertical

- **Category:** transform
- **One-line summary:** Mirror a layer (or selection set) across its horizontal or vertical axis.

## Triggers
- Right-sidebar Position section: Flip horizontal button + Flip vertical button (icons in the Position row).
- Keyboard: `Shift H` (flip horizontal) / `Shift V` (flip vertical) in common editor conventions — corpus doesn't explicitly list these shortcuts, but they are standard.
- Right-click → Transform → Flip horizontal / Flip vertical (context menu path).

## Preconditions
- Selection is non-empty.

## Inputs
- Just the trigger (button click / shortcut).

## Behavior
1. Compute the selection's bounding box center.
2. Negate the relevant scale axis (x for horizontal flip, y for vertical flip) for each selected layer, reflecting around the group center.
3. Commit.

## Outputs
- **Scene graph changes:** selected layers' transform updated (either via a `scaleX: -1` / `scaleY: -1` flag, or by baking the flip into path data — engine decision).
- **Selection changes:** none.

## UI feedback
- Canvas: layers mirror instantly.
- Right-panel values (X/Y/W/H/rotation) may update if the flip is baked into geometry.

## Side effects
- Undo stack: one entry per flip.

## Related UI schema entries
- `regions/right-properties.md` → position-section (Flip horizontal + Flip vertical buttons)

## Semantic event(s) candidate
- `flip_layer { layer_ids: [...], axis: "horizontal" | "vertical", trigger: "panel_button" | "shortcut" | "context_menu" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Representation of flip in the data model (transform flag vs baked geometry) is an engine decision (`plan/03`). Preserve enough information to round-trip the operation (undoable).
- Whether rotation "sticks" through a flip (flip then rotate vs rotate then flip differ) is standard transform semantics; keep consistent order at build time.
