# Double-click to edit text (re-enter edit mode after commit)

- **Category:** text
- **One-line summary:** Re-enter text edit mode on a previously-committed text layer by double-clicking it.

## Triggers
- Selection = text layer (or pointer on a text layer).
- Double-click on the text layer on canvas.
- OR press `Enter` with text layer selected.

## Preconditions
- Text layer exists.

## Inputs
- Pointer double-click OR `Enter` key.

## Behavior
1. Text layer enters edit mode (caret + selection model active).
2. Caret placed at click position (double-click) OR end of text (Enter key).
3. Standard text-edit affordances active (typing, range select, decoration shortcuts, etc.).

## Outputs
- **Scene graph changes:** none on enter; subsequent edits use standard text-edit paths.
- **Selection changes:** sub-selection (caret) within text.
- **Editor state:** text edit mode active.

## UI feedback
- Caret renders inside the text.
- Toolbar / sidebar may swap to text-edit context.

## Side effects
- Undo stack: unaffected by entering edit mode.

## Related UI schema entries
- `regions/canvas-overlays.md` → text-edit-caret

## Semantic event(s) candidate
- `enter_text_edit_mode { layer_id, caret_position?, trigger: "double_click" | "enter_key" }`

## Source articles
- `guide-to-text-in-figma-design`
- `explore-text-properties`

## Notes / gaps
- The user's item 27 ("Edit voxes after completion") translates to this: text layers can be re-edited after creation/commit. The spec covers exactly that flow.
