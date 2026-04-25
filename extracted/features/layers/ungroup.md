# Ungroup

- **Category:** layers
- **One-line summary:** Remove the wrapping group layer, reparenting its children to the group's parent.

## Triggers
- Keyboard: `Cmd Shift G` (Mac) / `Ctrl Shift G` (Windows).
- Right-click → Ungroup.

## Preconditions
- Selection contains at least one group layer. (If a frame is selected and `Cmd Shift G` pressed, behavior differs — typically only ungroups groups; frames do not ungroup this way.)

## Inputs
- Just the trigger.

## Behavior
1. For each selected group: move its children up to the group's parent, preserving their internal order and positions.
2. Delete the group layer.
3. Selection becomes the former children of the group(s).

## Outputs
- **Scene graph changes:** group layer(s) removed; their children reparented.
- **Selection changes:** selection = former children.

## UI feedback
- Left panel: group row removed; children appear at the parent level.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu

## Semantic event(s) candidate
- `ungroup { group_layer_ids, child_layer_ids, trigger: "shortcut" | "context_menu" }`

## Source articles
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Ungroup on a frame: real Figma does not ungroup frames this way (frames are not considered groups). Handle explicitly — no-op on frame selection.
