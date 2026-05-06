# Replace image

- **Category:** fills
- **One-line summary:** Swap the asset used by an image fill while preserving its fill-mode settings (cropping, mode, adjustments).

## Triggers
- Drag a file from the desktop onto the asset preview in the open color picker.
- Drag a file from the desktop onto the swatch in the right-sidebar **Fill** or **Stroke** section.
- Color picker → "Upload from computer" while an image fill is already in place.

## Preconditions
- A fill of type image (or video) exists on the targeted layer.

## Inputs
- File drop OR file picker selection.

## Behavior
1. New asset replaces the previous `imageRef` / `assetId`.
2. Existing settings persist: fill mode (Fill/Fit/Crop/Tile), crop rect, rotation, image adjustments.
3. Layer re-renders with the new image under the same mapping.

## Outputs
- **Scene graph changes:** fill's source asset reference updated.
- **Selection changes:** none.
- **Persistent file state:** new asset uploaded.

## UI feedback
- Picker preview thumbnail swaps.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per replace.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → asset-preview, upload-button
- `regions/right-properties.md` → fill-section → swatch (drop target)

## Semantic event(s) candidate
- `replace_image_fill { layer_ids, fill_index, from_asset_id, to_asset_id, trigger: "picker_drop" | "panel_drop" | "picker_upload" }`

## Source articles
- `add-images-and-videos-to-designs` (section "Replace image and video fills")

## Notes / gaps
- Behavior of replace when the new image has different dimensions: docs say "any fill mode settings you've applied, including any cropping or positioning" are preserved; geometry adapts.
