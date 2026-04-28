# Group selection

- **Category:** layers
- **One-line summary:** Wrap the current selection in a new group container.

## Triggers
- Keyboard: `Cmd G` (Mac) / `Ctrl G` (Windows).
- Right-click → Group selection.

## Preconditions
- Selection contains 1+ layers.
- Canvas has focus.

## Inputs
- Just the trigger.

## Behavior
1. Compute bounding box of selection (used only for layer ordering — group itself has no fixed bounds; its bounds derive from children).
2. Create a new group layer at the parent of the topmost selected layer (all selected layers share a parent path up to their common ancestor — group is created at that level).
3. Move the selected layers into the new group as children, preserving their internal order and positions.
4. Selection becomes the new group.

## Outputs
- **Scene graph changes:** one new group layer; selected layers reparented into it.
- **Selection changes:** selection = new group.

## UI feedback
- Canvas: bounding box now frames the group (whose bounds are children's union).
- Left panel: new group row inserted; selected layers nested under it.
- Right panel: Group selection view (per `state-matrix.md`).

## Side effects
- Undo stack: one entry; undo restores original layer parents and removes the group.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree
- `regions/floating-overlays.md` → right-click-context-menu
- `state-matrix.md` → Group row

## Semantic event(s) candidate
- `group_selection { source_layer_ids, new_group_id, trigger: "shortcut_cmd_g" | "context_menu" }`

## Source articles
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Common-ancestor rule: if selected layers are in different parents, Figma moves them to a common ancestor before grouping. Edge case — may be rare in practice but should be handled.
