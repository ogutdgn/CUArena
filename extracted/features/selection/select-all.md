# Select all

- **Category:** selection
- **One-line summary:** Select every layer on the current page (or within the current parent context).

## Triggers
- Keyboard: `Cmd A` (Mac) / `Ctrl A` (Windows) with canvas focused.
- Edit menu / right-click → Select all (if surfaced in context menu).

## Preconditions
- Canvas has focus (not a text field / input).
- At least one layer exists on the current page (else no-op).

## Inputs
- None beyond trigger.

## Behavior
1. Determine the current context:
   - If no layer is selected and cursor is on canvas: select all top-level layers on the current page.
   - If currently inside a group / frame (entered via double-click): select all children of that group / frame at the current nesting level.
2. Update selection to the computed list.
3. Right-sidebar + canvas update per multi-selection rules.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** set to all layers at the current hierarchy level.

## UI feedback
- Canvas: union bounding box around all selected layers.
- Left panel: all corresponding rows highlighted.
- Right panel: multi-selection view.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → multi-selection-bounding-box
- `regions/left-navigation.md` → layers-tree
- `state-matrix.md` → Multi-mixed selection row

## Semantic event(s) candidate
- `select_all { scope: "page" | "parent_group" | "parent_frame", layer_ids: [...] }`

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- Exact behavior when inside a deeply nested context not always consistent across editors; default: "select all siblings at current nesting level".
