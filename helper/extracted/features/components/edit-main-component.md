# Edit main component

- **Category:** components
- **One-line summary:** Open a component's main definition; changes propagate to all instances.

## Triggers
- From an instance: right-click → **Go to main component** (or shortcut from the source article).
- Navigate directly to the main in the Layers panel.

## Preconditions
- An instance selected (for the navigation flow).

## Inputs
- Right-click navigation OR direct selection.

## Behavior
1. Editor jumps to the main component's location and selects it.
2. Editing the main (geometry, fills, child structure) propagates to every instance.
3. Instances may show "Reset overrides" when their overrides conflict with main changes.

## Outputs
- **Scene graph changes:** main component edited; instances re-render.
- **Selection changes:** selection moves to main component.

## UI feedback
- Layer panel highlights the main; canvas zooms there.

## Side effects
- Undo stack: per-edit entries on the main.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `navigate_to_main_component { instance_id, main_id, trigger }`

## Source articles
- `edit-main-components`
- `apply-changes-to-instances`
- `move-published-components`
