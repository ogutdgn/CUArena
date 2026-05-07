# Manage flows (start points, multiple flows)

- **Category:** prototype
- **One-line summary:** Mark a frame as a flow's starting point so the prototype play knows where to begin; manage multiple flows.

## Triggers
- Frame selected → Prototype panel → **Flow starting point** add button.

## Preconditions
- Frame selected.

## Inputs
- Pointer click; optional flow name.

## Behavior
1. Frame is marked as a starting point and rendered with a play indicator on canvas.
2. Multiple flows can exist in one file (e.g. "Onboarding flow", "Checkout flow").
3. Pressing **Play** opens the prototype starting from the active flow.

## Outputs
- **Scene graph changes:** flow registry updated.

## UI feedback
- Play indicator on canvas; flows list in panel.

## Side effects
- Undo stack: per change.

## Related UI schema entries
- `regions/canvas-overlays.md` → flow-start-indicator
- `regions/right-properties.md` → prototype-section → flows list

## Semantic event(s) candidate
- `add_flow_starting_point { frame_id, flow_id, flow_name? }`
- `remove_flow_starting_point { frame_id }`

## Source articles
- `create-and-manage-prototype-flows`
- `connect-your-prototype`
- `play-your-prototypes`
