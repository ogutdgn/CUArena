# Resize frame to fit children

- **Category:** frames
- **One-line summary:** Shrink or grow a frame to exactly enclose the bounding box of its current children.

## Triggers
- Selection = frame, then:
  - Shortcut: `⌥ Shift ⌘ R` (Mac) / `Alt Shift Ctrl R` (Win).
  - Right sidebar **Layout** section → resize-to-fit icon (top-right corner of the section).

## Preconditions
- A frame is selected.
- Frame has at least one child (otherwise no-op).

## Inputs
- Keyboard shortcut OR click on icon.

## Behavior
1. Compute the bounding box of all children.
2. Set the frame's W/H to that bbox's W/H.
3. Adjust the frame's X/Y so the children remain in their original screen positions; their local coordinates inside the frame are translated accordingly.

## Outputs
- **Scene graph changes:** frame W/H/X/Y updated; children's local X/Y updated to match.
- **Selection changes:** none.

## UI feedback
- Frame snaps to children's bbox.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → layout-section → resize-to-fit icon

## Semantic event(s) candidate
- `resize_frame_to_fit { frame_id, from_size, to_size, from_position, to_position, trigger: "shortcut" | "panel_icon" }`

## Source articles
- `frames-in-figma-design`

## Notes / gaps
- Behavior on a frame with auto-layout: auto-layout already governs hugging — confirm whether resize-to-fit is a no-op or also triggers on hug. Corpus does not pin this — defer to auto-layout spec.
