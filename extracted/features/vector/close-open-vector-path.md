# Close / open vector path

- **Category:** vector
- **One-line summary:** Toggle a vector network's path between closed (start connects to end) and open.

## Triggers
- During Pen creation: hover starting anchor → click (small close-indicator appears) closes the path.
- In vector edit: select two endpoint anchors + invoke close (Cmd/Ctrl + J in some editors — corpus doesn't confirm for Figma).
- Right-click → Close path (if rendered).

## Preconditions
- Target vector has at least 2 anchor points.
- The specific interaction:
  - For Pen close: hovering the starting anchor during creation.
  - For edit-mode close: two endpoint anchors (or one if path is to be closed in-place) selected.

## Inputs
- Trigger (click on hover, or shortcut / menu).

## Behavior

**Close during Pen:**
1. Hover starting anchor → indicator appears.
2. Click → `closed = true`; optionally add a default fill (see `use-pen-tool.md` note).

**Open:**
1. Select a segment on a closed path.
2. Cut (X) tool splits the segment, turning the path open.

## Outputs
- **Scene graph changes:** vector's `closed` flag toggled; possibly `fill` added/removed.

## UI feedback
- Canvas: path now rendered with a closing segment between start and end (or that segment removed for open).

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode

## Semantic event(s) candidate
- `close_vector_path { layer_id, trigger: "pen_hover_click" | "shortcut" | "context_menu" }`
- `open_vector_path { layer_id, cut_segment_index, trigger: "cut_tool" }`

## Source articles
- `vector-networks`
- `edit-vector-layers`

## Notes / gaps
- Cut tool itself is outside plan/00 §2 explicit list — may be `visual-only`. If so, "open" path support is limited. Flag in `plan/03`.
