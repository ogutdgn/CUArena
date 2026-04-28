# Apply a color style

- **Category:** color
- **One-line summary:** Bind a layer's fill / stroke / effect color to an existing local or library color style.

## Triggers
- Color picker open — switch to **Libraries** tab; click a style swatch.
- Right sidebar **Fill** or **Stroke** row — apply-style icon → opens the styles browser inline → click a style.
- Eyedropper Shift+click on a layer that has a style applied — see `use-eyedropper.md`.

## Preconditions
- Picker / styles browser open.
- At least one color style exists locally OR an enabled library exposes color styles.

## Inputs
- Pointer click on a style swatch.

## Behavior
1. User browses available styles (grouped by current file vs enabled libraries).
2. Clicking a style binds the target property to that style id.
3. Layer renders with the style's color; if the style updates later, the layer follows.

## Outputs
- **Scene graph changes:** target property's color is replaced by a style binding.
- **Selection changes:** none.

## UI feedback
- Swatch in the right sidebar gains a style chip / icon.
- Picker shows the style as currently applied.

## Side effects
- Undo stack: one entry per style apply.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → libraries-tab
- `regions/right-properties.md` → fill-section → apply-style-icon

## Semantic event(s) candidate
- `apply_color_style { layer_ids, target, fill_index?, style_id, style_source: "local" | "library", trigger: "picker_click" | "panel_apply_style_icon" | "eyedropper_shift" }`

## Source articles
- `apply-styles-to-layers-and-objects`
- `manage-and-share-styles`

## Notes / gaps
- Multi-select with mixed style applications: apply replaces all targeted layers' bindings.
- Style detach (revert to raw color) — separate flow; document under `detach-color-style.md` if implemented.
