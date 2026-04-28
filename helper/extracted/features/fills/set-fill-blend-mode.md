# Set per-fill blend mode

- **Category:** fills
- **One-line summary:** Apply a blend mode to a single fill (independent of layer-level blend mode).

## Triggers
- Color picker open → click **Blend mode** dropdown in the picker.

## Preconditions
- Picker open with a fill targeted.

## Inputs
- Pointer click on dropdown → choose a blend mode (Normal, Multiply, Screen, Overlay, etc.).

## Behavior
1. Selected blend mode is stored per-fill.
2. Renderer composes that fill into the layer using the chosen mode.
3. Layer-level blend mode (in Appearance section) composes the layer onto its parent independently.

## Outputs
- **Scene graph changes:** fill's `blend_mode` field updated.
- **Selection changes:** none.

## UI feedback
- Picker dropdown shows the new mode.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → blend-mode-dropdown

## Semantic event(s) candidate
- `set_fill_blend_mode { layer_ids, fill_index, from_mode, to_mode, trigger: "picker_dropdown" }`

## Source articles
- `apply-blend-modes-to-layers-fills-and-effects`
- `update-fills-using-the-color-picker` (item 4)

## Notes / gaps
- Full blend-mode enum: see `apply-blend-modes-to-layers-fills-and-effects` for the canonical list (Normal, Darken, Multiply, Color burn, Lighten, Screen, Color dodge, Overlay, Soft light, Hard light, Difference, Exclusion, Hue, Saturation, Color, Luminosity).
