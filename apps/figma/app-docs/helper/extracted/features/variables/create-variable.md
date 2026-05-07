# Create variable

- **Category:** variables
- **One-line summary:** Define a named token (color, number, string, or boolean) reusable across designs and prototypes.

## Triggers
- Right sidebar (no selection) → **Local variables** section → **+** to create.
- Color picker → save-as-variable flow (`save-as-color-style.md` covers the variable-creation path).

## Preconditions
- Edit access to file.

## Inputs
- Variable type (color, number, string, boolean).
- Name (supports `/`-separated grouping).
- Default value (or per-mode values if collection has modes).
- Description (optional).
- Scope hints (where it can be applied).

## Behavior
1. Variable created in a collection (default collection if not specified).
2. Available immediately in pickers (color picker → Libraries tab; number/string inputs).

## Outputs
- **Persistent file state:** new variable stored in collection.

## UI feedback
- Local variables modal lists the new entry.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/floating-overlays.md` → variables-modal

## Semantic event(s) candidate
- `create_variable { collection_id, variable_id, type, name, default_value, scope }`

## Source articles
- `create-and-manage-variables-and-collections`
- `guide-to-variables-in-figma`
- `overview-of-variables-collections-and-modes`
