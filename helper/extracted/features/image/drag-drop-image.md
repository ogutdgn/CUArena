# Drag & drop image from desktop

- **Category:** image
- **One-line summary:** Drop an image / video file from the OS onto the canvas to create a new layer or replace an existing fill.

## Triggers
- Drag a file from the desktop into the Figma window.

## Preconditions
- File type supported (PNG/JPG/HEIC/WebP/GIF/TIFF/MP4/MOV/WebM).

## Inputs
- File drop event with one or more files.

## Behavior
- **Drop on empty canvas**: creates new rectangle layer with image as fill.
- **Drop on existing layer**: replaces that layer's fill.
- **Drop on a fill swatch in the right sidebar**: replaces that swatch's image (per `replace-image.md`).
- Multi-file drop: behaves like place-image-bulk.

## Outputs
- **Scene graph changes:** new layer(s) or fill updates.
- **Persistent state:** asset uploaded.

## UI feedback
- Drop-zone overlay during drag.

## Side effects
- Undo stack: per-drop entries.

## Related UI schema entries
- `regions/canvas-overlays.md` → file-drop-zone

## Semantic event(s) candidate
- `drag_drop_image { files: [...], target: "canvas" | "layer" | "swatch", trigger: "os_drag_drop" }`

## Source articles
- `add-images-and-videos-to-designs`
