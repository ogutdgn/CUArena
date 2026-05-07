# Reparent via canvas drag

- **Category:** frames
- **One-line summary:** Drag a layer over another frame on the canvas; if its bounding box overlaps the frame past the threshold, it becomes a child of that frame live during the drag.

## Triggers
- Pointer drag of a layer.
- During drag, the layer's bbox enters/exits a frame's bounds with sufficient overlap.

## Preconditions
- A layer is being moved on the canvas.
- Another frame exists under the moving layer's path.

## Inputs
- Pointer drag (move-tool).
- Optional `Space bar` modifier — keep object in current parent (override auto-reparent).

## Behavior
1. As the user drags a layer, the engine continuously evaluates which frame (if any) should be its parent.
2. Default rule (per `parent-child-and-sibling-relationships`):
   - If the dragged object is **smaller** than a frame and overlaps it, the frame becomes the new parent.
   - If the dragged object is **larger** than a frame, no reparenting.
3. Mock implementation uses a 50% overlap threshold (per commit `4413ce0` and `74c4896`): the layer reparents during drag once its bbox overlaps the candidate frame by ≥ 50% in area.
4. Reparenting is live: the layer's `parent_id` updates as soon as the threshold is crossed; subsequent drag movement is in the new parent's local space.
5. `Space bar` held during drag suppresses reparenting (locks current parent).
6. On drag-release, the final parent is whichever satisfied the threshold at release.

## Outputs
- **Scene graph changes:** `parent_id` updates (possibly multiple times during one drag); layer's local X/Y converts to the new parent's coordinate space each time.
- **Selection changes:** none (still on the moving layer).

## UI feedback
- Canvas: dashed parent-bounds overlay highlights the candidate parent (matches commit `20a05a4`).
- Layers panel: layer row moves to under the new parent in real time.

## Side effects
- Undo stack: one entry per drag, capturing the final parent and final position.
- The 50% overlap rule: documented for the mock; real Figma's rule is "smaller overlaps frame" without an explicit percent; mock standardizes on 50%.

## Related UI schema entries
- `regions/canvas-overlays.md` → parent-bounds-overlay, selection-bounding-box
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `reparent_layer { layer_id, from_parent_id, to_parent_id | null, trigger: "canvas_drag", overlap_at_release }`
- During drag, intermediate reparents may emit `reparent_layer_preview` (or be silent — engine choice; coalesce to one final on release).

## Source articles
- `parent-child-and-sibling-relationships`
- `frames-in-figma-design`

## Notes / gaps
- Threshold of 50% is mock-specific; real Figma's heuristic is not documented numerically.
- Multi-select reparent: each layer reparents independently per the same rule (largest+smaller mix can split).
