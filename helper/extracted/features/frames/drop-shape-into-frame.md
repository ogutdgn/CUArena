# Drop shape into frame (creation-time)

- **Category:** frames
- **One-line summary:** When creating a new shape via drag inside a frame's bounds, the new shape becomes a child of that frame.

## Triggers
- Tool-active (Rectangle / Ellipse / Line / Polygon / Star / Arrow / Frame / Text / Pen).
- Pointer-down + drag inside a frame's bounds.

## Preconditions
- A shape-creation tool is active.
- The drag region overlaps an existing frame's bounds.

## Inputs
- Pointer-down + drag inside a frame.
- Optional `Space bar` modifier to suppress reparenting (per `parent-child-and-sibling-relationships`).

## Behavior
1. On drag-release, the new shape's bbox is computed.
2. If the bbox is fully within (or sufficiently overlapping — see `reparent-via-canvas-drag.md`) a frame, the shape's parent is that frame.
3. The shape's coordinates are stored relative to the frame.
4. If `Space` was held during drag, the shape is created on the canvas root regardless of overlap.

## Outputs
- **Scene graph changes:** new shape with `parent_id` set to the enclosing frame.
- **Selection changes:** selection = new shape.

## UI feedback
- Layers panel: new shape appears nested under the frame.
- Canvas: standard creation outline + selection box on the new shape.

## Side effects
- Undo stack: one entry — the shape creation, including the parent assignment.

## Related UI schema entries
- `regions/canvas-overlays.md` → insertion-crosshair, parent-bounds-overlay
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `create_shape_in_frame { shape_type, parent_frame_id, bbox, modifiers, trigger: "tool_drag" }`

## Source articles
- `parent-child-and-sibling-relationships`
- `frames-in-figma-design`
- `shape-tools`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- The article frames-in-figma-design says: "Click inside an existing frame to add a 100 x 100 nested frame." (for the Frame tool). For other shape tools the same pattern holds — drag inside a frame creates a nested child.
