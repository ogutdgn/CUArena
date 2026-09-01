# Duplicate frame (quick-add `+` plus)

- **Category:** frames
- **One-line summary:** With the Frame tool active, hover over an existing frame; `+` plus icons appear on either side; click to duplicate (or hold Alt to create a blank same-size frame).

## Triggers
- Frame tool active (`F` / `A` / toolbar).
- Hover over an existing top-level frame on the canvas.
- Click `+` plus icon that appears on the frame's left or right.

## Preconditions
- Frame tool active.
- Hovered frame is on the canvas.

## Inputs
- Pointer click on the `+` button.
- Optional `⌥ Option` (Mac) / `Alt` (Win) modifier — creates a blank same-size frame instead of duplicating contents.

## Behavior
1. Click `+`: a duplicate of the hovered frame (with all children) is placed immediately adjacent on that side.
2. Other frames in the layout are nudged over to accommodate (per `frames-in-figma-design`).
3. If frame is inside a section, the section resizes to accommodate the new frame.
4. With `Alt` held: a blank frame of the same size is placed; no children copied.

## Outputs
- **Scene graph changes:** new frame added; possibly other frames moved.
- **Selection changes:** selection = new frame.

## UI feedback
- Plus indicators on hover.
- Animation as other frames slide.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → frame-quick-add-plus

## Semantic event(s) candidate
- `quick_add_frame { source_frame_id, new_frame_id, side: "left" | "right", blank: boolean, trigger: "plus_button" }`

## Source articles
- `frames-in-figma-design`

## Notes / gaps
- Whether plus icons appear on top/bottom (vertical layouts) is not addressed in the article; treat as left/right only.
