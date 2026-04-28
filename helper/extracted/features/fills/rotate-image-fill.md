# Rotate image fill (90° increments)

- **Category:** fills
- **One-line summary:** Rotate the image content within its fill in 90° clockwise increments without rotating the layer itself.

## Triggers
- Color picker open on image fill → click **Rotate 90°** button.

## Preconditions
- Fill type = image.
- Picker open.

## Inputs
- Pointer click on rotate button.

## Behavior
1. Each click rotates the image content 90° clockwise.
2. Layer geometry (W/H/X/Y/rotation) is unchanged — only the image-within-the-fill rotates.
3. For free-angle rotation of the image, use Crop mode (which exposes a corner rotate handle).

## Outputs
- **Scene graph changes:** fill's `image_rotation` field cycles through 0°/90°/180°/270°.
- **Selection changes:** none.

## UI feedback
- Canvas re-renders with rotated image.

## Side effects
- Undo stack: one entry per rotate.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → image-rotate-button

## Semantic event(s) candidate
- `rotate_image_fill { layer_ids, fill_index, from_rotation, to_rotation, trigger: "picker_button" }`

## Source articles
- `adjust-the-properties-of-an-image`

## Notes / gaps
- Crop mode supports free-angle rotation via corner handles — see `crop-image.md`.
