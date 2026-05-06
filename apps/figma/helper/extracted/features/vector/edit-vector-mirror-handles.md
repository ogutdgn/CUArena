# Edit vector mirror handles (mirroring modes)

- **Category:** vector
- **One-line summary:** Configure how a vector point's two bézier handles mirror each other — independent, mirror angle, or mirror angle and length.

## Triggers
- Vector edit mode active with a vector point selected.
- Mirror mode setting in the right sidebar (vector-edit context section).

## Preconditions
- Vector edit mode active.
- A vector point with bézier handles selected.

## Inputs
- Click on the mirroring mode option:
  - **No mirroring** — handles independent.
  - **Mirror angle** — opposite handle mirrors the angle of the selected handle.
  - **Mirror angle and length** — opposite mirrors both.

## Behavior
1. Mode is per-point (each point has its own mirror setting).
2. Changing mode immediately re-renders the curve.
3. With mirror modes set, dragging one handle automatically updates the opposite per the mode.
4. To move both handles in the same direction, `Shift` + select each + drag one.

## Outputs
- **Scene graph changes:** point's `mirror_mode` updated; opposite handle may snap to mirror.
- **Selection changes:** none.

## UI feedback
- Right sidebar shows the current mode.
- Canvas: handles snap to mirrored positions immediately.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → vector-edit-mode → mirror-handles section

## Semantic event(s) candidate
- `set_vector_point_mirror_mode { layer_id, point_index, from_mode, to_mode, trigger }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- Cross-cuts with `vector/use-bend-tool.md` (which adds the bezier handles in the first place).
