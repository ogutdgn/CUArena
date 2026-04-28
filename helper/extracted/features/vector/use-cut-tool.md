# Use cut tool (vector edit)

- **Category:** vector
- **One-line summary:** Divide vector paths or split a vector object by clicking a point/path or drag-cutting through paths.

## Triggers
- Vector edit mode + secondary toolbar **Cut** OR shortcut `X`.

## Preconditions
- Vector edit mode active.
- A vector layer with at least one path.

## Inputs
- **Click** on a point or path → creates a break at that location.
- **Click + drag** across one or more paths → divides the object; the divided portion moves to its own layer.

## Behavior
- Click splits a path at the click point (insert break/segment ending).
- Drag-cut creates a path that splits everything it crosses; the split-off region becomes a new layer.

## Outputs
- **Scene graph changes:** vector network gains a break OR a new vector layer is created with the divided region.
- **Selection changes:** post-cut selection = the new layer (drag mode) or the original (click mode).

## UI feedback
- Cursor changes to a cut icon.
- Cut path renders on canvas as the user drags.

## Side effects
- Undo stack: one entry per cut.

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → cut

## Semantic event(s) candidate
- `cut_vector_path { layer_id, cut_kind: "click_break" | "drag_divide", cut_path, result_layer_ids?, trigger }`

## Source articles
- `edit-vector-layers`
