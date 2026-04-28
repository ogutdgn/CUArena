# Set image tile scale

- **Category:** fills
- **One-line summary:** When image fill mode is **Tile**, set the size of each tile as a percentage of the image's original dimensions.

## Triggers
- Image fill in **Tile** mode → drag percentage slider OR type a value into the percent field.

## Preconditions
- Fill type = image, mode = tile.
- Picker open.

## Inputs
- Slider drag, or numeric typing of percentage.

## Behavior
1. Tile size = original image dimensions × percentage.
2. Tiles repeat across the layer's bounds.

## Outputs
- **Scene graph changes:** fill's `tile_scale_percent` updated.
- **Selection changes:** none.

## UI feedback
- Canvas re-renders the tiled fill at the new scale.

## Side effects
- Undo stack: one entry per commit (slider release or input commit).

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → image-tile-scale-slider

## Semantic event(s) candidate
- `set_image_tile_scale { layer_ids, fill_index, from_percent, to_percent, trigger: "picker_slider" | "picker_input" }`

## Source articles
- `adjust-the-properties-of-an-image`

## Notes / gaps
- Range minimum/maximum not enumerated by docs; treat as 1–1000% with sensible clamps.
