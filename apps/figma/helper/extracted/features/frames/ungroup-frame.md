# Ungroup frame

- **Category:** frames
- **One-line summary:** Remove a frame and promote its children to the frame's parent (canvas root or outer frame), preserving their on-canvas positions.

## Triggers
- Selection = frame, then:
  - Mac: `⌘ Shift G` or `⌘ Backspace`.
  - Windows: `Ctrl Shift G` or `Ctrl Backspace`.
- Right-click → **Ungroup** (when context menu is opened on a frame).

## Preconditions
- A frame is selected.

## Inputs
- Keyboard shortcut OR menu choice.

## Behavior
1. Frame is removed from the scene graph.
2. Each child's `parent_id` becomes the frame's former parent.
3. Children's coordinates are converted from frame-local to outer-parent-local so their on-canvas positions are unchanged.
4. Frame-only properties (clip content, layout guides, fill on the frame, auto-layout settings) are discarded — children do not inherit them.

## Outputs
- **Scene graph changes:** frame deleted; children reparented to frame's previous parent; coords updated.
- **Selection changes:** selection becomes the previously-children layers (multi-select).

## UI feedback
- Layers panel: frame row removed; children promoted up one level.
- Canvas: visual unchanged for the children themselves; the frame's own fill/border vanish.

## Side effects
- Undo stack: one entry covering the un-frame.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu → Ungroup
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `ungroup_frame { frame_id, child_ids: [...], to_parent_id, trigger: "shortcut" | "context_menu" }`

## Source articles
- `frames-in-figma-design`
- `the-difference-between-frames-and-groups`

## Notes / gaps
- Same shortcut works for groups (ungroup); behavior is symmetric.
