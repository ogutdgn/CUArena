# Zoom in / out

- **Category:** canvas-navigation
- **One-line summary:** Change the viewport zoom level, keeping a reference point fixed (cursor position or viewport center).

## Triggers
- `Cmd` + scroll (Mac) / `Ctrl` + scroll (Windows): zoom continuously; anchored at cursor.
- Pinch gesture on trackpad: zoom continuously; anchored at cursor.
- Magic Mouse double-tap: discrete zoom in step.
- Keyboard: `Shift +` zoom in, `Shift -` zoom out. Discrete steps.
- Right-sidebar zoom-% control: typing a number + Enter sets an exact zoom.
- Zoom/view-options dropdown: entries "Zoom in" / "Zoom out" with shortcuts displayed.

## Preconditions
- Pointer is over the canvas (for cursor-anchored zoom) or the canvas has focus (for keyboard / dropdown triggers).
- No modal overlay is capturing input.

## Inputs
- Scroll delta or pinch delta (continuous).
- Shift modifier + `+` or `-` key (discrete).
- Numeric value typed into zoom-% input.

## Behavior
1. Compute new zoom level from input (delta-based or absolute).
2. Determine zoom anchor:
   - Cursor-anchored (scroll / pinch): keep the world-space point under the cursor stationary while zoom changes.
   - Center-anchored (keyboard / dropdown): keep the viewport center's world-space point stationary.
3. Update viewport `zoom`; viewport `x/y` adjusts so the anchor stays fixed.
4. Zoom-% display in the right-sidebar header updates live.

## Outputs
- **Scene graph changes:** none.
- **Viewport state changes:** `zoom` updated; `x/y` adjusted to preserve anchor.

## UI feedback
- Canvas content rescales.
- Zoom-% display in right panel updates live.
- On-canvas overlays (selection box, handles, guides, rulers) rescale so their screen-space size stays consistent.
- If pixel-grid or pixel-preview is enabled and threshold crossed (zoom ≥ 400% for pixel grid), that overlay appears/disappears — visual-only for us.
- No toast.

## Side effects
- Undo stack: no entry (view state).
- Clipboard: untouched.
- Focus: unchanged.

## Related UI schema entries
- `regions/right-properties.md` → zoom-percentage-display
- `regions/right-properties.md` → zoom-and-view-options-dropdown
- `regions/canvas-overlays.md` → canvas-zoom-and-pan

## Semantic event(s) candidate
- `zoom_canvas { from, to, anchor: {x, y}, trigger: "scroll" | "pinch" | "keyboard" | "input_field" | "dropdown_entry" | "magic_mouse" }`

## Source articles
- `navigating-ui3`
- `adjust-your-zoom-and-view-options`

## Notes / gaps
- Continuous zoom step per scroll tick not numerically specified; common default is ~1.1× per tick. Pick at build time.
- Max / min zoom bounds not explicitly documented; safe defaults ~1% min / ~25600% max.
