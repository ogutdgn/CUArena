# Set child absolute position (ignore auto-layout)

- **Category:** auto-layout
- **One-line summary:** Pull a child out of the auto-layout flow so it positions absolutely within its parent — useful for tooltips, badges, overlays.

## Triggers
- Child of auto-layout frame selected → right sidebar **Position** section → **Ignore auto layout** icon (sometimes labeled "Absolute position").

## Preconditions
- Child of auto-layout frame.

## Inputs
- Click toggle.

## Behavior
1. Child's `absolute_position` flag set true.
2. Child no longer participates in flow; X / Y are explicitly editable.
3. Constraints (`set-constraints.md`) apply to the absolute child relative to the auto-layout parent.
4. Toggle off: child re-joins the flow at the next index.

## Outputs
- **Scene graph changes:** child's `absolute_position` flag toggled.
- **Selection changes:** none.

## UI feedback
- Position section gains X/Y inputs and constraints.
- Canvas: child positioned absolutely.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → ignore-auto-layout icon

## Semantic event(s) candidate
- `set_absolute_position { layer_id, to_state, trigger: "panel_button" }`

## Source articles
- `guide-to-auto-layout`
