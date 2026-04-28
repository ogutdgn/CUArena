# Resize frame (with children behavior)

- **Category:** frames
- **One-line summary:** Resize a frame via corner/edge handles, sidebar W/H inputs, or "Resize to fit"; children respond per their constraint settings.

## Triggers
- **Drag a corner / edge handle** on the frame's selection box.
- **Right sidebar Layout section**: type into W or H input; or scrub the icon; expressions supported (`+`, `-`, `*`, `/`, `%`).
- **Lock aspect ratio toggle**: keeps W/H proportional during input/scrub.
- **Resize to fit** (`⌥⇧⌘R` / `Alt+Shift+Ctrl+R`, or icon in Layout section): redraws the frame around the outermost bounds of its children.
- **Frame preset dropdown** in Layout section: switching presets (Phone/Tablet/Desktop/etc.) sets W/H to the preset.

## Preconditions
- A frame is selected.

## Inputs
- Pointer drag on handle, or numeric input, or shortcut.
- Modifiers during drag:
  - **Cmd / Ctrl** — ignore child constraints (children stay fixed, frame just resizes around them).
  - **Shift** — constrain to aspect ratio (or, with lock-aspect already on, breaks lock).
  - **Alt / Option** — resize from center.

## Behavior
1. Frame's W/H/X/Y update according to the handle and modifiers.
2. Children resize/move per their constraint settings (Left/Right/Top/Bottom/Center/Scale on each axis — see `set-constraints.md`).
3. With **Cmd/Ctrl** held during drag, children don't react (their absolute positions/sizes stay).
4. **Resize to fit** sets the frame's W/H to the bounding box of its children; X/Y adjust so that children's screen positions stay constant.
5. Frame **preset** application (per `frames-in-figma-design`): if children have constraints, they resize accordingly; otherwise children stay at original positions/sizes.

## Outputs
- **Scene graph changes:** frame W/H/X/Y updated; children's W/H/X/Y may update per constraints.
- **Selection changes:** none.

## UI feedback
- W/H labels render near the bottom edge during drag.
- Smart-snap guides may appear (alignment to siblings/parent).
- Right sidebar updates W/H inputs live.

## Side effects
- Undo stack: one entry per resize gesture.

## Related UI schema entries
- `regions/canvas-overlays.md` → resize-handles, dimension-labels
- `regions/right-properties.md` → layout-section → W/H, lock-aspect, resize-to-fit, frame-preset dropdown

## Semantic event(s) candidate
- `resize_frame { frame_id, from_size, to_size, from_position, to_position, ignore_constraints, trigger: "handle_drag" | "panel_input" | "resize_to_fit" | "preset_change" }`

## Source articles
- `frames-in-figma-design`
- `apply-constraints-to-define-how-layers-resize`
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Expression support in W/H input: `%` not multiplicable per article (`*50%` is not 50%).
- Aspect-lock scrub vs typing: scrubbing while locked ratio constrains both.
