# Delete

- **Category:** clipboard
- **One-line summary:** Remove the current selection from the scene graph.

## Triggers
- Keyboard: `Delete` / `Backspace`.
- Right-click → Delete.
- Layers-panel row `…` menu → Delete (if present).

## Preconditions
- Selection is non-empty.
- Canvas has focus (not in a text input — Delete would delete characters).

## Inputs
- Just the trigger.

## Behavior
1. Remove every selected layer from the scene graph. Children of deleted layers are deleted with their parent.
2. Selection becomes empty.

## Outputs
- **Scene graph changes:** selected layers + subtrees removed.
- **Selection changes:** cleared.
- **Clipboard state:** untouched (unlike Cut).

## UI feedback
- Canvas: layers disappear.
- Left panel: rows removed.
- Right panel: switches to no-selection view.

## Side effects
- Undo stack: one entry; undo restores the deleted layers to their original positions + parents.

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu (Delete entry — functional)

## Semantic event(s) candidate
- `delete { layer_ids: [...], trigger: "keyboard_delete" | "keyboard_backspace" | "context_menu" | "panel_menu" }`

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- Some editors distinguish `Delete` (soft — removes content but keeps container) from `Backspace`; Figma treats them the same for layers.
- "Delete with smart selection" (deletes and reflows) applies only in smart-selection context — smart selection is visual-only in our scope.
