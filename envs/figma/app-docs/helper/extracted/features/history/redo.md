# Redo

- **Category:** history
- **One-line summary:** Re-apply the last undone operation.

## Triggers
- Keyboard: `Cmd Shift Z` (Mac) / `Ctrl Shift Z` or `Ctrl Y` (Windows).
- Main menu → Edit → Redo.

## Preconditions
- Redo stack is non-empty.

## Inputs
- Just the trigger.

## Behavior
1. Pop the top entry from the redo stack.
2. Re-apply the original operation to the scene graph.
3. Push the entry back onto the undo stack.

Redo stack is cleared whenever a new (non-undo) operation is performed — standard editor semantics.

## Outputs
- **Scene graph changes:** re-applies the original op.
- **Selection / mode:** restored to the post-op state (before it was undone).
- **Stack state:** redo shrinks by 1; undo grows by 1.

## UI feedback
- Canvas: content returns to the pre-undo state.
- Panels update.

## Side effects
- Clipboard: untouched.

## Related UI schema entries
- None directly.

## Semantic event(s) candidate
- `redo { reapplied_op_name, trigger: "shortcut" | "main_menu" }`

## Source articles
- No dedicated article; universal editor behavior.

## Notes / gaps
- Redo stack is cleared on any new user op (not on undo itself). Standard behavior.
