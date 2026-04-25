# Zoom to selection

- **Category:** canvas-navigation
- **One-line summary:** Fit the currently-selected layers into the visible viewport.

## Triggers
- Keyboard: `Shift 2`.
- Zoom/view-options dropdown: "Zoom to selection" entry.
- Some docs report `Cmd/Ctrl 3` as an alternate.

## Preconditions
- At least one layer is selected. If nothing is selected, the trigger is a no-op (behavior not explicitly documented; reasonable to show a toast or silently ignore — `plan/03` decision).

## Inputs
- None beyond the trigger.

## Behavior
1. Compute the bounding box of the current selection (union of all selected layers).
2. Compute zoom + viewport offset such that the bounding box fits (with padding margin) into the visible canvas area.
3. Set `viewport.zoom` and `viewport.x/y` accordingly.

## Outputs
- **Scene graph changes:** none.
- **Viewport state changes:** `zoom` + `x/y` set to fit-selection values.

## UI feedback
- Canvas reframes onto the selection.
- Zoom-% display updates.
- Selection bounding box remains visible (now larger on screen).

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/right-properties.md` → zoom-and-view-options-dropdown (entry "Zoom to selection")

## Semantic event(s) candidate
- `zoom_to_selection { selection_bounds: {x, y, w, h}, layer_ids: [...], trigger: "keyboard" | "dropdown_entry" }`

## Source articles
- `adjust-your-zoom-and-view-options`

## Notes / gaps
- Empty-selection behavior not documented. Default: silently ignore.
