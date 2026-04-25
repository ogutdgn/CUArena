# Set fill

- **Category:** properties
- **One-line summary:** Add, remove, reorder, or change the fill(s) of selected layer(s) — color, opacity, blend mode, image source.

## Triggers
- Right-sidebar Fill section:
  - `+` → add a new fill (default solid color)
  - Click a fill-row swatch → opens Color picker; edit color / change fill type
  - Hex input → type new value
  - Opacity input → type / scrub value
  - Eye icon on a fill row → toggle that fill's visibility
  - `…` on fill row → remove / reorder / paste over
- Color picker (opened from Fill swatch) — see `regions/floating-overlays.md` → color-picker for full control set.

## Preconditions
- Selection is non-empty.
- Selected layer type supports fills (shapes, frames, text, images, vectors).

## Inputs
- User interaction with any of the controls above.

## Behavior

**Add a fill:**
1. Click `+` in Fill section.
2. A new solid-color fill appended to the layer's `fills` array with default color.
3. Color picker may auto-open anchored to the new swatch.

**Change color of existing fill:**
1. Click swatch → color picker opens.
2. User edits HSV / hex / sliders → color updates live on canvas (via throttled updates).
3. Close picker = commit.

**Change opacity of a fill:**
1. Type in opacity input OR drag the picker's opacity slider.
2. Commit on blur / slider release.

**Toggle fill visibility:**
1. Click eye icon on the fill row.
2. Fill's `visible` flag toggles.

**Reorder fills:**
1. Drag a fill row in the Fill section (if supported) OR use `…` → move up / move down.

**Remove a fill:**
1. `…` on fill row → Remove.

## Outputs
- **Scene graph changes:** for each selected layer, the `fills` array is mutated.
- **Selection changes:** none.

## UI feedback
- Canvas: layer fill updates live as color changes.
- Panel: fill row updates to reflect new state.

## Side effects
- Undo stack: one entry per commit (opening picker, scrubbing, closing = one entry; fine-grained entries may be debounced).
- Clipboard: untouched.

## Related UI schema entries
- `regions/right-properties.md` → fill-section
- `regions/floating-overlays.md` → color-picker

## Semantic event(s) candidate
- `set_fill_color { layer_ids: [...], fill_index, from_color, to_color, trigger: "color_picker" | "hex_input" | "panel_swatch" }`
- `add_fill { layer_ids: [...], fill_index, default_color, trigger: "panel_plus" }`
- `remove_fill { layer_ids: [...], fill_index, trigger: "panel_menu" }`
- `reorder_fill { layer_ids: [...], from_index, to_index, trigger: "drag" | "panel_menu" }`
- `toggle_fill_visibility { layer_ids: [...], fill_index, to_visible, trigger: "panel_eye" }`
- `set_fill_opacity { layer_ids: [...], fill_index, from_opacity, to_opacity, trigger: "input" | "slider" }`
- Multiple events under one feature file because "fill" is a grouped meta-feature (per plan/02 §5 note: granularity rule collapses multi-trigger into one feature; here multiple *effects* keep separate events).

## Source articles
- `guide-to-fills`
- `apply-styles-to-layers-and-objects`

## Notes / gaps
- Gradient / Pattern / Video fills are `visual-only` (plan/00 §3 — not in §2). Solid fills + Image fills are functional.
- Multi-selection behavior: if selection has mixed fills, the Fill section shows "Mixed" for the swatch; applying a color sets all selected layers' fill to that color. Behavior consistent with real Figma.
- "Show in exports" checkbox is `visual-only` (exports out of scope).
