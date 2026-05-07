# Shift-click — add to selection

- **Category:** selection
- **One-line summary:** Add a layer to the current selection by holding `Shift` while clicking it.

## Triggers
- `Shift` + pointer click on a layer not in the current selection (canvas or layers panel).

## Preconditions
- Move tool is active.
- There is already a current selection OR current selection is empty (in the latter case this behaves like `click-select`).
- Clicked layer is not locked (or is accessible via nested click).

## Inputs
- Pointer coordinates.
- `Shift` modifier held.

## Behavior
1. Hit-test at pointer position.
2. If a layer is hit AND not already in the selection: add its id to the selection list.
3. If a layer is hit AND already in the selection: this is `shift-click-remove-from-selection` — see separate file.
4. If empty canvas is hit: no-op (selection unchanged).
5. Multi-selection bounding box updates to encompass the union.
6. Right-sidebar updates per mixed-selection rules.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** layer id appended to selection list.

## UI feedback
- Canvas: union bounding box redraws.
- Left panel: additional row highlighted.
- Right panel: may switch to mixed-selection view (see `state-matrix.md`).

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → multi-selection-bounding-box
- `state-matrix.md` → Multi-mixed selection row

## Semantic event(s) candidate
- `shift_click_add_selection { target_layer_id, pointer: {x, y}, source: "canvas" | "layers_panel" }`

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- None.
