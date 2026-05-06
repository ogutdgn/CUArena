# Detach instance

- **Category:** components
- **One-line summary:** Convert an instance into an independent layer hierarchy that no longer follows the main component.

## Triggers
- Selected instance → right-click → **Detach instance**.
- Shortcut: `⌥ ⌘ B` (Mac) / `Ctrl Alt B` (Win).

## Preconditions
- An instance selected.

## Inputs
- Shortcut OR menu choice.

## Behavior
1. Instance's `main_id` removed; node becomes a regular frame/group with the same content.
2. Future updates to the main do not propagate to this layer.
3. Existing overrides become permanent property values.

## Outputs
- **Scene graph changes:** instance node converted; main reference and override-state cleared.
- **Selection changes:** none.

## UI feedback
- Layers panel: diamond icon → standard frame/group icon.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `detach_instance { instance_id, trigger }`

## Source articles
- `detach-an-instance-from-the-component`
