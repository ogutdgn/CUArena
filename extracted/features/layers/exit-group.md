# Exit group / frame

- **Category:** layers
- **One-line summary:** Leave the current group / frame context back out to the parent.

## Triggers
- Keyboard: `Esc`.
- Keyboard: `Shift Enter`.
- Click outside the container's bounds on canvas.

## Preconditions
- User is currently "inside" a group / frame context (entered via `enter-group`).

## Inputs
- Just the trigger.

## Behavior
1. Move the active context up one level.
2. If the user was inside multiple nested contexts, a single Esc moves out by one level (repeatable).
3. At the top level, Esc with a selection may additionally deselect; without selection it is a no-op.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** may shift to the container (after exiting into its parent).
- **Mode state change:** "current context" moves one level up.

## UI feedback
- Canvas: dashed parent-bounds overlay moves out.
- Left panel: tree focus updates.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → dashed-parent-bounds

## Semantic event(s) candidate
- `exit_group { from_container_id, to_parent_id, trigger: "escape" | "shift_enter" | "click_outside" }`

## Source articles
- `parent-child-and-sibling-relationships`
- `select-layers-and-objects`

## Notes / gaps
- Interaction with `deselect`: if `Esc` both exits a context AND deselects, decide order (exit first; only deselect at top-level).
