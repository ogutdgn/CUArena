# Place image (or video)

- **Category:** shape-creation
- **One-line summary:** Insert one or more images / videos on the canvas from an OS file picker or drag-drop.

## Triggers
- Keyboard: `Shift Cmd/Ctrl K` — opens OS file picker.
- Toolbar: Shape-tools dropdown → Image / video.
- Drag-drop: drag image / video files from OS onto the canvas.
- Clipboard paste: paste image from system clipboard (also creates an image layer; overlaps with `clipboard/paste.md`).

## Preconditions
- User has at least one valid image file selected (or the drag payload contains image files).
- Image format supported (PNG / JPG / GIF / SVG / WebP / MP4 — subset per docs).

## Inputs
- File(s) chosen via OS picker OR file(s) dropped onto canvas.
- Drop coordinates (for drag-drop).

## Behavior

**Via file picker (Shift Cmd K):**
1. User triggers shortcut → OS file picker opens.
2. User selects one or more image files → cursor becomes a "place image" state with thumbnail preview of the first image.
3. Each click on canvas places the next image at natural dimensions; ESC cancels remaining placements.
4. OR user drags to define size at placement time.

**Via drag-drop:**
1. Files dragged from OS over canvas → drop overlay appears.
2. On drop: each file becomes a new image layer placed at the drop point, at natural dimensions.

**In all cases:**
- Image data becomes the fill of a rectangle-shaped layer (per Figma convention — `an image is imported as a fill on a shape`).
- Selection = the newly-placed layer (last one if batch).

## Outputs
- **Scene graph changes:** N new image layers.
  - `type: "image"` (a rectangle with an image fill in engine terms)
  - `x`, `y`, `w`, `h` from natural image dimensions (or drag-defined size)
  - `fill: [{ type: "image", data: <imageRef>, mode: "fill" }]`
- **Selection changes:** selection = last placed layer (or all, if the engine batches).

## UI feedback
- During "place image" state (post-picker): cursor carries a small thumbnail preview.
- On drop / click: standard image-layer appearance; selection bounding box.
- Left panel: new layer(s) added.
- Right panel: single-shape view; Fill section shows the image fill with Fill / Fit / Crop / Tile dropdown.

## Side effects
- Undo stack: adds "place image" entry; undo removes the layer(s).
- Clipboard: untouched (unless the source was a paste, in which case the paste.md event applies).

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown (Image / video entry)
- `regions/right-properties.md` → fill-section (image fill controls)
- `regions/floating-overlays.md` → color-picker (image-fill mode entries)

## Semantic event(s) candidate
- `place_image { source: "file_picker" | "drag_drop" | "clipboard_paste", files: [{ name, size, natural_w, natural_h }], position: {x, y}, layer_ids: [...] }`
- Clipboard-paste path may also emit `paste` — `plan/03` decides whether these overlap or are distinct.

## Source articles
- `add-images-and-videos-to-designs`
- `adjust-the-properties-of-an-image`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- Multi-image batch placement sequence not fully detailed; per docs each click places next, ESC cancels. Treat as the documented behavior.
- Video support: MP4 is documented; GIF handled as image. Treat video as the same layer type with a video-fill flag.
- Natural-dimension cap (e.g. 4096×4096) not specified; pick a sane max.
