# Apply variable to property

- **Category:** variables
- **One-line summary:** Bind a property (color, number, string, boolean) to a variable so it follows the variable's resolved value (and any mode switches).

## Triggers
- Right sidebar property field → **Apply variable** icon (small dot/diamond icon).
- Color picker → Libraries tab → click variable swatch (per `library-colors-browser.md`).

## Preconditions
- Property type matches variable type.

## Inputs
- Pointer click → variable picker opens → choose variable.

## Behavior
1. Property's value becomes a binding `{ variable_id }`.
2. Renderer resolves to the variable's value at render time, in the active mode.
3. Detach: remove the binding, restoring the resolved value as the literal.

## Outputs
- **Scene graph changes:** property's binding object updated.
- **Selection changes:** none.

## UI feedback
- Field shows variable chip.

## Side effects
- Undo stack: one entry per apply.

## Related UI schema entries
- `regions/right-properties.md` → property field → apply-variable icon
- `regions/floating-overlays.md` → variable-picker

## Semantic event(s) candidate
- `apply_variable { layer_ids, property, variable_id, trigger }`
- `detach_variable { layer_ids, property, trigger }`

## Source articles
- `apply-variables-to-designs`
- `guide-to-variables-in-figma`
