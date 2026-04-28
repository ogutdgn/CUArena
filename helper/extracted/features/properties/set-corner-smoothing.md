# Set corner smoothing (squircle)

- **Category:** properties
- **One-line summary:** Apply Apple-style "squircle" corner smoothing in addition to corner radius for a softer organic curve.

## Triggers
- Right sidebar Appearance section → corner smoothing slider (visible when corner radius > 0).

## Preconditions
- Layer has a corner radius value > 0.

## Inputs
- Slider 0-100% smoothing factor.

## Behavior
1. 0% = standard rounded corner (circular arc).
2. Higher values = squircle / continuous curvature.

## Outputs
- **Scene graph changes:** `corner_smoothing` field updated (in addition to `corner_radius`).

## UI feedback
- Live canvas redraw.

## Side effects
- Undo stack: per change.

## Related UI schema entries
- `regions/right-properties.md` → appearance-section → corner-smoothing slider

## Semantic event(s) candidate
- `set_corner_smoothing { layer_ids, from, to, trigger }`

## Source articles
- `adjust-corner-radius-and-smoothing`
