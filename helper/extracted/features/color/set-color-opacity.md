# Set color opacity (alpha)

- **Category:** color
- **One-line summary:** Adjust the alpha channel of the current color via the picker's opacity slider or a percentage input field.

## Triggers
- Color picker open — pointer-drag the opacity slider, OR type a percentage into the alpha/opacity input next to the slider.
- Right sidebar fill row — type a percentage into the per-fill opacity input (no picker needed).

## Preconditions
- Picker open OR fill row visible with the per-fill opacity input shown.

## Inputs
- Pointer-drag on opacity slider.
- Keyboard input of a percentage `0-100` in the opacity field.

## Behavior
1. User drags slider or types value.
2. Color's alpha channel updates live.
3. Commit on pointer-release / Enter / blur.

## Outputs
- **Scene graph changes:** color's alpha component updated for the targeted property.
- **Selection changes:** none.

## UI feedback
- Slider handle moves; numeric field updates.
- Canvas updates live (layer fades / un-fades).
- The fill swatch itself shows a checkerboard background through transparency to communicate alpha.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → opacity-slider, opacity-input
- `regions/right-properties.md` → fill-section → fill-row opacity input

## Semantic event(s) candidate
- `set_color_opacity { layer_ids, target, fill_index?, from_opacity, to_opacity, trigger: "picker_slider" | "picker_input" | "panel_input" }`

## Source articles
- `update-fills-using-the-color-picker`
- `guide-to-fills`

## Notes / gaps
- Distinction between **fill opacity** (per-fill alpha) and **layer opacity** (global on the layer): both exist independently. This spec is fill alpha; layer opacity is `properties/set-opacity.md`. Source: `guide-to-fills` and `apply-blend-modes-to-layers-fills-and-effects`.
