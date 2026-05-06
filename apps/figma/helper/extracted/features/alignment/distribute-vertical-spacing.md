# Distribute vertical spacing

- **Category:** alignment
- **One-line summary:** Equalize vertical gaps between selected layers; topmost and bottommost stay anchored.

## Triggers
- Alignment row → "distribute vertical spacing" icon.
- Shortcut: per Figma keyboard sheet.

## Preconditions
- 2+ layers selected (3+ for meaningful distribute).

## Inputs
- Pointer click OR shortcut.

## Behavior
- Mirror of `distribute-horizontal-spacing.md` along Y axis.

## Outputs
- **Scene graph changes:** middle layers' Y positions updated.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `distribute_vertical_spacing { layer_ids, computed_gap, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
