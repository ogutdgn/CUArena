# Variable collections

- **Category:** variables
- **One-line summary:** Group related variables into a collection (e.g. "Theme", "Spacing"); collections own modes and scope settings.

## Triggers
- Variables modal → **+** new collection.

## Preconditions
- Edit access.

## Inputs
- Collection name.
- Initial modes (default: 1 mode named "Mode 1").

## Behavior
1. Each variable lives in exactly one collection.
2. Collection-wide modes apply to every variable in the collection.
3. Renaming, reordering modes affects all consumers.

## Outputs
- **Persistent state:** collection added.

## UI feedback
- Modal lists collections in left rail.

## Side effects
- Undo stack: per change.

## Related UI schema entries
- `regions/floating-overlays.md` → variables-modal → collections rail

## Semantic event(s) candidate
- `create_variable_collection { collection_id, name }`
- `delete_variable_collection { collection_id, cascading_changes }`

## Source articles
- `create-and-manage-variables-and-collections`
- `overview-of-variables-collections-and-modes`
- `extend-a-variable-collection`
