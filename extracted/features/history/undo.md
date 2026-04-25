# Undo

- **Category:** history
- **One-line summary:** Revert the last undoable operation.

## Triggers
- Keyboard: `Cmd Z` (Mac) / `Ctrl Z` (Windows).
- Main menu → Edit → Undo (if rendered).

## Preconditions
- Undo stack is non-empty.

## Inputs
- Just the trigger.

## Behavior
1. Pop the top entry from the undo stack.
2. Apply its inverse operation to the scene graph.
3. Push the entry onto the redo stack.
4. Restore selection and possibly other state (caret position, mode) to what it was before the undone operation, to the extent the entry captured them.

## Outputs
- **Scene graph changes:** whatever the inverse operation dictates (layer restored, property reverted, etc.).
- **Selection changes:** typically restored to pre-op state.
- **Mode state changes:** may restore (e.g., if operation included entering/exiting a mode).
- **Stack state:** undo shrinks by 1; redo grows by 1.

## UI feedback
- Canvas: reverts to prior state.
- Left panel / right panel: update accordingly.
- Optional toast (rarely): "Undone" — `plan/03` decides.

## Side effects
- Clipboard: untouched.

## Related UI schema entries
- None directly — this is a global operation.

## Semantic event(s) candidate
- `undo { reverted_op_name, trigger: "shortcut" | "main_menu" }`
- Engine may also emit the "reverse" of the prior op (e.g., if undoing a `create_rectangle`, emit a `delete { source: "undo" }`). `plan/03` decides whether to emit the reverse op or just the `undo` event — likely both, with `source: "undo"` on the derived op so CUA can tell it's undo-driven.

## Source articles
- No dedicated undo article in the corpus; `workflows.md` and several feature articles mention Ctrl+Z. Treat as universal editor behavior.

## Notes / gaps
- Stack depth limit: real Figma has a large but finite undo depth. Pick a reasonable cap (e.g., 1000 entries).
- Coalescing rules (typing burst, color-picker scrubbing) discussed per-feature. Stack-level behavior pops one "coalesced entry" per Cmd Z.
