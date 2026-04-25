# Shift-click — remove from selection

- **Category:** selection
- **One-line summary:** Remove a layer from the current selection by holding `Shift` and clicking it when it is already selected.

## Triggers
- `Shift` + pointer click on a layer that is already in the current selection.

## Preconditions
- Move tool active.
- Clicked layer is a member of the current selection.

## Inputs
- Pointer coordinates.
- `Shift` modifier held.

## Behavior
1. Hit-test at pointer position.
2. Determine that the hit layer is in the current selection.
3. Remove its id from the selection list.
4. Multi-selection bounding box updates (or disappears if only one layer was left and is now removed).
5. Right-sidebar sections update for the new selection size.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** layer id removed from selection list.

## UI feedback
- Canvas: bounding box redraws.
- Left panel: row unhighlighted.
- Right panel: may return to single-selection view.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → selection-bounding-box / multi-selection-bounding-box
- `state-matrix.md`

## Semantic event(s) candidate
- `shift_click_remove_selection { target_layer_id, pointer: {x, y}, source: "canvas" | "layers_panel" }`

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- None.
