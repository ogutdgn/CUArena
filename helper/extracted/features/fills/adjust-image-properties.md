# Adjust image properties (exposure, contrast, saturation, temperature, tint, highlights, shadows)

- **Category:** fills
- **One-line summary:** Apply non-destructive photo-style adjustments to an image fill via picker sliders.

## Triggers
- Color picker open on an image fill → drag any of the adjustment sliders.

## Preconditions
- Fill type = image.
- Picker open.

## Inputs
- Slider drag (left = negative, right = positive).
- Numeric typing into the adjacent value field.

## Behavior

The picker exposes seven sliders (each non-destructive, reversible at any time):

1. **Exposure** — overall brightness; negative darkens, positive brightens.
2. **Contrast** — gap between light and dark pixels; negative narrows, positive widens.
3. **Saturation** — color intensity; full negative = black-and-white.
4. **Temperature** — cool (blue) ↔ warm (amber) tone shift.
5. **Tint** — green ↔ magenta cast.
6. **Highlights** — adjusts only the lighter pixels.
7. **Shadows** — adjusts only the darker pixels.

Adjustments do not modify the source asset; they're stored as fill-level parameters.

## Outputs
- **Scene graph changes:** fill's `image_adjustments` object updated (`{ exposure, contrast, saturation, temperature, tint, highlights, shadows }`).
- **Selection changes:** none.

## UI feedback
- Canvas re-renders with the adjustments applied.
- Slider handle and numeric value update.

## Side effects
- Undo stack: one entry per picker session that produces changes (drag-release or input commit).

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → image-adjustment-sliders

## Semantic event(s) candidate
- `set_image_adjustment { layer_ids, fill_index, property: "exposure" | "contrast" | "saturation" | "temperature" | "tint" | "highlights" | "shadows", from_value, to_value, trigger: "picker_slider" | "picker_input" }`

## Source articles
- `adjust-the-properties-of-an-image`

## Notes / gaps
- Slider value range (e.g. -100 to +100) not pinned; treat as -100…+100 (typical Figma convention).
