# Zoom to fit

- **Category:** canvas-navigation
- **One-line summary:** Fit all content on the current page into the visible viewport.

## Triggers
- Keyboard: `Shift 1`.
- Zoom/view-options dropdown: "Zoom to fit" entry.
- When a file is first opened: applied automatically.

## Preconditions
- The current page has at least one layer (if empty, behavior may default to 100% at origin; not explicitly documented).

## Inputs
- None beyond the trigger.

## Behavior
1. Compute the bounding box of all layers on the current page.
2. Compute the zoom level + viewport offset such that the bounding box fits (with a small padding margin) inside the visible canvas area.
3. Set `viewport.zoom` and `viewport.x/y` accordingly.
4. Zoom-% display updates.

## Outputs
- **Scene graph changes:** none.
- **Viewport state changes:** `zoom` + `x/y` set to fit-all-content values.

## UI feedback
- Canvas reframes smoothly (with a short animation, per common editor convention — not explicitly documented in corpus).
- Zoom-% display updates.
- No toast.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/right-properties.md` → zoom-and-view-options-dropdown (entry "Zoom to fit")
- `regions/canvas-overlays.md` → canvas-zoom-and-pan

## Semantic event(s) candidate
- `zoom_to_fit { content_bounds: {x, y, w, h}, trigger: "keyboard" | "dropdown_entry" | "initial_load" }`

## Source articles
- `navigating-ui3`
- `adjust-your-zoom-and-view-options`

## Notes / gaps
- Padding margin around content when fitting not specified; common default ~5-10% of viewport on each side.
- Animated vs instant transition not specified; instant is fine as a default.
