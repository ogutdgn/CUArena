# Distribute horizontal spacing

- **Category:** alignment
- **One-line summary:** Equalize horizontal gaps between selected layers; outermost layers stay anchored.

## Triggers
- Alignment row → "distribute horizontal spacing" icon (visible only with multi-selection).
- Shortcut: per Figma keyboard sheet (covered by `use-figma-products-with-a-keyboard`).

## Preconditions
- 2+ layers selected (3+ for distribute to be meaningful).

## Inputs
- Pointer click OR shortcut.

## Behavior
1. Compute the total horizontal extent (leftmost layer's left edge to rightmost layer's right edge).
2. Subtract the layers' widths.
3. Divide remaining space equally and place layers with that uniform gap.
4. Outermost layers do not move.

## Outputs
- **Scene graph changes:** middle layers' X positions updated.
- **Selection changes:** none.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `distribute_horizontal_spacing { layer_ids, computed_gap, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
