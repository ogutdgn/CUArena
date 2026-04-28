# Create variants (component sets)

- **Category:** components
- **One-line summary:** Group multiple components as variants of one component-set, configurable via property axes (e.g. "Size" × "State").

## Triggers
- Two or more components selected → right sidebar Component section → **Combine as variants**.
- Adding a variant to an existing component set: select the set → **Add variant** (or duplicate).

## Preconditions
- 2+ main components selected (for combine path) OR an existing component set (for add path).

## Inputs
- Pointer click on combine / add.

## Behavior
1. Components wrap into a component-set (parent node), with each variant's property values inferred from name (e.g. `Size=Small, State=Default`).
2. Variants share a property schema; instance UI exposes dropdowns to switch.
3. Interactive components can use variant transitions in Prototype mode.

## Outputs
- **Scene graph changes:** new component-set node containing the variants.
- **Selection changes:** selection = component set.

## UI feedback
- Layers panel: dashed bounding box around the variant set.
- Right sidebar shows variant property list.

## Side effects
- Undo stack: per-action.

## Related UI schema entries
- `regions/right-properties.md` → component-section → variants

## Semantic event(s) candidate
- `create_variant_set { component_ids, set_id }`
- `add_variant { set_id, new_variant_id, properties }`
- `set_instance_variant_property { instance_id, axis, from, to }`

## Source articles
- `create-and-use-variants`
- `create-interactive-components-with-variants`
- `the-difference-between-slots-instance-swaps-and-variants`
