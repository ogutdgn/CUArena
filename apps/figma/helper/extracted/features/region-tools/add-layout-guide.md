# Add layout guide (rows / columns / grid) on a frame

- **Category:** region-tools
- **One-line summary:** Add a layout guide to a frame — rows, columns, or square grid — to help align children visually.

## Triggers
- Frame selected → right sidebar Layout section → **Layout guide** sub-section → `+`.

## Preconditions
- A frame selected.

## Inputs
- Guide type: **Grid** (square cells), **Columns**, **Rows**.
- Per type: count, gutter (px), margin / offset (px), color (with alpha).
- Stretch / Center / Left / Right alignment for columns / rows.

## Behavior
1. Guide stored on frame; rendered as overlay on canvas (visible while frame selected, by default).
2. Children unaffected geometrically — guides are visual aids only.
3. Toggle visibility globally via View Options dropdown (Layout guides toggle).

## Outputs
- **Scene graph changes:** frame's `layout_guides` array gains entry.
- **Selection changes:** none.

## UI feedback
- Guide overlay on canvas.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → layout-guide-section
- `regions/canvas-overlays.md` → layout-guide-overlay

## Semantic event(s) candidate
- `add_layout_guide { frame_id, type, count, gutter, margin, color }`
- `remove_layout_guide { frame_id, guide_index }`

## Source articles
- `create-layout-guides`
- `add-guides-to-the-canvas-or-frames`
- `combine-layout-guides-and-constraints`

## Notes / gaps
- Layout guides on the canvas (not on a frame) work similarly — created via menu / shortcut and span the page.
