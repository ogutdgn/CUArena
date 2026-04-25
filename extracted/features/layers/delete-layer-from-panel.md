# Delete layer from panel

- **Category:** layers
- **One-line summary:** Delete a layer from the scene graph using the Layers panel (as opposed to selecting on canvas and pressing Delete).

## Triggers
- Layers panel: right-click row → Delete.
- Layers panel: select row(s) + keyboard Delete / Backspace (same as canvas-selection delete — overlaps with `clipboard/delete.md` but source distinguishes).

## Preconditions
- At least one layer row is selected in the panel.

## Inputs
- Just the trigger.

## Behavior
1. Same scene-graph mutation as `clipboard/delete.md`: remove selected layers.
2. Distinguished only by `trigger.source` in the semantic event (panel vs canvas).

## Outputs
- **Scene graph changes:** selected layers removed.
- **Selection changes:** cleared.

## UI feedback
- Left panel: rows removed.
- Canvas: layers disappear.

## Side effects
- Undo stack: one entry; undo restores.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree
- `regions/floating-overlays.md` → right-click-context-menu

## Semantic event(s) candidate
- Same event name as `clipboard/delete.md`: `delete { layer_ids, trigger: "context_menu_panel" | "keyboard_from_panel" }`.
- Two distinct trigger values (`context_menu_panel` vs `context_menu`, `keyboard_from_panel` vs `keyboard_delete`) so CUA can tell panel-originated deletes from canvas-originated.

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- Semantically this is the same feature as canvas delete — the `trigger` field is what distinguishes. Maintaining separate file only because plan/02 §5 listed it; `plan/03` may collapse this into `clipboard/delete.md`.
