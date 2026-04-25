# Exit vector edit mode

- **Category:** vector
- **One-line summary:** Leave vector edit mode and restore the main toolbar.

## Triggers
- Keyboard: `Enter` while in vector edit mode.
- Keyboard: `Esc`.
- Click "Done" button in the vector-edit secondary toolbar.

## Preconditions
- User is currently in vector edit mode.

## Inputs
- Just the trigger.

## Behavior
1. Exit vector edit mode; restore main toolbar.
2. Selection remains the vector layer (in normal selection mode).
3. Any uncommitted edits are saved.

## Outputs
- **Scene graph changes:** none (edits were committed as they happened).
- **Mode state change:** `editMode = null`; previous main-toolbar state restored.

## UI feedback
- Toolbar: swaps back to main toolbar.
- Canvas: anchor points + handles disappear; layer shown with normal bounding box.

## Side effects
- Undo stack: none directly for exiting.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode (Done button)

## Semantic event(s) candidate
- `exit_vector_edit_mode { layer_id, trigger: "enter_key" | "escape" | "done_button" }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- None.
