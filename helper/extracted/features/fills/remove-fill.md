# Remove fill

- **Category:** fills
- **One-line summary:** Remove a fill row from a layer's fills array.

## Triggers
- Right sidebar **Fill** section, on a fill row → click `-` (minus icon).
- Right sidebar **Fill** section, fill row → click `…` (overflow) → "Remove".

## Preconditions
- Selection non-empty.
- Layer has at least one fill.

## Inputs
- Pointer click.

## Behavior
1. The targeted fill row is deleted from each selected layer's `fills` array.
2. Other fills shift up; layer renders with one fewer fill stacked.

## Outputs
- **Scene graph changes:** layer's `fills` array shrinks by one entry.
- **Selection changes:** none.

## UI feedback
- Fill row disappears from the panel.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per remove.

## Related UI schema entries
- `regions/right-properties.md` → fill-section → fill-row minus + overflow menu

## Semantic event(s) candidate
- `remove_fill { layer_ids: [...], fill_index, removed_fill_snapshot, trigger: "panel_minus" | "panel_menu" }`

## Source articles
- `guide-to-fills`

## Notes / gaps
- When all fills are removed, the layer renders with no fill (transparent for shapes, see-through for frames).
