# Swap component instance

- **Category:** components
- **One-line summary:** Replace an instance with another component while preserving overrides where compatible.

## Triggers
- Selected instance → right sidebar Component section → component-name dropdown → **Swap instance**.
- Right-click instance → **Swap instance**.

## Preconditions
- Instance selected.

## Inputs
- Pointer click → list of available components → choose target.

## Behavior
1. Instance's `main_id` points to the new component.
2. Overrides (text content, fills, etc.) carry across when names match.
3. Layout / position retained.

## Outputs
- **Scene graph changes:** instance's main reference updated; overrides re-mapped.

## UI feedback
- Canvas re-renders with new component visuals.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → component-section → swap-dropdown

## Semantic event(s) candidate
- `swap_instance { instance_id, from_main_id, to_main_id, trigger }`

## Source articles
- `swap-components-and-instances`
- `the-difference-between-slots-instance-swaps-and-variants`
