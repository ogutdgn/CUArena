# Edit boolean group

- **Category:** boolean
- **One-line summary:** Boolean operations are non-destructive — children of a boolean group can still be selected and modified for position, dimensions, rotation, corner radius.

## Triggers
- Double-click into a boolean group on canvas to enter scope (or use Layers panel).
- Right-click on the group → **Ungroup** to break it back into individual objects.

## Preconditions
- A boolean group exists.

## Inputs
- Pointer click / double-click / Ungroup action.

## Behavior
1. Children are still individual layers and can be moved, resized, rotated, given a different corner radius.
2. **Per-child fill / stroke / effects / opacity are NOT independently editable** — those properties are taken from the boolean group as a whole (top or bottom layer rules per op).
3. Result re-computes whenever child geometry changes.
4. **Ungroup** restores original individual layers (and discards the boolean group).

## Outputs
- **Scene graph changes:** depends — re-computed on child geometry change; ungroup deletes the group node and releases children.
- **Selection changes:** none / changes on ungroup.

## UI feedback
- Canvas re-renders the boolean result on every child change.
- Layers panel: group expandable to show children.

## Side effects
- Undo stack: standard per-action.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu → Ungroup

## Semantic event(s) candidate
- `move_boolean_child { layer_id, ... }`  // delegates to standard move with re-compute side effect
- `ungroup_boolean_group { group_id, child_ids: [...] }`

## Source articles
- `boolean-operations`

## Notes / gaps
- Ungroup of a boolean group uses the same shortcut as group-ungroup (`⌘ ⇧ G` / `Ctrl Shift G`).
