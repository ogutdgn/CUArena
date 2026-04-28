# Set image fill mode (Fill / Fit / Crop / Tile)

- **Category:** fills
- **One-line summary:** Choose how an image fill maps onto the layer — Fill, Fit, Crop, or Tile.

## Triggers
- Color picker open on an image fill → Fill-mode dropdown → choose one.

## Preconditions
- A fill is set to image type.
- Picker open with that fill targeted.

## Inputs
- Click on dropdown → select option.

## Behavior

**Fill** — image positioned and scaled so it covers the layer entirely. If aspect ratios differ, image is clipped. Recomputed when layer is resized.

**Fit** — image scaled so the entire image is visible inside the layer. May leave letterbox/pillarbox space depending on layer shape.

**Crop** — like a non-destructive mask: blue handles appear so the user can drag the visible region. Equivalent in many ways to entering a "Crop" tool (see `crop-image.md`).

**Tile** — image is repeated across the layer. The Tile mode exposes a percentage scale slider that controls the tile size relative to the original image dimensions.

Mode persists when the layer is later resized.

## Outputs
- **Scene graph changes:** fill's `mode` field set to one of `"fill" | "fit" | "crop" | "tile"`.
- For `crop`, additional `crop_rect` field becomes editable.
- For `tile`, additional `tile_scale_percent` field.

## UI feedback
- Picker reflects the new mode.
- Canvas re-renders the fill accordingly.
- For Crop, blue resize handles appear on the image inside the layer.

## Side effects
- Undo stack: one entry per mode change (or one per picker session if combined with other edits).

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → image-fill-mode dropdown
- `regions/canvas-overlays.md` → image-crop-handles (Crop mode only)

## Semantic event(s) candidate
- `set_image_fill_mode { layer_ids, fill_index, from_mode, to_mode, trigger: "picker_dropdown" }`

## Source articles
- `adjust-the-properties-of-an-image`
- `crop-an-image`

## Notes / gaps
- Default mode for newly added image fills is **Fill** per the article.
