# Set corner radius

- **Category:** properties
- **One-line summary:** Change the corner radius of a rectangle / frame / supported shape — uniform or per-corner.

## Triggers
- Right-sidebar Appearance section: corner-radius input (uniform) or Independent-corners expand.
- Canvas: corner-radius circle handles inside the shape's corners — drag inward to increase radius, outward to decrease.
- Keyboard: some editors bind `Shift [ / ]` — corpus doesn't confirm.

## Preconditions
- Selection is a shape or frame that supports corner radius (rectangle, frame; not line, not ellipse, not text).

## Inputs
- Panel: numeric input (uniform), or independent-corner inputs when expanded (top-left / top-right / bottom-right / bottom-left).
- Canvas handle drag: pointer delta relative to corner.

## Behavior

**Uniform:**
1. Set corner radius on all four corners to typed / dragged value.

**Independent corners:**
1. Click the "Independent corners" icon → panel expands to show four individual inputs.
2. Edit any corner's value independently.

**On-canvas drag:**
1. Hover near a corner → circle handle appears.
2. Drag handle toward / away from corner → radius changes.

## Outputs
- **Scene graph changes:** selected layer's corner-radius fields updated.
- **Selection changes:** none.

## UI feedback
- Canvas: shape corners round live.
- Panel: value(s) reflect.
- Handles visually anchor at the current radius.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → appearance-section (corner radius)
- `regions/canvas-overlays.md` → corner-radius-handles

## Semantic event(s) candidate
- `set_corner_radius { layer_ids, from: {tl, tr, bl, br}, to: {tl, tr, bl, br}, trigger: "panel_uniform" | "panel_per_corner" | "canvas_handle_drag" }`

## Source articles
- `adjust-corner-radius-and-smoothing`

## Notes / gaps
- Corner smoothing is `visual-only` (advanced aesthetic feature — not in plan/00 §2).
- Max corner radius is typically `min(w, h) / 2` (real Figma clamps there).
