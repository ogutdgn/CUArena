# Set image fill

- **Category:** fills
- **One-line summary:** Set a fill to use an uploaded image (or video / GIF) as its source.

## Triggers
- Color picker open → fill-type icons → **Image** (or **Video** for video/GIF).
- Bulk place tool: Toolbar **Image/video** (or `Shift+Cmd+K` / `Shift+Ctrl+K`), select files, click on existing layer to replace its fill.
- Drag-and-drop file from desktop onto an existing layer's swatch in the panel.
- Drag-and-drop file from desktop onto the asset preview in the open color picker.
- Paste from clipboard (after copy of an image).

## Preconditions
- File type supported: JPG, PNG, HEIC, WebP, GIF, TIFF (Safari only) for image; MP4, MOV, WebM for video.
- (For "select existing layer" path) layer is selectable.

## Inputs
- Click → **Upload from computer** file dialog → choose file.
- Or drag-drop file directly.

## Behavior
1. On selecting **Image**, picker shows a checkered placeholder until a file is chosen.
2. Picker presents two paths: **Upload from computer** OR **Make an image** (Figma AI; out-of-scope for mock).
3. Selected image becomes the fill's `source` (asset reference).
4. Fill mode defaults to **Fill** (covers the layer; clipped if aspect ratios differ).
5. Files larger than 4096 × 4096 are auto-scaled proportionally to fit (longest dimension capped at 4096).

## Outputs
- **Scene graph changes:** fill type → `image` (or `video`); `imageRef` / `assetId`; default `mode = "fill"`.
- **Selection changes:** none.
- **Persistent file state:** asset uploaded to the file's asset store.

## UI feedback
- Picker shows asset preview thumbnail.
- Layer renders the image clipped to its bounds.
- Layers panel: layer icon switches to image / video / GIF icon.

## Side effects
- Undo stack: one entry per fill set.
- Asset upload (out-of-scope for mock — implementer can keep blob in memory).

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → fill-type-row, image-controls
- `regions/right-properties.md` → fill-section → fill-row swatch (drop target)
- `regions/canvas-overlays.md` → drop-zone overlay during file drag

## Semantic event(s) candidate
- `set_fill_type { layer_ids, fill_index, to_type: "image", from_type, trigger }`
- `upload_image_fill { layer_ids, fill_index, asset_id, dimensions, trigger: "picker_upload" | "drag_drop" | "paste" | "place_image_tool" }`

## Source articles
- `add-images-and-videos-to-designs`
- `guide-to-fills`
- `update-fills-using-the-color-picker`

## Notes / gaps
- Video fills are paid-plan-only. Mock can render static placeholder for video.
- "Make an image" (Figma AI) — out of scope for mock; treat as visual-only or unsupported toast.
