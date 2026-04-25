# Enter vector edit mode

- **Category:** vector
- **One-line summary:** Enter a dedicated mode for editing a vector network's points, handles, and sub-paths.

## Triggers
- Keyboard: `Enter` while a vector layer is selected.
- Double-click on a vector layer on canvas.
- Right-click → Edit object (or equivalent entry).

## Preconditions
- Selection is a single vector layer.

## Inputs
- Just the trigger.

## Behavior
1. Enter vector edit mode.
2. Main toolbar is replaced by the vector-edit secondary toolbar (Move / Pen / Bend / Lasso / Cut / Paint / Variable width / Shape builder / Done — see `regions/toolbar.md` → secondary toolbar).
3. Canvas displays anchor points and handles of the vector.
4. Clicks on the canvas are now interpreted as point-editing operations.

## Outputs
- **Scene graph changes:** none.
- **Mode state change:** `editMode = "vector"` active; previous tool remembered for restoration on exit.

## UI feedback
- Toolbar: swaps to vector-edit variant.
- Canvas: vector's anchor points + handles become visible (points as squares, handles as round endpoints with thin connecting lines).
- Right panel: reduced set of properties (engine decision; may continue showing Stroke / Fill; Layout sections less relevant in edit mode).

## Side effects
- Undo stack: no entry for entering mode.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode

## Semantic event(s) candidate
- `enter_vector_edit_mode { layer_id, trigger: "enter_key" | "double_click_canvas" | "context_menu" }`

## Source articles
- `edit-vector-layers`
- `vector-networks`

## Notes / gaps
- Vector edit mode vs enter-group mode: these are distinct. Vector edit exposes point-level tools; enter-group just scopes clicks to children. Engine must distinguish.
