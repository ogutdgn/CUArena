# Exit frame

- **Category:** frames
- **One-line summary:** Step out of a frame's scope; selection moves up to the parent (or clears).

## Triggers
- `Shift Enter` — selects the parent (per `frames-in-figma-design`).
- `Esc` — clears selection and resets scope to the page root.
- Click on empty canvas outside the frame's bounds.

## Preconditions
- The current scope is inside one or more nested frames.

## Inputs
- Keyboard `Shift Enter` / `Esc` OR pointer click on empty canvas.

## Behavior
1. `Shift Enter`: selection moves up one level — to the parent frame.
2. `Esc` / outside click: scope resets to the page root and selection clears.
3. Hit-testing returns to whole-frame selection (clicks on the frame surface select the frame, not children).

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** selection moves up or clears.
- **Editor state:** scope changes.

## UI feedback
- Parent-bounds overlay disappears (or moves to outer parent).
- Layers panel selection updates.

## Side effects
- Undo stack: unaffected.

## Related UI schema entries
- `regions/canvas-overlays.md` → parent-bounds-overlay
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `exit_frame { from_frame_id, to_parent_id | null, trigger: "shift_enter" | "esc" | "outside_click" }`

## Source articles
- `frames-in-figma-design`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Behavior of `Esc` while a tool is active (e.g. text edit) is tool-specific; this spec covers selection scope only.
