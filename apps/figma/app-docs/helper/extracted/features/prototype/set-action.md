# Set prototype action

- **Category:** prototype
- **One-line summary:** Choose what happens when a trigger fires — Navigate to / Change to / Open overlay / Swap overlay / Close overlay / Back / Scroll to / Open link / Set variable / Conditional.

## Triggers
- Connection selected → Prototype panel → Action dropdown.

## Preconditions
- A connection exists.

## Inputs
- Action type from dropdown + action-specific parameters (e.g. destination frame for navigate; URL for open link; variable assignment for set variable).

## Behavior
- Each action describes the destination behavior at runtime.
- **Multiple actions** can be chained on a single trigger (per `multiple-actions-and-conditionals`).
- **Conditionals** add an `if (expression)` gate on actions.

## Outputs
- **Scene graph changes:** connection's `actions` array updated.

## UI feedback
- Action UI in prototype panel.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → prototype-section → actions

## Semantic event(s) candidate
- `set_prototype_action { connection_id, action_index, type, params, trigger }`

## Source articles
- `prototype-actions`
- `multiple-actions-and-conditionals`
- `use-expressions-in-prototypes`
- `state-management-for-prototypes`
