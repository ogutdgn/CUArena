# Set per-fill opacity

- **Category:** fills
- **One-line summary:** Adjust the opacity of one fill row (independent of the layer's overall opacity).

## Triggers
- Right sidebar **Fill** section, fill row → opacity input field.
- Color picker open → opacity slider / input (per `set-color-opacity.md`).

## Preconditions
- Fill row exists.

## Inputs
- Numeric input `0–100`%.
- Picker slider drag.

## Behavior
1. Per-fill opacity is multiplied with the fill's color alpha.
2. Layer-level opacity is then multiplied with the result when compositing.
3. Stacking: each fill's opacity composes with the underlying fill stack.

## Outputs
- **Scene graph changes:** fill's `opacity` field updated.
- **Selection changes:** none.

## UI feedback
- Panel input updates; canvas updates live.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → fill-section → fill-row opacity input
- `regions/floating-overlays.md` → color-picker → opacity-slider

## Semantic event(s) candidate
- `set_fill_opacity { layer_ids, fill_index, from_opacity, to_opacity, trigger: "panel_input" | "picker_slider" }`

## Source articles
- `guide-to-fills`
- `update-fills-using-the-color-picker`

## Notes / gaps
- Distinction with **layer opacity** (`properties/set-opacity.md`): layer opacity affects all fills+strokes+effects together as one composite; per-fill opacity affects only that fill.
