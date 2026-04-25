# Click select

- **Category:** selection
- **One-line summary:** Select a single layer by clicking on it, or deselect everything by clicking on empty canvas.

## Triggers
- Pointer click on a layer on the canvas (Move tool active).
- Pointer click on a row in the Layers panel.

## Preconditions
- Move tool is active (or Hand tool + no drag — then Hand takes over for pan).
- Not in text-edit mode, vector-edit mode, or a tool that creates layers on click.

## Inputs
- Pointer coordinates (canvas space).
- OR layer row click (layer panel).

## Behavior
1. Hit-test at pointer position. Resolve the topmost layer whose bounds contain the point (respecting lock state — locked layers are not selectable unless `Cmd/Ctrl + click`).
2. If a layer is hit: replace selection with `[hit_layer_id]`. Select the topmost non-locked layer by default. To dig into nested children, double-click to enter the parent group/frame, then click.
3. If empty canvas is hit: clear selection.
4. Right-sidebar swaps to selection-aware sections or to the no-selection state.
5. Bounding box + handles + W×H label render around the selected layer (or disappear on deselect).

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** replaced with single layer (or cleared).

## UI feedback
- Canvas: bounding box + handles appear around the newly-selected layer, or disappear if empty canvas clicked.
- Right panel: sections update per `state-matrix.md`.
- Left panel (Layers tree): the corresponding row is highlighted; ancestors auto-expand so the row is visible.

## Side effects
- Undo stack: no entry (selection is not undoable in real Figma).
- Focus: canvas retains focus.

## Related UI schema entries
- `regions/canvas-overlays.md` → selection-bounding-box
- `regions/left-navigation.md` → layers-tree (highlighted row)
- `regions/right-properties.md` (all selection-driven sections)
- `state-matrix.md`

## Semantic event(s) candidate
- `click_select { target_layer_id | null, pointer: {x, y}, source: "canvas" | "layers_panel" }`
- null target on empty-canvas click = deselect.

## Source articles
- `select-layers-and-objects`
- `explore-design-files`

## Notes / gaps
- `Cmd/Ctrl + click` for "select inside group" / "select deeper layer" may be part of this flow or a distinct feature; corpus ambiguous. Here treated as a modifier variant of click-select; if it diverges, split in `plan/03`.
