# Deselect

- **Category:** selection
- **One-line summary:** Clear the current selection.

## Triggers
- `Esc` with canvas focused.
- Click on empty canvas (Move tool active) — also counts as a case of `click-select` with no hit target.
- Keyboard: `Shift Cmd A` / `Shift Ctrl A` (deselect-all shortcut, reported in some docs).

## Preconditions
- At least one layer is currently selected (otherwise no-op).

## Inputs
- None beyond trigger.

## Behavior
1. Set selection to `[]`.
2. Right-sidebar swaps to no-selection state (Page + Local styles + Export page sections).
3. Canvas overlays (bounding box, handles) disappear.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** cleared.

## UI feedback
- Canvas: bounding box removed.
- Left panel: no rows highlighted.
- Right panel: switches to no-selection view.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `state-matrix.md` → Nothing selected row

## Semantic event(s) candidate
- `deselect { trigger: "escape" | "click_empty_canvas" | "shortcut" }`

## Source articles
- `select-layers-and-objects`
- `explore-design-files`

## Notes / gaps
- `Esc` behavior may also exit nested-group context (if one is entered via double-click). That is separate, handled by `layers/exit-group.md`.
