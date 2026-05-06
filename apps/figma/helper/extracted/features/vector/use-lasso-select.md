# Use lasso select (vector edit)

- **Category:** vector
- **One-line summary:** Free-form select vector points and segments by drawing a lasso shape around them.

## Triggers
- Vector edit mode + secondary toolbar **Lasso** OR shortcut `Q`.
- Click and drag to draw a lasso path.

## Preconditions
- Vector edit mode active.

## Inputs
- Pointer drag describing a closed shape.

## Behavior
1. Engine selects all vector points whose positions are inside the lasso shape.
2. Selected points show selection styling.
3. After selection, can manipulate or delete the selected points.

## Outputs
- **Scene graph changes:** none (selection only).
- **Selection changes:** vector-point sub-selection updated.

## UI feedback
- Lasso path renders during drag.
- Selected points highlight.

## Side effects
- Undo stack: unaffected (selection-only).

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → lasso

## Semantic event(s) candidate
- `lasso_select_vector_points { layer_id, lasso_path, selected_point_indices: [...], trigger }`

## Source articles
- `edit-vector-layers`
