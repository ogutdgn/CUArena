# Enter frame

- **Category:** frames
- **One-line summary:** Step into a frame so subsequent clicks scope to its children. The frame becomes the "current container" for hit-testing and select-all.

## Triggers
- Double-click on a frame on the canvas (selects the first child).
- With a frame selected: press `Enter` / `Return` — selects a child and scopes editing into the frame (per `frames-in-figma-design`).
- Click a child via the Layers panel (also enters scope to that child's parent).

## Preconditions
- A frame exists with at least one child (otherwise Enter has no effect).

## Inputs
- Pointer double-click OR `Enter` key.

## Behavior
1. The selection moves to a child of the frame.
2. The "current scope" becomes the frame: hit-testing for clicks now hits children directly (rather than the frame itself).
3. `Tab` / `Shift Tab` cycles to next/previous siblings within the same parent.
4. `Shift Enter` selects the parent (steps back out one level — see `exit-frame.md`).

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** selection moves to the entered child.
- **Editor state:** active scope is the entered frame.

## UI feedback
- Selected child shows selection outline.
- Parent bounds overlay (dashed) renders to indicate the parent context (matches commit `20a05a4`).
- Layers panel: row for the entered child highlights; parent rows expand if collapsed.

## Side effects
- Undo stack: not affected (selection-only change).
- Subsequent `Cmd A` / `Ctrl A` selects all children of this scope, not all layers in the page (matches commit `4c6eb77`).

## Related UI schema entries
- `regions/canvas-overlays.md` → parent-bounds-overlay, selection-bounding-box
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `enter_frame { frame_id, entered_child_id?, trigger: "double_click" | "enter_key" | "panel_click" }`

## Source articles
- `frames-in-figma-design`
- `parent-child-and-sibling-relationships`
- `select-layers-and-objects`

## Notes / gaps
- Real Figma's "double-click to enter" cascades on already-nested frames — each subsequent double-click goes one level deeper.
- A click outside the frame (or `Esc`) exits scope — see `exit-frame.md`.
