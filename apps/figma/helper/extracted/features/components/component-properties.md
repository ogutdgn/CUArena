# Component properties (variants, boolean, instance swap, text)

- **Category:** components
- **One-line summary:** Define editable per-instance properties on a main component — boolean, text, instance-swap, variant — exposed as controls on each instance.

## Triggers
- Main component selected → right sidebar Component section → **Properties** add `+` icon → choose property type.

## Preconditions
- A main component selected.

## Inputs
- Property type: **Variant**, **Boolean**, **Text**, **Instance swap**.
- Field name + default value.

## Behavior
1. Property is stored on the main; each instance shows controls for the configured properties.
2. Instances inherit defaults; can override per-instance.
3. **Variant** group properties become a multi-axis variant matrix (see `create-and-use-variants`).
4. **Slots** are an additional concept layered on instance-swap to standardize swapping with placeholder content (see `use-slots-to-build-flexible-components-in-figma`).

## Outputs
- **Scene graph changes:** main's `properties` array updated; per-instance overrides accept these as fields.
- **Selection changes:** none.

## UI feedback
- Right sidebar Component section shows property list.

## Side effects
- Undo stack: per-property change.

## Related UI schema entries
- `regions/right-properties.md` → component-section → properties

## Semantic event(s) candidate
- `add_component_property { component_id, property_id, type, default }`
- `set_instance_property { instance_id, property_id, from, to, trigger }`

## Source articles
- `explore-component-properties`
- `edit-instances-with-component-properties`
- `create-and-use-variants`
- `use-slots-to-build-flexible-components-in-figma`
- `migrate-a-library-to-using-slots`
- `the-difference-between-slots-instance-swaps-and-variants`
