# Variable modes (light/dark, language, etc.)

- **Category:** variables
- **One-line summary:** Each variable collection can have multiple modes; switching modes on a frame retargets all bound variables to that mode's values.

## Triggers
- Variables modal → collection → **Modes** column → add / rename / reorder.
- Frame selected → right sidebar Appearance section → **Apply variable mode** swatch → choose mode.

## Preconditions
- A collection with ≥2 modes.

## Inputs
- Mode-management UI in modal; mode-selection UI per frame.

## Behavior
1. Each variable holds one value per mode (e.g. light/dark colors).
2. A frame's `applied_modes` map specifies which mode it uses per collection.
3. Resolution at render: variable resolution respects the nearest ancestor's `applied_modes`.

## Outputs
- **Scene graph changes:** frame's `applied_modes` updated.
- **Persistent state:** modes added/removed in collection.

## UI feedback
- Frame re-renders with new mode values.

## Side effects
- Undo stack: per change.

## Related UI schema entries
- `regions/floating-overlays.md` → variables-modal
- `regions/right-properties.md` → appearance-section → apply-variable-mode

## Semantic event(s) candidate
- `add_variable_mode { collection_id, mode_id, name }`
- `apply_variable_mode { frame_id, collection_id, mode_id, trigger }`

## Source articles
- `modes-for-variables`
- `extend-a-variable-collection`
- `overview-of-variables-collections-and-modes`
- `variable-modes-in-prototypes`
