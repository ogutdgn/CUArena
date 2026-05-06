# Crop image (Crop tool)

- **Category:** fills
- **One-line summary:** Non-destructively crop, reposition, resize, and free-rotate an image inside its fill.

## Triggers
- **Double-click** the image layer on canvas → activates Crop tool.
- Right sidebar **Image** section → click **Crop image**.
- Color picker → set fill mode to **Crop**.

## Preconditions
- Fill type = image.

## Inputs
- Pointer drag on blue handles around the image to crop.
- Slider in panel (alternative to handles).
- **Aspect ratio** picker.
- **Resize to fit** button.
- Modifier keys during drag:
  - **Option / Alt** — modify opposite sides simultaneously.
  - **Cmd / Ctrl** + drag corner — quick-crop shortcut from outside Crop mode.
  - **Control / Fn** — break aspect-ratio lock.
- After crop is applied, additional in-place edits:
  - Hover faded area → **reposition** cursor → drag to reposition.
  - Hover outside corner → **rotate** cursor → drag to rotate (Shift = 15° increments).
  - Hover edge → **resize** cursor → drag to resize.
- `Enter` or click outside applies the crop. `Esc` cancels (TBC by docs).

## Behavior
1. Tool is non-destructive — the cropped-out area stays in the fill data and can be revealed by un-cropping.
2. Resulting fill stores: source asset + crop rect + rotation.

## Outputs
- **Scene graph changes:** fill's `mode = "crop"`, `crop_rect`, `image_rotation` updated.
- **Selection changes:** none.

## UI feedback
- Crop tool active: blue handles around the image, image area outside crop fades.
- Cursor changes contextually (reposition / rotate / resize).
- Toolbar may surface a Crop-mode secondary toolbar (aspect ratio + resize-to-fit).

## Side effects
- Undo stack: one entry per crop session (Enter / outside-click commits).
- Tool state: editor in "crop mode" until exit.

## Related UI schema entries
- `regions/canvas-overlays.md` → image-crop-handles, image-crop-cursor-states
- `regions/floating-overlays.md` → crop-aspect-ratio-picker

## Semantic event(s) candidate
- `enter_crop_mode { layer_ids, fill_index, trigger: "double_click" | "panel_button" | "picker_mode" }`
- `apply_crop { layer_ids, fill_index, crop_rect, rotation, trigger: "enter" | "outside_click" }`
- `cancel_crop { layer_ids, fill_index }`

## Source articles
- `crop-an-image`
- `adjust-the-properties-of-an-image`

## Notes / gaps
- Aspect ratio picker contents (preset list) not enumerated by docs; "free" + common presets like 1:1, 4:3, 16:9, 3:2 are typical.
