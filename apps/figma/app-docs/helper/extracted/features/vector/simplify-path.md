# Simplify vector path

- **Category:** vector
- **One-line summary:** Reduce the number of vector points on a path while preserving the overall shape (lossy smoothing).

## Triggers
- Selection of vector layer in vector edit mode (or with vector selected) + menu / right-click → **Simplify**.
- Actions menu (`Cmd K`) → "Simplify".

## Preconditions
- A vector layer / vector network selected.

## Inputs
- Menu choice. Per article, may include a slider to set simplification tolerance.

## Behavior
1. Engine reduces redundant or near-collinear vector points using a simplification algorithm.
2. The visual shape stays approximately the same; small details may be lost as tolerance increases.

## Outputs
- **Scene graph changes:** vector network's point list shortened.
- **Selection changes:** none.

## UI feedback
- Canvas: shape redrawn with fewer points.
- (If tolerance slider exists) live preview as user scrubs.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu, actions-menu

## Semantic event(s) candidate
- `simplify_vector_path { layer_ids, tolerance, points_before, points_after, trigger }`

## Source articles
- `simplify-a-vector-path`

## Notes / gaps
- The exact tolerance interface (slider vs preset levels vs single shot) is not enumerated here in detail; treat as a slider with live preview per the article.
