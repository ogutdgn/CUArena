# Nudge with arrow keys

- **Category:** transform
- **One-line summary:** Move selected layers by a small or big nudge using arrow keys.

## Triggers
- Selection non-empty + arrow keys: `←`, `→`, `↑`, `↓`.
- Hold `Shift` + arrow key for big nudge.

## Preconditions
- One or more layers selected.

## Inputs
- Arrow keys, optionally with Shift.

## Behavior
1. **Small nudge** (default = 1 point): one arrow press moves the layer 1 unit on that axis.
2. **Big nudge** (default = 10 points): `Shift` + arrow moves by 10 units.
3. Both values are configurable via Figma preferences (per `set-small-and-big-nudge-values`).
4. Repeated arrow presses move repeatedly; auto-repeat works if held.

## Outputs
- **Scene graph changes:** selected layers' X/Y updated.
- **Selection changes:** none.

## UI feedback
- Position fields update; canvas reflects new position.

## Side effects
- Undo stack: one entry per "nudge burst" (consecutive presses within a short window coalesce); each new direction or pause starts a new entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → X/Y inputs

## Semantic event(s) candidate
- `nudge_layer { layer_ids, direction: "left" | "right" | "up" | "down", magnitude: "small" | "big", count, trigger: "arrow_key" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
- `set-small-and-big-nudge-values`
