# Offset vector path

- **Category:** vector
- **One-line summary:** Expand or contract a vector path along its normals by a specified distance.

## Triggers
- Vector selection + menu → **Offset path** (also accessible via Actions menu / `Cmd K`).

## Preconditions
- A vector layer selected.

## Inputs
- Numeric offset value (positive = outward, negative = inward).

## Behavior
1. Each segment is offset perpendicular to the path by the entered distance.
2. The resulting path replaces the original (or creates a copy — confirm with article).
3. Self-intersections may occur for high offsets; handled by the engine's standard offset algorithm.

## Outputs
- **Scene graph changes:** vector network points and segments updated to the offset path.
- **Selection changes:** none.

## UI feedback
- Canvas: shape grows/shrinks along its normals.
- (If a modal exists) preview as user types.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → offset-path-modal (if implemented)

## Semantic event(s) candidate
- `offset_vector_path { layer_ids, distance, trigger }`

## Source articles
- `offset-a-vector-path`

## Notes / gaps
- Whether the result replaces the source or creates a duplicate is not pinned in the spec excerpt — confirm in source article.
