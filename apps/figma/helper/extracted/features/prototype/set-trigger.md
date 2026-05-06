# Set prototype trigger

- **Category:** prototype
- **One-line summary:** Choose what user gesture initiates a connection's action — On click / On drag / While hovering / While pressing / Mouse enter / Mouse leave / Mouse down / Mouse up / After delay / Key/gamepad / etc.

## Triggers
- Connection selected → right sidebar Prototype panel → Trigger dropdown.

## Preconditions
- A prototype connection exists.

## Inputs
- Choose trigger type from dropdown.

## Behavior
- Each trigger type listens for a specific gesture in the running prototype.
- "After delay" includes a delay-ms input.
- "Key/gamepad" lets you specify a key code or button.

## Outputs
- **Scene graph changes:** connection's `trigger_type` updated.

## UI feedback
- Connection arrow may render different style per trigger.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → prototype-section → trigger-dropdown

## Semantic event(s) candidate
- `set_prototype_trigger { connection_id, from_type, to_type, params, trigger }`

## Source articles
- `prototype-triggers`
- `connect-your-prototype`
