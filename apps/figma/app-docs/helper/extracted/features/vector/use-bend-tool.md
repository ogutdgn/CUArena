# Use bend tool (vector edit)

- **Category:** vector
- **One-line summary:** Add bézier handles to a point or path segment to curve straight paths.

## Triggers
- Vector edit mode active.
- Select **Bend** in the secondary toolbar.
- Click on a point or path → bézier handles appear; drag to adjust the curve.

## Preconditions
- Vector edit mode active.
- A vector network exists.

## Inputs
- Pointer click on a point / path segment.
- Drag the bézier handle endpoints.

## Behavior
1. Click a point: handles for that point become editable.
2. Click a path segment: a midpoint handle is added, allowing the segment to bend.
3. Drag handles: adjust length and angle, producing a curve.
4. Handle mirroring options (per `edit-vector-layers`):
   - **No mirroring** — handles independent.
   - **Mirror angle** — opposite handle mirrors angle only.
   - **Mirror angle and length** — opposite handle mirrors both.
5. `Shift` + select handles + drag — moves both in the same direction.

## Outputs
- **Scene graph changes:** vector network's point handles updated.
- **Selection changes:** none.

## UI feedback
- Bézier handles render on the active point; canvas redraws curve.

## Side effects
- Undo stack: one entry per drag commit.

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → bend
- `regions/right-properties.md` → vector-edit-mode mirror-handle settings

## Semantic event(s) candidate
- `set_bezier_handle { layer_id, point_index, handle_side: "in" | "out", from, to, mirror_mode, trigger }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- Mirror mode setting also covered separately by `edit-vector-mirror-handles.md`.
