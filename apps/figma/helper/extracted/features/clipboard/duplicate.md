# Duplicate

- **Category:** clipboard
- **One-line summary:** Duplicate the current selection in place (with a small offset) without touching the clipboard.

## Triggers
- Keyboard: `Cmd D` (Mac) / `Ctrl D` (Windows).
- `Alt/Option` + drag a selection — creates a duplicate at the drag position (a different trigger path; same semantic effect).
- Right-click → Duplicate (if rendered).

## Preconditions
- Selection is non-empty.

## Inputs
- Just the trigger.
- For Alt-drag: pointer delta.

## Behavior

**Shortcut path (`Cmd D`):**
1. Deep-clone each selected layer.
2. Offset each clone by a small amount (commonly `+10, +10` px, or the last "smart duplicate" offset if user has recently moved a duplicate — `Cmd D` repeated after a manual move aligns with the manual delta).
3. Insert clones as siblings of the original.
4. Selection becomes the clones.

**Alt-drag path:**
1. Pointer-down on selected layer + Alt held: record start state.
2. Pointer-move: create a duplicate of the selection and move it along with the pointer (original stays in place).
3. Pointer-up: commit the duplicate at the drop position.

## Outputs
- **Scene graph changes:** N new layer(s), each a deep clone of a selected layer.
- **Selection changes:** selection = new duplicates.
- **Clipboard state:** untouched.

## UI feedback
- Canvas: duplicates appear; for shortcut path, offset by default ~10px.
- Left panel: new rows added.

## Side effects
- Undo stack: one entry per commit.
- "Smart duplicate" state: after a `Cmd D` + manual move, subsequent `Cmd D` repeats the offset (typically tracked in engine as the last-used duplicate delta).

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu

## Semantic event(s) candidate
- `duplicate { source_layer_ids: [...], new_layer_ids: [...], offset: {dx, dy}, trigger: "shortcut_cmd_d" | "alt_drag" | "context_menu" }`
- Alt-drag emits `duplicate` with `trigger: "alt_drag"` — and may also emit a `move_layer` immediately after for the drag portion. `plan/03` decides coupling.

## Source articles
- `copy-and-paste-objects`
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Smart-duplicate offset behavior (Figma tracks the last manual move delta and reapplies on subsequent `Cmd D`) is a subtle but user-facing feature. Worth implementing in the engine.
- Alt-drag vs plain drag is critical for CUA trajectory testing: the logger must clearly distinguish "drag_move" (with no copy) from "alt_drag_duplicate" (with copy creation).
