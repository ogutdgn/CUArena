# Add vector point (in edit mode)

- **Category:** vector
- **One-line summary:** Insert a new anchor point into an existing vector network while in vector edit mode.

## Triggers
- Click on an existing path segment (between two points) while Pen is active in vector-edit mode.
- Click in empty space while Pen is active in vector-edit mode → adds a new disconnected point OR extends from the last-selected point.

## Preconditions
- User is in vector-edit mode.
- Pen tool (or compatible) is active.

## Inputs
- Pointer click position.

## Behavior

**Click on segment:**
1. Compute the point on the segment nearest the click.
2. Insert an anchor point there, splitting the segment into two new segments.
3. New anchor inherits smooth or corner type per neighboring handles (engine decision).

**Click in empty space with a point selected:**
1. Extend from the selected point: create a new segment connecting to a new anchor at the click position.

## Outputs
- **Scene graph changes:** vector layer's `points` array has a new entry; affected segments updated.

## UI feedback
- Canvas: new anchor visible; segment now renders with the new point in its path.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode (Pen sub-tool)

## Semantic event(s) candidate
- `add_vector_point { layer_id, point_index, position: {x, y}, source: "segment_insert" | "extend_from_selected" }`

## Source articles
- `edit-vector-layers`
- `vector-networks`

## Notes / gaps
- Closest-point-on-segment algorithm: standard bezier sampling + distance minimization. Implementation detail.
